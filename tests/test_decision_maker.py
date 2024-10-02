import time
import threading
import re
import sys
import logging
from logging.handlers import RotatingFileHandler
from queue import Queue

sys.path.append('S:/')
from core.logger import SnowballLogger
from core.memory import Memory


class DecisionMaker:
    def __init__(self):
        self.reminders = []
        self.logger = SnowballLogger()  # Initialize logger
        self.memory = Memory()  # Access to Memory
        self.task_queue = Queue()  # Task queue for asynchronous processing
        self.logger.logger.info("DecisionMaker initialized.")
        threading.Thread(target=self.process_tasks, daemon=True).start()

    def process_tasks(self):
        """Continuously process tasks from the queue asynchronously."""
        while True:
            if not self.task_queue.empty():
                task, args = self.task_queue.get()
                task(*args)
            time.sleep(1)  # Prevent CPU overuse

    def handle_request(self, request):
        """Main method to handle various user requests."""
        request = ' '.join(request.lower().split())  # Normalize spaces in request
        self.logger.logger.info(f"Received request: {request}")

        # Handle different types of requests based on content
        if "remind me" in request:
            response = self.handle_reminder(request)
        elif "list reminders" in request:
            response = self.list_reminders()
        elif "cancel reminders" in request:
            response = self.cancel_reminder()
        elif "system" in request or "monitor" in request:
            response = self.start_system_monitor()
        elif "game" in request:
            response = self.handle_game_request(request)
        elif "name" in request:
            response = self.ask_for_name()
        else:
            response = "Sorry, I don't understand that request."
            self.logger.logger.warning(f"Unrecognized request: {request}")
        
        self.logger.logger.info(f"Response generated: {response}")
        return response

    def handle_game_request(self, request):
        """Launch the requested game."""
        game_name = request.split()[-2]  # Expect game name before 'game' keyword
        if game_name == "snake":
            from games.snake.snake import game_loop
            self.logger.logger.info(f"Launching game: {game_name}")
            game_loop()
            return f"Launching {game_name}..."
        else:
            self.logger.logger.warning(f"Game not found: {game_name}")
            return f"Sorry, I don't know how to play {game_name} yet."

    def handle_reminder(self, request):
        """Handle user requests related to reminders."""
        if "remind me" in request:
            self.logger.logger.info("Processing 'set reminder' request.")
            return self.set_reminder(request)
        else:
            self.logger.logger.warning(f"Invalid reminder request: {request}")
            return "I can set, list, or cancel reminders."

    def set_reminder(self, request):
        """Set a new reminder based on natural language input."""
        # Extended regex to handle different times (minutes, hours, days)
        pattern = r"remind me to\s+(.+?)\s+in\s+(\d+)\s*(minute[s]?|hour[s]?|day[s]?)"
        match = re.search(pattern, request)

        if match:
            try:
                action = match.group(1)
                time_value = int(match.group(2))
                time_unit = match.group(3)

                # Convert to minutes for internal consistency
                if "hour" in time_unit:
                    time_in_minutes = time_value * 60
                elif "day" in time_unit:
                    time_in_minutes = time_value * 60 * 24
                else:
                    time_in_minutes = time_value  # Already in minutes

                # Log parsed values
                self.logger.logger.info(f"Parsed reminder: Action - {action}, Time - {time_in_minutes} minutes")

                # Schedule the reminder
                self.reminders.append((action.strip(), time_in_minutes))
                self.task_queue.put((self._reminder_timer, (action.strip(), time_in_minutes)))
                
                # Store reminder in memory for persistence
                self.memory.store_interaction(request, f"Reminder set for {action.strip()} in {time_in_minutes} minutes.")

                return f"Reminder set for {action.strip()} in {time_in_minutes} minutes."
            except Exception as e:
                self.logger.logger.error(f"Error setting reminder: {e}")
                return f"Error setting reminder: {e}"
        else:
            self.logger.logger.warning(f"Failed to parse reminder request: {request}")
            return "Invalid reminder format. Please use 'remind me to [action] in [time] [minutes/hours/days].'"

    def list_reminders(self):
        """List all active reminders."""
        if not self.reminders:
            self.logger.logger.info("No active reminders to list.")
            return "No active reminders."
        reminders_list = "\n".join([f"Reminder: {r[0]} in {r[1]} minutes." for r in self.reminders])
        self.logger.logger.info("Listing all active reminders.")
        return reminders_list

    def cancel_reminder(self):
        """Cancel all reminders."""
        self.logger.logger.info("Cancelling all reminders.")
        self.reminders.clear()
        return "All reminders cancelled."

    def _reminder_timer(self, action, time_in_minutes):
        """Internal method to handle reminder timing."""
        time.sleep(time_in_minutes * 60)
        self.logger.logger.info(f"Reminder triggered: {action}")
        print(f"Reminder: {action}")

    def start_system_monitor(self):
        """Simulate starting the system monitor."""
        self.logger.logger.info("Starting system monitor.")
        return "Starting system monitor..."

    def ask_for_name(self):
        """Ask user if they want to keep or change the AI's name."""
        self.logger.logger.info("Asking for name preference.")
        return "Would you like me to keep the name Snowball or choose a new one?"

    def answer_question(self, question):
        """Provide an answer to a general question."""
        self.logger.logger.info(f"Answering question: {question}")
        return f"Answering the question: {question}"


if __name__ == "__main__":
    # Example usage
    decision_maker = DecisionMaker()
    print(decision_maker.handle_request("remind me to take a break in 10 minutes"))
    print(decision_maker.handle_request("start snake game"))
