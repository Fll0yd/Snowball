import logging
import os
import json
import threading
import smtplib
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
from plyer import notification  # For notifications

# Define log paths using absolute paths (Adjust these as necessary)
LOG_DIR = os.path.abspath(r'storage/logs')

INTERACTION_LOG_PATH = os.path.join(LOG_DIR, "interaction_logs", "interaction_log.txt")
ERROR_LOG_PATH = os.path.join(LOG_DIR, "error_logs", "error_log.txt")
SYSTEM_HEALTH_LOG_PATH = os.path.join(LOG_DIR, "system_health_logs", "cpu_log.txt")
EVENT_LOG_PATH = os.path.join(LOG_DIR, "event_logs", "event_log.txt")
FILE_IO_LOG_PATH = os.path.join(LOG_DIR, "file_io_logs", "file_io_log.txt")
DECISION_LOG_PATH = os.path.join(LOG_DIR, "decision_logs", "decision_log.txt")

# Create the log directories if they don't exist
for log_path in [INTERACTION_LOG_PATH, ERROR_LOG_PATH, SYSTEM_HEALTH_LOG_PATH, EVENT_LOG_PATH, FILE_IO_LOG_PATH, DECISION_LOG_PATH]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Path to settings.json
SETTINGS_PATH = os.path.abspath(r'S:/Snowball/config/settings.json')

class SnowballLogger:
    _instance = None  # Class variable for the singleton logger instance
    _lock = threading.Lock()  # Lock for thread-safe operations

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:  # Ensure thread safety when initializing
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super(SnowballLogger, cls).__new__(cls)
                    cls._instance._initialize_logger()  # Initialize the logger
        return cls._instance

    def _initialize_logger(self):
        # Initialize the logger
        self.logger = logging.getLogger('SnowballLogger')
        self.logger.setLevel(logging.DEBUG)

        # Load settings.json for thresholds and email settings
        self._load_settings()

        # Setup the log handlers
        self._setup_handlers()

    def _load_settings(self):
        """Load system thresholds and email settings from the settings file."""
        try:
            with open(SETTINGS_PATH, 'r') as file:
                settings = json.load(file)
                thresholds = settings.get('system_monitor_thresholds', {})
                self.cpu_threshold = thresholds.get('cpu', 85)
                self.memory_threshold = thresholds.get('memory', 85)
                self.temp_threshold = thresholds.get('temperature', 80)
                self.email_settings = settings.get('email_settings', {})
        except FileNotFoundError:
            print(f"Settings file {SETTINGS_PATH} not found.")
            self.cpu_threshold, self.memory_threshold, self.temp_threshold = 85, 85, 80
            self.email_settings = {}

    def _setup_handlers(self):
        """Set up different file handlers for each type of log."""
        if not self.logger.handlers:  # Avoid adding handlers multiple times
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Adding file handlers
            self._add_handler(INTERACTION_LOG_PATH, logging.INFO, formatter)
            self._add_handler(SYSTEM_HEALTH_LOG_PATH, logging.INFO, formatter)
            self._add_handler(ERROR_LOG_PATH, logging.ERROR, formatter)
            self._add_handler(EVENT_LOG_PATH, logging.INFO, formatter)
            self._add_handler(FILE_IO_LOG_PATH, logging.INFO, formatter)
            self._add_handler(DECISION_LOG_PATH, logging.DEBUG, formatter)

            # Console handler for real-time debugging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _add_handler(self, log_path, level, formatter):
        """Add a file handler to the logger."""
        try:
            # Avoid adding multiple handlers for the same log file
            if not any(isinstance(handler, RotatingFileHandler) and handler.baseFilename == log_path for handler in self.logger.handlers):
                handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
                handler.setLevel(level)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        except Exception as e:
            print(f"Failed to add handler for {log_path}: {e}")

    def log_event(self, event_message):
        """Log system events (e.g., start/stop)."""
        with self._lock:
            self.logger.info(f"Event: {event_message}")

    def log_error(self, message):
        """Log errors, notify the user, and send email if configured."""
        with self._lock:
            self.logger.error(f"Error: {message}")
            self.notify_user("Error", message)
            self.send_error_email(message)
            if error_settings.get('auto_restart_on_crash', False):
                self.restart_system_on_crash()

    def notify_user(self, title, message):
        """Show a notification to the user for critical events."""
        message = (message[:252] + '...') if len(message) > 255 else message
        notification.notify(title=title, message=message, timeout=5)

    def send_error_email(self, message):
        """Send an email notification for critical errors."""
        if self.email_settings.get('send_error_logs', False):
            try:
                msg = MIMEText(message)
                msg['Subject'] = 'Critical Error in Snowball'
                msg['From'] = self.email_settings['from_email']
                msg['To'] = self.email_settings['to_email']

                with smtplib.SMTP(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                    server.starttls()
                    server.login(self.email_settings['from_email'], self.email_settings['email_password'])
                    server.sendmail(msg['From'], [msg['To']], msg.as_string())
                    print("Error email sent successfully.")
            except Exception as e:
                print(f"Failed to send error email: {e}")

    def restart_system_on_crash(self):
        """Restart the system in case of a crash."""
        print("Restarting system...")
        os.system('shutdown /r /t 1')  # Adjust command for your OS

    def log_interaction(self, user_message, ai_response):
        """Log interactions between the user and the AI."""
        with self._lock:
            self.logger.info(f"User: {user_message} | AI: {ai_response}")

    def log_system_health(self, cpu_usage, memory_usage=None, temp=None):
        """Log system health data and notify if thresholds are exceeded."""
        with self._lock:
            health_status = f"CPU Usage: {cpu_usage}%"
            if memory_usage is not None:
                health_status += f" | Memory Usage: {memory_usage}%"
            if temp is not None:
                health_status += f" | Temp: {temp}°C"
            self.logger.info(health_status)

            # Check thresholds and notify if necessary
            alerts = []
            if cpu_usage >= self.cpu_threshold:
                alerts.append(f"CPU usage is high: {cpu_usage}%")
            if memory_usage is not None and memory_usage >= self.memory_threshold:
                alerts.append(f"Memory usage is high: {memory_usage}%")
            if temp is not None and temp >= self.temp_threshold:
                alerts.append(f"Temperature is high: {temp}°C")

            if alerts:
                alert_message = " | ".join(alerts)
                self.notify_user("System Health Alert", alert_message)
                self.logger.warning(alert_message)

if __name__ == "__main__":
    logger = SnowballLogger()
    logger.log_event("Logger initialized.")
