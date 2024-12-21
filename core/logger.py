import logging
import os
import threading
from logging.handlers import RotatingFileHandler
from plyer import notification

# Define log paths
DEFAULT_LOG_DIR = os.path.join('S:/Snowball/storage/logs')
LOG_PATHS = {
    "interaction": os.path.join(DEFAULT_LOG_DIR, "interaction_logs", "interaction_log.txt"),
    "error": os.path.join(DEFAULT_LOG_DIR, "error_logs", "error_log.txt"),
    "system_health": os.path.join(DEFAULT_LOG_DIR, "system_health_logs", "system_health_log.txt"),
    "event": os.path.join(DEFAULT_LOG_DIR, "event_logs", "event_log.txt"),
    "file_io": os.path.join(DEFAULT_LOG_DIR, "file_io_logs", "file_io_log.txt"),
    "warning": os.path.join(DEFAULT_LOG_DIR, "warning_logs", "warning_log.txt"),
}

# Create log directories if they don't exist
for log_path in LOG_PATHS.values():
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

class SnowballLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SnowballLogger, cls).__new__(cls)
                    cls._instance._initialize_loggers()
        return cls._instance

    def _initialize_loggers(self):
        """Initialize separate loggers for each log type."""
        self.loggers = {}
        for log_type, log_path in LOG_PATHS.items():
            logger = logging.getLogger(log_type)
            logger.setLevel(logging.DEBUG)

            handler = RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=15)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO if log_type != "error" else logging.ERROR)

            logger.addHandler(handler)
            logger.propagate = False  # Prevent logs from being passed to parent loggers

            self.loggers[log_type] = logger

        # Add a console handler for debugging purposes
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)

    def _setup_handlers(self):
        """Set up different file handlers for each type of log."""
        if not self.logger.handlers:  # Avoid adding handlers multiple times
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Assign different levels for different logs
            log_levels = {
                "interaction": logging.INFO,
                "error": logging.ERROR,
                "system_health": logging.INFO,
                "event": logging.INFO,
                "file_io": logging.INFO,
                "warning": logging.WARNING,
            }

            # Add handlers for each log type with specific filtering
            for log_name, log_path in LOG_PATHS.items():
                level = logging.INFO if log_name not in ["error", "warning"] else logging.WARNING
                handler = RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=15)
                handler.setLevel(level)
                handler.setFormatter(formatter)

                # Add a filter to the handler
                handler.addFilter(logging.Filter(log_name))
                self.logger.addHandler(handler)

            # Add console handler for real-time debugging
            if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

    def _add_handler(self, log_path, level, formatter):
        """Add a file handler to the logger."""
        if not any(isinstance(handler, RotatingFileHandler) and handler.baseFilename == log_path for handler in self.logger.handlers):
            handler = RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=15)
            handler.setLevel(level)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)


    def log_event(self, message):
        self.loggers["event"].info(message)

    def log_warning(self, message):
        self.loggers["warning"].warning(message)

    def log_error(self, message):
        self.loggers["error"].error(message)
        self.notify_user("Error", message)

    def log_interaction(self, user_message, ai_response):
        self.loggers["interaction"].info(f"User: {user_message} | AI: {ai_response}")

    def log_system_health(self, cpu_usage, memory_usage=None, temp=None, disk_usage=None):
        health_status = f"CPU Usage: {cpu_usage}%"
        if memory_usage:
            health_status += f" | Memory Usage: {memory_usage}%"
        if temp:
            health_status += f" | Temp: {temp}°C"
        if disk_usage:
            health_status += f" | Disk Usage: {disk_usage}%"
        self.loggers["system_health"].info(health_status)

    def notify_user(self, title, message):
        message = (message[:252] + '...') if len(message) > 255 else message
        notification.notify(title=title, message=message, timeout=5)

    def shutdown_logger(self):
        """Clean up handlers properly."""
        for logger in self.loggers.values():
            handlers = logger.handlers[:]
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)

if __name__ == "__main__":
    logger = SnowballLogger()
    logger.log_event("Logger initialized.")
    logger.log_interaction("Hello", "Hi, how can I assist you?")
    logger.log_warning("This is a warning.")
    logger.log_error("This is an error.")
    logger.log_system_health(cpu_usage=75, memory_usage=60, temp=55)
