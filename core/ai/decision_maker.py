import threading
import re
import logging
from queue import Queue, Empty
import time
import requests
from datetime import datetime
from core.initializer import SnowballInitializer

class DecisionMaker:
    """Class to handle user requests and make decisions based on input."""

    REMIND_ME = "remind me"
    LIST_REMINDERS = "list reminders"
    CANCEL_REMINDERS = "cancel reminders"
    SYSTEM_MONITOR = "system"
    GAME_REQUEST = "game"
    NAME_REQUEST = "name"
    FEEDBACK_REQUEST = "feedback"
    DAILY_SUMMARY = "daily summary"
    CONTEXT_REQUEST = "remember context"
    FETCH_WEATHER = "weather"
    CUSTOM_COMMAND = "custom command"

    def __init__(self):
        initializer = SnowballInitializer()
        self.logger = initializer.logger
        self.memory = initializer.memory
        self.sentiment_analysis = initializer.sentiment_analysis
        self.vision = initializer.vision

        self.reminders = []
        self.reminder_lock = threading.Lock()  # Lock for thread-safe access to reminders
        self.task_queue = Queue(maxsize=10)  # Limit queue size for performance
        self.logger.log_event("DecisionMaker initialized.")
        self._stop_event = threading.Event()  # Event for stopping the thread gracefully
        threading.Thread(target=self.process_tasks, daemon=True).start()

    def stop(self):
        """Stop the decision maker processing thread."""
        self._stop_event.set()
        self.logger.log_event("Stopping DecisionMaker.")

    def process_tasks(self):
        """Continuously process tasks from the queue asynchronously."""
        while not self._stop_event.is_set():
            try:
                task, args = self.task_queue.get(timeout=1)  # Timeout to check stop event
                self.logger.log_task(f"Processing task: {task.__name__}", status="Started")
                task(*args)
                self.logger.log_task(f"Processing task: {task.__name__}", status="Completed")
            except Empty:
                continue  # No tasks to process, continue looping
            except Exception as e:
                self.logger.log_error(f"Error processing task: {e}")

    def handle_request(self, request: str) -> str:
        """Main method to handle various user requests."""
        request = ' '.join(request.lower().split())  # Normalize spaces in request
        sentiment = self.sentiment_analysis.analyze(request)
        facial_emotion = self.vision.get_current_emotion()  # Assume method returns current facial emotion

        # Log the interaction along with sentiment and emotion details
        self.logger.log_interaction(f"Received request: {request}", ai_response="Processing...", sentiment=sentiment, facial_emotion=facial_emotion)

        try:
            # Use sentiment and emotion data to adjust response style
            response_style = self.determine_response_style(sentiment, facial_emotion)

            if "remind me" in request:
                response = self.handle_reminder(request, response_style)
            elif "list reminders" in request:
                response = self.list_reminders(response_style)
            elif "cancel reminders" in request:
                response = self.cancel_reminder(response_style)
            elif "play game" in request:
                response = self.handle_game_request(request, response_style)
            else:
                response = "Sorry, I don't understand that request."
                self.logger.log_warning(f"Unrecognized request: {request}")

        except Exception as e:
            response = "An error occurred while processing your request."
            self.logger.log_error(f"Error in handle_request: {e}")

        self.logger.log_interaction(request, ai_response=response)
        return response

    def handle_game_request(self, request: str) -> str:
        """Launch the requested game."""
        game_name = self.extract_game_name(request)
        if game_name:
            try:
                module = __import__(f"games.{game_name}.{game_name}", fromlist=['game_loop'])
                game_loop = getattr(module, 'game_loop')
                self.logger.log_event(f"Launching game: {game_name}")
                threading.Thread(target=game_loop, daemon=True).start()  # Run game in separate thread
                return f"Launching {game_name}..."
            except (ImportError, AttributeError) as e:
                self.logger.log_warning(f"Game not found: {game_name}, Error: {e}")
                return f"Sorry, I don't know how to play {game_name} yet."
        return "Please specify a valid game name."

    def extract_game_name(self, request: str) -> str:
        """Extract game name from the request."""
        match = re.search(r'play (\w+)', request)
        return match.group(1) if match else None

    def determine_response_style(self, sentiment: str, facial_emotion: str) -> str:
        """Determine the response style based on sentiment and facial emotion."""
        if sentiment == 'negative' or facial_emotion in ['sad', 'angry']:
            return 'empathetic'
        elif sentiment == 'positive' or facial_emotion == 'happy':
            return 'encouraging'
        else:
            return 'neutral'

    def handle_reminder(self, request: str, response_style: str) -> str:
        """Handle user requests related to reminders, adjusted for response style."""
        reminder_response = self.set_reminder(request)
        if response_style == 'empathetic':
            return f"I've set the reminder for you. If there's anything else I can help with, I'm here for you."
        elif response_style == 'encouraging':
            return f"Got it! Reminder set. You're doing great—keep it up!"
        else:
            return reminder_response

    def set_reminder(self, request: str) -> str:
        """Set a new reminder based on natural language input."""
        pattern = r"remind me to\s+(.+?)\s+in\s+(\d+)\s*(minute[s]?|hour[s]?|day[s]?)"
        matches = re.findall(pattern, request)

        if matches:
            responses = []
            for match in matches:
                try:
                    action = match[0]
                    time_value = int(match[1])
                    time_unit = match[2]

                    # Convert to minutes for internal consistency
                    time_in_minutes = self.convert_to_minutes(time_value, time_unit)

                    # Log parsed values
                    self.logger.log_event(f"Parsed reminder: Action - {action}, Time - {time_in_minutes} minutes")

                    # Schedule the reminder
                    with self.reminder_lock:
                        self.reminders.append((action.strip(), time_in_minutes))
                        self.task_queue.put((self._reminder_timer, (action.strip(), time_in_minutes)))

                    # Store reminder in memory for persistence
                    self.memory.store_interaction(request, f"Reminder set for {action.strip()} in {time_in_minutes} minutes.")

                    responses.append(f"Reminder set for {action.strip()} in {time_in_minutes} minutes.")
                except Exception as e:
                    self.logger.log_error(f"Error setting reminder: {e}")
                    responses.append(f"Error setting reminder: {e}")
            return "\n".join(responses)
        else:
            self.logger.log_warning(f"Failed to parse reminder request: {request}")
            return "Invalid reminder format. Please use 'remind me to [action] in [time] [minutes/hours/days].'"

    def convert_to_minutes(self, time_value: int, time_unit: str) -> int:
        """Convert time value to minutes based on the unit."""
        conversion_factors = {'minute': 1, 'hour': 60, 'day': 1440}
        for unit, factor in conversion_factors.items():
            if unit in time_unit:
                return time_value * factor
        return time_value  # Default to minutes if no match

    def list_reminders(self, response_style: str) -> str:
        """List all active reminders, with a response style adjustment."""
        with self.reminder_lock:
            if not self.reminders:
                self.logger.log_event("No active reminders to list.")
                return "No active reminders."

            reminders_list = "\n".join([f"Reminder: {r[0]} in {r[1]} minutes." for r in self.reminders])
            self.logger.log_event("Listing all active reminders.")

            if response_style == 'empathetic':
                return f"Here are your reminders. Let me know if there's anything else I can do for you:\n{reminders_list}"
            elif response_style == 'encouraging':
                return f"Here's what you've got planned. You're on top of things!\n{reminders_list}"
            else:
                return reminders_list

    def cancel_reminder(self) -> str:
        """Cancel all reminders."""
        with self.reminder_lock:
            self.reminders.clear()
            self.logger.log_event("All reminders have been canceled.")
            return "All reminders have been canceled."

    def _reminder_timer(self, action: str, time_in_minutes: int):
        """Wait for the specified time and then notify the user."""
        try:
            time.sleep(time_in_minutes * 60)  # Convert minutes to seconds
            self.logger.log_event(f"Reminder for action: {action} triggered.")
            print(f"Reminder: {action}")  # Notify user, replace with more complex notification as needed
        except Exception as e:
            self.logger.log_error(f"Error in reminder timer: {e}")

    def start_system_monitor(self) -> str:
        """Start the system monitoring functionality."""
        self.logger.log_event("System monitoring started.")
        # Placeholder implementation for system monitoring
        return "System monitoring has started."

    def ask_for_name(self) -> str:
        """Ask the user for their name."""
        self.logger.log_event("Asking for user's name.")
        return "What is your name?"

    def provide_feedback(self, request: str) -> str:
        """Handle user feedback."""
        self.logger.log_event("Processing feedback request.")
        return "Thank you for your feedback!"

    def daily_summary(self) -> str:
        """Provide a summary of the day's activities."""
        self.logger.log_event("Providing daily summary.")
        # Placeholder for daily summary logic
        return "Here is your daily summary."

    def remember_context(self, request: str) -> str:
        """Remember the context for future interactions."""
        self.logger.log_event(f"Remembering context: {request}")
        # Save context in memory for future interactions
        self.memory.store_interaction("context", request)
        return "Context remembered."


    def fetch_weather(self, request: str) -> str:
        """Fetch the current weather information, using memory for preferred locations."""
        # If the user has previously asked for a specific city, remember it
        preferred_city = self.memory.retrieve_recent("preferred_city")
        city = "New York"  # Default city

        if "in" in request:
            # Extract city name from the request
            match = re.search(r'weather in (\w+)', request)
            if match:
                city = match.group(1)
                self.memory.store_interaction("preferred_city", city)  # Store the city as a preferred location

        elif preferred_city:
            city = preferred_city

        self.logger.log_event(f"Fetching weather information for {city}.")
        try:
            # Example weather API request (Replace API_KEY and URL with actual service)
            api_key = "YOUR_WEATHER_API_KEY"
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                weather_info = weather_data['current']['condition']['text']
                temperature = weather_data['current']['temp_f']
                return f"The current weather in {city} is {weather_info} with a temperature of {temperature}°F."
            else:
                return f"Failed to fetch weather information for {city}."
        except Exception as e:
            self.logger.log_error(f"Error fetching weather information: {e}")
            return "Sorry, I couldn't fetch the weather information."
        
    def add_custom_command(self, request: str) -> str:
        """Add a custom command."""
        self.logger.log_event("Adding custom command.")
        # Placeholder for custom command logic
        return "Custom command added."

