import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import json
import logging
from plyer import notification  # For push notifications
from core.config_loader import ConfigLoader  # Importing the ConfigLoader class

# Define the scope for Google OAuth
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load mobile sync settings using ConfigLoader
settings = ConfigLoader.load_config('S:/Snowball/config/settings.json')
mobile_sync_interval = settings.get('mobile_sync_interval', 10)  # Default to 10 minutes

# Load sync and backup settings using ConfigLoader
backup_settings = ConfigLoader.load_config('S:/Snowball/config/sync_and_backup.json')
cloud_backup_enabled = backup_settings.get('backup_to_cloud', False)
nas_backup_enabled = backup_settings.get('backup_to_nas', False)


class MobileIntegration:
    def __init__(self):
        self.credentials = self.initialize_google_credentials()
        self.facebook_access_token = self.load_facebook_token()
        self.google_maps_api_key = self.load_google_maps_key()
        self.facebook_api_url = "https://graph.facebook.com/v15.0/me/messages"
        self.gps_data_file = os.environ.get('GPS_DATA_FILE', 'S:/Snowball/cloud_sync/mobile_sync/gps_data.json')
        self.notification_service = self.initialize_notification_service()

    def initialize_google_credentials(self):
        """Initialize Google OAuth credentials or prompt for authentication if needed."""
        creds = None
        token_path = 'S:/Snowball/config/token.json'
        credentials_path = 'S:/Snowball/config/credentials.json'

        # Load token from file if it exists
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If there are no valid credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Try to refresh the token if it's expired
                try:
                    creds.refresh(Request())
                    logging.info("Token refreshed successfully.")
                except Exception as e:
                    logging.error(f"Error refreshing token: {e}")
                    return None
            else:
                # If no valid token exists, start the OAuth flow to generate a new token
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

                # Save the new credentials to token.json
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                    logging.info(f"New token saved to {token_path}")

        return creds
    
    def load_facebook_token(self):
        """Load Facebook API access token from a JSON file."""
        try:
            with open("config/facebook_token.json", 'r') as file:
                data = json.load(file)
                return data.get("facebook_access_token")
        except FileNotFoundError:
            logging.error("Facebook API token not found.")
            return None

    def load_google_maps_key(self):
        """Load Google Maps API key from a JSON file."""
        try:
            with open("config/google_maps_key.json", 'r') as file:
                data = json.load(file)
                return data.get("google_maps_api_key")
        except FileNotFoundError:
            logging.error("Google Maps API key not found.")
            return None

    def get_facebook_message_history(self):
        """Fetch Facebook message history using the Graph API."""
        if self.facebook_access_token:
            try:
                params = {'access_token': self.facebook_access_token, 'limit': 100}
                response = requests.get(self.facebook_api_url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching Facebook messages: {e}")
        else:
            logging.warning("Facebook token not available.")
        return None
    
    def update_gps_data_file(self, location_data):
        """Update the GPS data file with new location information."""
        if location_data:
            new_entry = {
                "latitude": location_data.get('geometry', {}).get('location', {}).get('lat'),
                "longitude": location_data.get('geometry', {}).get('location', {}).get('lng'),
                "timestamp": location_data.get('timestamp', 'N/A'),
                "location_name": location_data.get('name', 'Unknown Location')
            }

            try:
                with open(self.gps_data_file, 'r+') as file:
                    try:
                        gps_data = json.load(file)
                    except json.JSONDecodeError:
                        gps_data = {"locations": []}  # Reset on invalid JSON

                    gps_data["locations"].append(new_entry)
                    file.seek(0)  # Move to the beginning of the file before writing
                    json.dump(gps_data, file, indent=4)
                    file.truncate()  # Remove remaining part if new data is shorter
                    logging.info(f"GPS Data Updated: {new_entry}")
            except IOError as e:
                logging.error(f"Error updating GPS data file: {e}")

    def check_travel_patterns(self):
        """Check your location and remind you of tasks."""
        if self.google_maps_api_key:
            location_data = self.get_current_location()
            if location_data and "grocery store" in location_data.get("name", "").lower():
                self.send_alert("You're near a grocery store. Don't forget the milk!")
        else:
            logging.warning("Google Maps API key not available.")

    def get_current_location(self):
        """Fetch current location using Google Maps API."""
        lat, lon = self.get_device_coordinates()  # Implement this method to get dynamic coordinates
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f'{lat},{lon}',
            'radius': 500,
            'key': self.google_maps_api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            places = response.json().get("results", [])
            return places[0] if places else None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching current location: {e}")
            return None

    def initialize_notification_service(self):
        """Initialize push notification service (like Firebase)."""
        # Firebase setup code would go here if needed
        pass

    def send_push_notification(self, title, message):
        """Send a push notification to the mobile device."""
        notification.notify(
            title=title,
            message=message,
            timeout=5  # Notification timeout in seconds
        )

    def listen_for_requests(self):
        """Listen for mobile commands."""
        return "Check my schedule"

    def respond(self, response):
        """Respond to mobile requests."""
        logging.info(f"Responding to mobile request with: {response}")

    def send_alert(self, message):
        """Send alerts via push notification."""
        self.send_push_notification("Snowball AI Alert", message)


# If running standalone
if __name__ == "__main__":
    mobile_integration = MobileIntegration()
    mobile_integration.check_travel_patterns()
