import logging
import sys
from logging.handlers import RotatingFileHandler
from plyer import notification  # To notify on critical events
import unittest
import os
import threading
from unittest.mock import patch, mock_open

# Add the logger module to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
from logger import SnowballLogger

# Log file paths
INTERACTION_LOG_PATH = os.path.abspath('storage/logs/interaction_logs/interaction_log.txt')
ERROR_LOG_PATH = os.path.abspath('storage/logs/error_logs/error_log.txt')
SYSTEM_HEALTH_LOG_PATH = os.path.abspath('storage/logs/system_health_logs/cpu_log.txt')
EVENT_LOG_PATH = os.path.abspath('storage/logs/event_logs/event_log.txt')
FILE_IO_LOG_PATH = os.path.abspath('storage/logs/file_io_logs/file_io_log.txt')
DECISION_LOG_PATH = os.path.abspath('storage/logs/decision_logs/decision_log.txt')

LOG_DIRS = [
    os.path.dirname(INTERACTION_LOG_PATH),
    os.path.dirname(ERROR_LOG_PATH),
    os.path.dirname(SYSTEM_HEALTH_LOG_PATH),
    os.path.dirname(EVENT_LOG_PATH),
    os.path.dirname(FILE_IO_LOG_PATH),
    os.path.dirname(DECISION_LOG_PATH)
]

class TestSnowballLogger(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"system_monitor_thresholds": {"cpu": 90, "memory": 80, "temperature": 70}}')
    def setUp(self, mock_file):
        """Set up the logger instance and ensure directories and files exist."""
        # Ensure log directories exist before testing
        for dir_path in LOG_DIRS:
            os.makedirs(dir_path, exist_ok=True)

        # Initialize the logger instance, settings will be mocked
        self.logger = SnowballLogger()

        # Trigger handler initialization (this ensures log files are created)
        self.logger._setup_handlers()

        # Disable console output during testing
        self.logger.logger.handlers = [h for h in self.logger.logger.handlers if not isinstance(h, logging.StreamHandler)]

    def tearDown(self):
        """Clean up log files after each test."""
        self.logger.flush_handlers()

        log_files = [
            INTERACTION_LOG_PATH,
            ERROR_LOG_PATH,
            SYSTEM_HEALTH_LOG_PATH,
            EVENT_LOG_PATH,
            FILE_IO_LOG_PATH,
            DECISION_LOG_PATH
        ]
        # Remove the log files
        for log_file in log_files:
            try:
                if os.path.exists(log_file):
                    os.remove(log_file)
            except PermissionError:
                pass  # If the file is in use, skip deletion

    def test_log_files_created(self):
        """Ensure log files are created and contain logs after logger initialization."""
        self.logger.log_event("Log file creation test.")
        
        # Force flush to make sure the log is written
        self.logger.flush_handlers()
        
        self.assertTrue(os.path.exists(INTERACTION_LOG_PATH), f"{INTERACTION_LOG_PATH} was not created.")
        with open(INTERACTION_LOG_PATH, 'r') as log_file:
            content = log_file.read()
            self.assertIn("Log file creation test.", content)

    def test_log_interaction(self):
        """Test if interaction logs are correctly handled."""
        self.logger.log_interaction("Hi Snowball", "Hello, how can I assist?")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(INTERACTION_LOG_PATH), "Interaction log not created.")
        with open(INTERACTION_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("User: Hi Snowball | AI: Hello, how can I assist?", log_content)

    def test_log_system_health(self):
        """Test logging system health metrics."""
        self.logger.log_system_health(cpu_usage=70, memory_usage=50, temp=50)
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(SYSTEM_HEALTH_LOG_PATH), "System health log not created.")
        with open(SYSTEM_HEALTH_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("CPU Usage: 70% | Memory Usage: 50% | Temp: 50°C", log_content)

    @patch('plyer.notification.notify')
    def test_log_system_health_with_notification(self, mock_notify):
        """Test logging system health with notification when thresholds are exceeded."""
        self.logger.log_system_health(cpu_usage=90)
        self.logger.flush_handlers()
        mock_notify.assert_called_once_with(title="System Alert", message="CPU usage is high: 90%", timeout=5)

    @patch('plyer.notification.notify')
    def test_log_warning(self, mock_notify):
        """Test logging warnings and notifying the user."""
        self.logger.log_warning("Disk space is low.")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(ERROR_LOG_PATH), "Warning log not created.")
        mock_notify.assert_called_once_with(title="Warning", message="Disk space is low.", timeout=5)
        with open(ERROR_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("Warning: Disk space is low.", log_content)

    @patch('plyer.notification.notify')
    def test_log_error(self, mock_notify):
        """Test logging errors and notifying the user."""
        self.logger.log_error("File not found.")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(ERROR_LOG_PATH), "Error log not created.")
        mock_notify.assert_called_once_with(title="Error", message="File not found.", timeout=5)
        with open(ERROR_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("Error: File not found.", log_content)

    def test_log_event(self):
        """Test logging system events."""
        self.logger.log_event("Snowball started.")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(EVENT_LOG_PATH), "Event log not created.")
        with open(EVENT_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("Event: Snowball started.", log_content)

    def test_log_file_io(self):
        """Test logging file I/O operations."""
        self.logger.log_file_io("read", "config/settings.json")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(FILE_IO_LOG_PATH), "File I/O log not created.")
        with open(FILE_IO_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("File I/O: read operation performed on config/settings.json", log_content)

    def test_log_decision(self):
        """Test logging AI decisions."""
        self.logger.log_decision("AI decided to search the web.")
        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(DECISION_LOG_PATH), "Decision log not created.")
        with open(DECISION_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("Decision: AI decided to search the web.", log_content)

    def test_concurrent_logging(self):
        """Test logging from multiple threads to ensure thread safety."""
        def log_in_thread():
            for _ in range(100):
                self.logger.log_interaction("Thread logging", "This is a test.")

        threads = [threading.Thread(target=log_in_thread) for _ in range(10)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        self.logger.flush_handlers()
        self.assertTrue(os.path.exists(INTERACTION_LOG_PATH), "Interaction log not created.")
        with open(INTERACTION_LOG_PATH, "r") as log_file:
            log_content = log_file.read()
        self.assertIn("User: Thread logging | AI: This is a test.", log_content)

    def test_log_rotation(self):
        """Test log rotation when the log file exceeds its size limit."""
        handler = RotatingFileHandler(INTERACTION_LOG_PATH, maxBytes=100, backupCount=2)
        self.logger.logger.addHandler(handler)

        for i in range(200):
            self.logger.log_interaction(f"Interaction {i}", "Testing rotation")

        self.logger.flush_handlers()

        log_files = os.listdir(os.path.dirname(INTERACTION_LOG_PATH))
        rotated_logs = [f for f in log_files if "interaction_log" in f]
        self.assertGreaterEqual(len(rotated_logs), 2)

    @patch("builtins.open", new_callable=mock_open, read_data='{"system_monitor_thresholds": {"cpu": 90, "memory": 80, "temperature": 70}}')
    def test_logger_loads_thresholds_from_settings(self, mock_file):
        """Test that the logger loads thresholds from the settings.json file."""
        self.logger._initialize_logger()
        self.assertEqual(self.logger.cpu_threshold, 90)
        self.assertEqual(self.logger.memory_threshold, 80)
        self.assertEqual(self.logger.temp_threshold, 70)


if __name__ == "__main__":
    unittest.main()
