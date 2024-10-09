import logging
import os
import json
import threading
import smtplib
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
from plyer import notification  # For notifications
from core.config_loader import ConfigLoader
import psutil  # For system health tracking
import datetime

# Load the log directory from config or use a default value
CONFIG = ConfigLoader.load_config("interface_settings.json")
LOG_DIR = CONFIG.get("log_directory", os.path.abspath('storage/logs'))

# Define log paths using the loaded configuration
INTERACTION_LOG_PATH = os.path.join(LOG_DIR, "interaction_logs", "interaction_log.txt")
ERROR_LOG_PATH = os.path.join(LOG_DIR, "error_logs", "error_log.txt")
SYSTEM_HEALTH_LOG_PATH = os.path.join(LOG_DIR, "system_health_logs", "cpu_log.txt")
EVENT_LOG_PATH = os.path.join(LOG_DIR, "event_logs", "event_log.txt")
FILE_IO_LOG_PATH = os.path.join(LOG_DIR, "file_io_logs", "file_io_log.txt")
DECISION_LOG_PATH = os.path.join(LOG_DIR, "decision_logs", "decision_log.txt")
CONFIG_CHANGE_LOG_PATH = os.path.join(LOG_DIR, "config_logs", "config_log.txt")  # New log path for configuration changes
WARNING_LOG_PATH = os.path.join(LOG_DIR, "warning_logs", "warning_log.txt")  # New warning log path
SECURITY_LOG_PATH = os.path.join(LOG_DIR, "security_logs", "security_log.txt")  # New security log path
TASK_LOG_PATH = os.path.join(LOG_DIR, "task_logs", "task_log.txt")  # New task log path

# Create the log directories if they don't exist
for log_path in [INTERACTION_LOG_PATH, ERROR_LOG_PATH, SYSTEM_HEALTH_LOG_PATH, EVENT_LOG_PATH, FILE_IO_LOG_PATH, DECISION_LOG_PATH, CONFIG_CHANGE_LOG_PATH, WARNING_LOG_PATH, SECURITY_LOG_PATH, TASK_LOG_PATH]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

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

        # Load settings from the configuration file using ConfigLoader
        try:
            settings = ConfigLoader.load_config("interface_settings.json")
            thresholds = settings.get('system_monitor_thresholds', {})
            self.cpu_threshold = thresholds.get('cpu', 85)
            self.memory_threshold = thresholds.get('memory', 85)
            self.temp_threshold = thresholds.get('temperature', 80)
            self.email_settings = settings.get('email_settings', {})
            self.error_settings = settings.get('error_settings', {})
            self.logger.info("Successfully loaded logger settings from interface_settings.json")
        except Exception as e:
            self.logger.error(f"Settings file could not be loaded: {e}")
            self.cpu_threshold, self.memory_threshold, self.temp_threshold = 85, 85, 80
            self.email_settings = {}
            self.error_settings = {}

        # Setup the log handlers
        self._setup_handlers()

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
            self._add_handler(CONFIG_CHANGE_LOG_PATH, logging.INFO, formatter)  # Handler for config changes
            self._add_handler(WARNING_LOG_PATH, logging.WARNING, formatter)  # Handler for warnings
            self._add_handler(SECURITY_LOG_PATH, logging.WARNING, formatter)  # Handler for security-related logs
            self._add_handler(TASK_LOG_PATH, logging.INFO, formatter)  # Handler for task-related logs

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
                handler = RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=15)  # Use smaller chunks for rotation
                handler.setLevel(level)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        except Exception as e:
            self.logger.error(f"Failed to add handler for {log_path}: {e}")

    def log_config_change(self, setting_name, old_value, new_value, user):
        """Log configuration changes with old and new values and user info."""
        with self._lock:
            change_message = f"Config Change - User: '{user}', Setting: '{setting_name}', Old Value: '{old_value}', New Value: '{new_value}', Timestamp: '{datetime.datetime.now()}"
            self.logger.info(change_message)

    def log_event(self, event_message):
        """Log system events (e.g., start/stop)."""
        with self._lock:
            self.logger.info(f"Event: {event_message}")

    def log_warning(self, warning_message):
        """Log warnings that are notable but not critical."""
        with self._lock:
            self.logger.warning(f"Warning: {warning_message}")

    def log_error(self, message):
        """Log errors, notify the user, and send email if configured."""
        with self._lock:
            self.logger.error(f"Error: {message}")
            self.notify_user("Error", message)
            self.send_error_email(message)
            if self.error_settings.get('auto_restart_on_crash', False):
                self.restart_system_on_crash()

    def log_security_event(self, security_message):
        """Log security-related events such as unauthorized access attempts."""
        with self._lock:
            self.logger.warning(f"Security: {security_message}")

    def log_task(self, task_name, status):
        """Log task-related events, e.g., start/stop of background tasks."""
        with self._lock:
            task_message = f"Task: '{task_name}' - Status: '{status}'"
            self.logger.info(task_message)

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
                    self.logger.info("Error email sent successfully.")
            except Exception as e:
                self.logger.error(f"Failed to send error email: {e}")

    def restart_system_on_crash(self):
        """Restart the system in case of a crash."""
        self.logger.info("Restarting system...")
        os.system('shutdown /r /t 1')  # Adjust command for your OS

    def log_interaction(self, user_message, ai_response):
        """Log interactions between the user and the AI."""
        with self._lock:
            self.logger.info(f"User: {user_message} | AI: {ai_response}")

    def log_system_health(self, cpu_usage, memory_usage=None, temp=None, disk_usage=None, network_bandwidth=None):
        """Log system health data and notify if thresholds are exceeded."""
        with self._lock:
            health_status = f"CPU Usage: {cpu_usage}%"
            if memory_usage is not None:
                health_status += f" | Memory Usage: {memory_usage}%"
            if temp is not None:
                health_status += f" | Temp: {temp}°C"
            if disk_usage is not None:
                health_status += f" | Disk Usage: {disk_usage}%"
            if network_bandwidth is not None:
                health_status += f" | Network Bandwidth: {network_bandwidth} Mbps"
            
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