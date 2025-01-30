from plyer import notification
import logging
import os
import threading
import datetime
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue
from email.mime.text import MIMEText
import smtplib
from typing import Optional

# Define log paths
DEFAULT_LOG_DIR = os.path.join('S:/Snowball/storage/logs')
LOG_PATHS = {
    "config": os.path.join(DEFAULT_LOG_DIR, "config_logs", "config_log.txt"),
    "decision": os.path.join(DEFAULT_LOG_DIR, "decision_logs", "decision_log.txt"),
    "error": os.path.join(DEFAULT_LOG_DIR, "error_logs", "error_log.txt"),
    "event": os.path.join(DEFAULT_LOG_DIR, "event_logs", "event_log.txt"),
    "file": os.path.join(DEFAULT_LOG_DIR, "file_logs", "file_log.txt"),
    "interaction": os.path.join(DEFAULT_LOG_DIR, "interaction_logs", "interaction_log.txt"),
    "memory": os.path.join(DEFAULT_LOG_DIR, "memory_logs", "memory_log.txt"),
    "security": os.path.join(DEFAULT_LOG_DIR, "security_logs", "security_log.txt"),
    "system_health": os.path.join(DEFAULT_LOG_DIR, "system_health_logs", "system_health_log.txt"),
    "task": os.path.join(DEFAULT_LOG_DIR, "task_logs", "task_log.txt"),
    "warning": os.path.join(DEFAULT_LOG_DIR, "warning_logs", "warning_log.txt"),
}

# Create log directories
for log_path in LOG_PATHS.values():
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Thread lock for safe file handling
file_lock = threading.Lock()

class SafeRotatingFileHandler(RotatingFileHandler):
    """Thread-safe RotatingFileHandler."""
    def doRollover(self):
        with file_lock:
            super().doRollover()

class SnowballLogger:
    def __init__(self, settings: Optional[dict] = None):
        self.loggers = {}
        self.queue = Queue()
        self.listener = self._setup_listener()
        self._setup_loggers()

    def _setup_listener(self):
        handlers = []
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        for log_path in LOG_PATHS.values():
            handler = SafeRotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=5)
            handler.setFormatter(formatter)
            handlers.append(handler)

        listener = QueueListener(self.queue, *handlers)
        listener.start()
        return listener

    def _setup_loggers(self):
        for log_type in LOG_PATHS.keys():
            logger = logging.getLogger(log_type)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(QueueHandler(self.queue))
            logger.propagate = False
            self.loggers[log_type] = logger

    def log_config(self, message):
        """Log configuration changes."""
        self.loggers["config"].info(message)

    def log_decision(self, decision_details):
        """Log details about decisions made by the decision_maker."""
        self.loggers["decision"].info(decision_details)

    def log_error(self, message):
        """Log errors from any module."""
        self.loggers["error"].error(message)

    def log_event(self, message):
        """Log significant system or user events."""
        self.loggers["event"].info(message)

    def log_file(self, action, file_path):
        """Log file-related operations."""
        self.loggers["file"].info(f"Action: {action} | File: {file_path}")

    def log_interaction(self, user_message, ai_response):
        """Log user input and AI response."""
        self.loggers["interaction"].info(f"User: {user_message} | AI: {ai_response}")

    def log_memory(self, action, details):
        """Log memory database changes."""
        self.loggers["memory"].info(f"Action: {action} | Details: {details}")

    def log_security(self, message):
        """Log security-related events."""
        self.loggers["security"].warning(message)

    def log_system_health(self, metrics):
        """Log system health metrics (future use)."""
        self.loggers["system_health"].info(metrics)

    def log_task(self, task_name, status):
        """Log tasks and their outcomes."""
        self.loggers["task"].info(f"Task: '{task_name}' - Status: '{status}'")

    def log_warning(self, message):
        """Log warnings from any module."""
        self.loggers["warning"].warning(message)

    def shutdown(self):
        """Shut down the logging system cleanly."""
        self.listener.stop()
        for logger in self.loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

if __name__ == "__main__":
    # Example usage of the logger
    logger = SnowballLogger()

    # Log various events
    logger.log_config("Updated AI settings.")
    logger.log_decision("Decision: Selected GPT-4 response for user query.")
    logger.log_error("Failed to load configuration file.")
    logger.log_event("Snowball AI initialized.")
    logger.log_file("Created", "S:/Snowball/data/example.txt")
    logger.log_interaction("Hello, Snowball!", "Hello, how can I assist you?")
    logger.log_memory("Inserted", "New interaction added to database.")
    logger.log_security("Unauthorized access attempt detected.")
    logger.log_task("Analyze file", "Completed successfully.")
    logger.log_warning("High memory usage detected.")

    # Shut down logging
    logger.shutdown()