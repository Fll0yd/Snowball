# mobile_integration.py (S:/Snowball/core) 
 
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import json
import logging
from plyer import notification  # For push notifications

# Define the scope for Google OAuth
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']

# Load mobile sync settings using ConfigLoader
settings = ConfigLoader.load_config('interface_settings.json')
backup_settings = ConfigLoader.load_config('mobile_settings.json')
cloud_backup_enabled = backup_settings.get('backup_to_cloud', False)
nas_backup_enabled = backup_settings.get('backup_to_nas', False)
mobile_sync_interval = settings.get('mobile_sync_interval', 10)  # Default to 10 minutes

class MobileIntegration:
    def __init__(self):
        self.logger = SnowballLogger()
        self.credentials = self.initialize_google_credentials()
        self.facebook_access_token = self.load_facebook_token()
        self.google_maps_api_key = self.load_google_maps_key()
        self.facebook_api_url = "https://graph.facebook.com/v15.0/me/messages"
        self.gps_data_file = os.environ.get('GPS_DATA_FILE', 'S:/Snowball/cloud_sync/mobile_sync/gps_data.json')
        self.notification_service = self.initialize_notification_service()

    def initialize_google_credentials(self):
        """Initialize Google OAuth credentials or prompt for authentication if needed."""
        creds = None
        token_path = 'S:/Snowball/config/account_integrations.json'

        # Load token from file if it exists
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as token_file:
                    data = json.load(token_file)
                    google_token_data = data.get("tokens", {}).get("google", {})

                    if not all(key in google_token_data for key in ["client_id", "client_secret", "refresh_token"]):
                        self.logger.log_warning("Google credentials are missing required fields.")
                        return None

                    creds = Credentials.from_authorized_user_info(google_token_data, SCOPES)
            except json.JSONDecodeError:
                self.logger.log_error("Google token file is empty or improperly formatted.")
                return None

        # If there are no valid credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.log_event("Google token refreshed successfully.")
                except Exception as e:
                    self.logger.log_error(f"Error refreshing Google token: {e}")
                    return None
            else:
                # If no valid token exists, start the OAuth flow to generate a new token
                credentials_path = 'S:/Snowball/config/account_integrations.json'
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

                # Save the new credentials to the JSON file
                try:
                    with open(token_path, 'r+') as token_file:
                        data = json.load(token_file)
                        data['tokens']['google'] = json.loads(creds.to_json())
                        token_file.seek(0)
                        json.dump(data, token_file, indent=4)
                        token_file.truncate()
                        self.logger.log_event(f"New Google token saved to {token_path}")
                except Exception as e:
                    self.logger.log_error(f"Error saving Google token: {e}")

        return creds

    def load_facebook_token(self):
        """Load Facebook API access token from a JSON file."""
        try:
            with open("S:/Snowball/config/account_integrations.json", 'r') as file:  # Use absolute path
                data = json.load(file)
                token = data.get("tokens", {}).get("facebook", {}).get("access_token")
                if token:
                    self.logger.log_event("Facebook token loaded successfully.")
                return token
        except FileNotFoundError:
            self.logger.log_warning("Facebook API token file not found.")
        except json.JSONDecodeError as e:
            self.logger.log_error(f"Error parsing Facebook token file: {e}")
        return None

    def load_google_maps_key(self):
        """Load Google Maps API key from a JSON file."""
        try:
            with open("S:/Snowball/config/account_integrations.json", 'r') as file:  # Use absolute path
                data = json.load(file)
                key = data.get("integrations", {}).get("google_maps", {}).get("api_key")
                if key:
                    self.logger.log_event("Google Maps API key loaded successfully.")
                return key
        except FileNotFoundError:
            self.logger.log_warning("Google Maps API key file not found.")
        except json.JSONDecodeError as e:
            self.logger.log_error(f"Error parsing Google Maps API key file: {e}")
        return None

    def get_facebook_message_history(self):
        """Fetch Facebook message history using the Graph API."""
        if self.facebook_access_token:
            try:
                params = {'access_token': self.facebook_access_token, 'limit': 100}
                response = requests.get(self.facebook_api_url, params=params)
                response.raise_for_status()
                self.logger.log_event("Successfully fetched Facebook message history.")
                return response.json()
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"Error fetching Facebook messages: {e}")
        else:
            self.logger.log_warning("Facebook token not available.")
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
                        self.logger.log_warning("GPS data file had invalid JSON. Resetting.")

                    gps_data["locations"].append(new_entry)
                    file.seek(0)  # Move to the beginning of the file before writing
                    json.dump(gps_data, file, indent=4)
                    file.truncate()  # Remove remaining part if new data is shorter
                    self.logger.log_event(f"GPS Data Updated: {new_entry}")
            except IOError as e:
                self.logger.log_error(f"Error updating GPS data file: {e}")

    def check_travel_patterns(self):
        """Check your location and remind you of tasks."""
        if self.google_maps_api_key:
            location_data = self.get_current_location()
            if location_data and "grocery store" in location_data.get("name", "").lower():
                self.send_alert("You're near a grocery store. Don't forget the milk!")
                self.logger.log_event("User reminded of grocery shopping near location.")
        else:
            self.logger.log_warning("Google Maps API key not available.")

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
            self.logger.log_event("Successfully fetched current location from Google Maps API.")
            return places[0] if places else None
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error fetching current location: {e}")
            return None

    def initialize_notification_service(self):
        """Initialize push notification service (like Firebase)."""
        # Firebase setup code would go here if needed
        pass

    def send_push_notification(self, title, message):
        """Send a push notification to the mobile device."""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5  # Notification timeout in seconds
            )
            self.logger.log_event(f"Push notification sent: {title} - {message}")
        except Exception as e:
            self.logger.log_error(f"Error sending push notification: {e}")

    def listen_for_requests(self):
        """Listen for mobile commands."""
        command = "Check my schedule"
        self.logger.log_event(f"Listening for mobile requests, received: {command}")
        return command

    def respond(self, response):
        """Respond to mobile requests."""
        self.logger.log_event(f"Responding to mobile request with: {response}")
        logging.info(f"Responding to mobile request with: {response}")

    def send_alert(self, message):
        """Send alerts via push notification."""
        self.send_push_notification("Snowball AI Alert", message)
        self.logger.log_event(f"Alert sent to user: {message}")

# If running standalone
if __name__ == "__main__":
    mobile_integration = MobileIntegration()
    mobile_integration.check_travel_patterns()