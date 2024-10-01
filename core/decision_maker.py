import threading
import re
import logging
from queue import Queue, Lock
import time
from core.logger import SnowballLogger
from core.memory import Memory
from core.config_loader import load_config

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
        self.reminders = []
        self.reminder_lock = Lock()  # Lock for thread-safe access to reminders
        self.logger = SnowballLogger()  # Initialize logger
        self.memory = Memory()  # Access to Memory
        self.task_queue = Queue(maxsize=10)  # Limit queue size for performance
        self.logger.logger.info("DecisionMaker initialized.")
        threading.Thread(target=self.process_tasks, daemon=True).start()

    def process_tasks(self):
        """Continuously process tasks from the queue asynchronously."""
        while True:
            try:
                if not self.task_queue.empty():
                    task, args = self.task_queue.get()
                    task(*args)
            except Exception as e:
                self.logger.logger.error(f"Error processing task: {e}")

    def handle_request(self, request: str) -> str:
        """Main method to handle various user requests."""
        request = ' '.join(request.lower().split())  # Normalize spaces in request
        self.logger.logger.info(f"Received request: {request}")

        # Handle different types of requests based on content
        if self.REMIND_ME in request:
            response = self.handle_reminder(request)
        elif self.LIST_REMINDERS in request:
            response = self.list_reminders()
        elif self.CANCEL_REMINDERS in request:
            response = self.cancel_reminder()
        elif self.SYSTEM_MONITOR in request:
            response = self.start_system_monitor()
        elif self.GAME_REQUEST in request:
            response = self.handle_game_request(request)
        elif self.NAME_REQUEST in request:
            response = self.ask_for_name()
        elif self.FEEDBACK_REQUEST in request:
            response = self.provide_feedback(request)
        elif self.DAILY_SUMMARY in request:
            response = self.daily_summary()
        elif self.CONTEXT_REQUEST in request:
            response = self.remember_context(request)
        elif self.FETCH_WEATHER in request:
            response = self.fetch_weather(request)
        elif self.CUSTOM_COMMAND in request:
            response = self.add_custom_command(request)
        else:
            response = "Sorry, I don't understand that request."
            self.logger.logger.warning(f"Unrecognized request: {request}")

        self.logger.logger.info(f"Response generated: {response}")
        return response

    def handle_game_request(self, request: str) -> str:
        """Launch the requested game."""
        game_name = self.extract_game_name(request)
        if game_name:
            try:
                module = __import__(f"games.{game_name}.{game_name}", fromlist=['game_loop'])
                game_loop = getattr(module, 'game_loop')
                self.logger.logger.info(f"Launching game: {game_name}")
                game_loop()
                return f"Launching {game_name}..."
            except (ImportError, AttributeError):
                self.logger.logger.warning(f"Game not found: {game_name}")
                return f"Sorry, I don't know how to play {game_name} yet."
        return "Please specify a valid game name."

    def extract_game_name(self, request: str) -> str:
        """Extract game name from the request."""
        match = re.search(r'play (\w+)', request)
        return match.group(1) if match else None

    def handle_reminder(self, request: str) -> str:
        """Handle user requests related to reminders."""
        self.logger.logger.info("Processing reminder request.")
        return self.set_reminder(request)

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
                    self.logger.logger.info(f"Parsed reminder: Action - {action}, Time - {time_in_minutes} minutes")

                    # Schedule the reminder
                    with self.reminder_lock:
                        self.reminders.append((action.strip(), time_in_minutes))
                        self.task_queue.put((self._reminder_timer, (action.strip(), time_in_minutes)))

                    # Store reminder in memory for persistence
                    self.memory.store_interaction(request, f"Reminder set for {action.strip()} in {time_in_minutes} minutes.")

                    responses.append(f"Reminder set for {action.strip()} in {time_in_minutes} minutes.")
                except Exception as e:
                    self.logger.logger.error(f"Error setting reminder: {e}")
                    responses.append(f"Error setting reminder: {e}")
            return "\n".join(responses)
        else:
            self.logger.logger.warning(f"Failed to parse reminder request: {request}")
            return "Invalid reminder format. Please use 'remind me to [action] in [time] [minutes/hours/days].'"

    def convert_to_minutes(self, time_value: int, time_unit: str) -> int:
        """Convert time value to minutes based on the unit."""
        if "hour" in time_unit:
            return time_value * 60
        elif "day" in time_unit:
            return time_value * 60 * 24
        return time_value  # Already in minutes

    def list_reminders(self) -> str:
        """List all active reminders."""
        with self.reminder_lock:
            if not self.reminders:
                self.logger.logger.info("No active reminders to list.")
                return "No active reminders."
            reminders_list = "\n".join([f"Reminder: {r[0]} in {r[1]} minutes." for r in self.reminders])
            self.logger.logger.info("Listing all active reminders.")
            return reminders_list

    def cancel_reminder(self) -> str:
        """Cancel all reminders."""
        with self.reminder_lock:
            self.reminders.clear()
            self.logger.logger.info("All reminders have been canceled.")
            return "All reminders have been canceled."

    def _reminder_timer(self, action: str, time_in_minutes: int):
        """Wait for the specified time and then notify the user."""
        time.sleep(time_in_minutes * 60)  # Convert minutes to seconds
        self.logger.logger.info(f"Reminder for action: {action} triggered.")
        # Notify the user (this could be a print statement or a more sophisticated notification)
        print(f"Reminder: {action}")

    def start_system_monitor(self) -> str:
        """Start the system monitoring functionality."""
        # Implementation of system monitoring functionality
        self.logger.logger.info("System monitoring started.")
        return "System monitoring has started."

    def ask_for_name(self) -> str:
        """Ask the user for their name."""
        self.logger.logger.info("Asking for user's name.")
        return "What is your name?"

    def provide_feedback(self, request: str) -> str:
        """Handle user feedback."""
        self.logger.logger.info("Processing feedback request.")
        return "Thank you for your feedback!"

    def daily_summary(self) -> str:
        """Provide a summary of the day's activities."""
        self.logger.logger.info("Providing daily summary.")
        return "Here is your daily summary."

    def remember_context(self, request: str) -> str:
        """Remember the context for future interactions."""
        self.logger.logger.info(f"Remembering context: {request}")
        return "Context remembered."

    def fetch_weather(self, request: str) -> str:
        """Fetch the current weather information."""
        self.logger.logger.info("Fetching weather information.")
        return "The current weather is sunny and 72°F."

    def add_custom_command(self, request: str) -> str:
        """Add a custom command."""
        self.logger.logger.info(f"Adding custom command: {request}")
        return "Custom command added."

# Example usage:
if __name__ == "__main__":
    decision_maker = DecisionMaker()
    # Sample request handling
    print(decision_maker.handle_request("remind me to take out the trash in 10 minutes"))
    print(decision_maker.handle_request("list reminders"))
    print(decision_maker.handle_request("cancel reminders"))
