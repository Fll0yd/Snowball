import logging
import os
import threading
import datetime
from logging.handlers import RotatingFileHandler
from plyer import notification  # For notifications
import smtplib
from email.mime.text import MIMEText
from typing import Optional

# Define log paths using the default value (it can be overridden later by passing config)
DEFAULT_LOG_DIR = os.path.join('S:/Snowball/storage/logs')

LOG_PATHS = {
    "interaction": os.path.join(DEFAULT_LOG_DIR, "interaction_logs", "interaction_log.txt"),
    "error": os.path.join(DEFAULT_LOG_DIR, "error_logs", "error_log.txt"),
    "system_health": os.path.join(DEFAULT_LOG_DIR, "system_health_logs", "system_health_log.txt"),
    "event": os.path.join(DEFAULT_LOG_DIR, "event_logs", "event_log.txt"),
    "file_io": os.path.join(DEFAULT_LOG_DIR, "file_io_logs", "file_io_log.txt"),
    "decision": os.path.join(DEFAULT_LOG_DIR, "decision_logs", "decision_log.txt"),
    "config_change": os.path.join(DEFAULT_LOG_DIR, "config_logs", "config_log.txt"),
    "warning": os.path.join(DEFAULT_LOG_DIR, "warning_logs", "warning_log.txt"),
    "security": os.path.join(DEFAULT_LOG_DIR, "security_logs", "security_log.txt"),
    "task": os.path.join(DEFAULT_LOG_DIR, "task_logs", "task_log.txt"),
}

# Create the log directories if they don't exist
for log_path in LOG_PATHS.values():
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

class SnowballLogger:
    _instance = None  # Class variable for the singleton logger instance
    _lock = threading.Lock()  # Lock for thread-safe operations

    def __new__(cls, settings=None):
        if cls._instance is None:
            with cls._lock:  # Ensure thread safety when initializing
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super(SnowballLogger, cls).__new__(cls)
                    cls._instance._initialize_logger(settings)  # Initialize the logger with settings
        return cls._instance

    def _initialize_logger(self, settings=None):
        # Initialize the logger
        self.logger = logging.getLogger('SnowballLogger')
        self.logger.setLevel(logging.DEBUG)

        # Use the provided settings or default values
        self.cpu_threshold = settings.get('cpu', 85) if settings else 85
        self.memory_threshold = settings.get('memory', 85) if settings else 85
        self.temp_threshold = settings.get('temperature', 80) if settings else 80
        self.email_settings = settings.get('email_settings', {}) if settings else {}
        self.error_settings = settings.get('error_settings', {}) if settings else {}

        self._setup_handlers()

    def _setup_handlers(self):
        """Set up different file handlers for each type of log."""
        if not self.logger.handlers:  # Avoid adding handlers multiple times
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Adding file handlers
            for log_name, log_path in LOG_PATHS.items():
                level = logging.INFO if log_name != "error" else logging.ERROR
                self._add_handler(log_path, level, formatter)

            # Console handler for real-time debugging (avoid adding multiple times)
            if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

    def _add_handler(self, log_path, level, formatter):
        """Add a file handler to the logger."""
        try:
            # Avoid adding multiple handlers for the same log file
            if not any(isinstance(handler, RotatingFileHandler) and handler.baseFilename == log_path for handler in self.logger.handlers):
                handler = RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=15)
                handler.setLevel(level)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        except Exception as e:
            self.logger.error(f"Failed to add handler for {log_path}: {e}")

    def log_config_change(self, setting_name, old_value, new_value, user):
        """Log configuration changes with old and new values and user info."""
        with self._lock:
            change_message = f"Config Change - User: '{user}', Setting: '{setting_name}', Old Value: '{old_value}', New Value: '{new_value}', Timestamp: '{datetime.datetime.now()}'"
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

    def shutdown_logger(self):
        """Clean up handlers and close the logger properly."""
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

if __name__ == "__main__":
    logger = SnowballLogger()
    logger.log_event("Logger initialized.")
