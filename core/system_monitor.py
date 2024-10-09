import psutil
import tkinter as tk
from tkinter import messagebox
import logging
import json
import time
import statistics
from logging.handlers import RotatingFileHandler
from plyer import notification
import GPUtil
import requests
import os
import smtplib
from email.mime.text import MIMEText
from matplotlib import pyplot as plt
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Dict, Any

# Import the ConfigLoader class
from core.config_loader import ConfigLoader

class Config:
    EMAIL_SUBJECT = 'System Performance Report'
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587


def load_settings() -> Dict[str, Any]:
    """Load configuration from system_monitor_settings.json."""
    try:
        settings = ConfigLoader.load_config("system_monitor_settings.json")
        if "resource_thresholds" not in settings:
            raise ValueError("Missing 'resource_thresholds' in settings.")
        return settings
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading settings: {e}")
        # Fallback to default settings if there's an issue
        return {
            "resource_thresholds": {
                "cpu_usage_percent": {
                    "warning_threshold": 75,
                    "critical_threshold": 90
                },
                "memory_usage_percent": {
                    "warning_threshold": 70,
                    "critical_threshold": 85
                },
                "disk_space_percent": {
                    "warning_threshold": 80,
                    "critical_threshold": 95
                },
                "gpu_usage_percent": {
                    "warning_threshold": 80,
                    "critical_threshold": 95
                },
                "temperature_celsius": {
                    "warning_threshold": 70,
                    "critical_threshold": 90
                },
                "network_usage_mbps": {
                    "warning_threshold": 100,
                    "critical_threshold": 200
                }
            }
        }
    
def setup_logging() -> logging.Logger:
    """Set up logging with rotation."""
    logger = logging.getLogger("SystemMonitor")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("system_monitor.log", maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class SystemMonitor:
    def __init__(self):
        self.settings = load_settings()

        # Update to use the new structure from system_monitor_settings.json
        if "resource_thresholds" not in self.settings:
            raise ValueError("Missing 'resource_thresholds' in settings.")

        thresholds = self.settings["resource_thresholds"]

        self.cpu_threshold = thresholds["cpu_usage_percent"]["critical_threshold"]
        self.memory_threshold = thresholds["memory_usage_percent"]["critical_threshold"]
        self.disk_threshold = thresholds["disk_space_percent"]["critical_threshold"]
        self.temperature_threshold = thresholds["temperature_celsius"]["critical_threshold"]

        # Continue initializing other necessary parts of the SystemMonitor
        self.logger = setup_logging()
        self.running = True

        # Flags for tracking unsupported features
        self.temperature_supported = True

        # Initialize metrics lists for logging
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.disk_usage: List[float] = []
        self.network_usage: List[float] = []
        self.process_stats: Dict[str, Any] = {}
        self.running_processes: List[str] = []

        # Initialize the fan monitor
        self.fan_monitor = self.FanMonitor()

        # Start monitoring
        self.running = True
        self.schedule_reports(interval=60)  # Schedule reports every minute

    class FanMonitor:
        def __init__(self) -> None:
            self.fan_speeds: List[float] = []

        def get_fan_speed(self) -> float:
            """Get the current fan speed."""
            try:
                fans = psutil.sensors_fans()
                if fans:
                    for entries in fans.values():
                        if entries:
                            return entries[0].current
            except Exception as e:
                logging.error(f"Error getting fan speed: {e}")
            return 0.0

        def log_fan_speed(self) -> None:
            """Logs the current fan speed."""
            current_fan_speed = self.get_fan_speed()
            self.fan_speeds.append(current_fan_speed)
            logging.info(f"Current fan speed: {current_fan_speed} RPM")

        def average_fan_speed(self) -> float:
            """Calculates the average fan speed."""
            if self.fan_speeds:
                avg_speed = statistics.mean(self.fan_speeds)
                logging.info(f"Average fan speed: {avg_speed} RPM")
                return avg_speed
            logging.warning("No fan speed data available for average calculation.")
            return 0.0

    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0

    def get_memory_usage(self) -> float:
        """Get memory usage percentage."""
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0

    def get_temperature(self) -> float:
        """Get CPU temperature, return a default if not supported or available."""
        if not self.temperature_supported:
            return 65.0  # Return default value if sensors are not supported

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    for entry in entries:
                        if entry.current:  # Return the first available temperature
                            return entry.current
            self.logger.warning("Temperature sensors not available on this system.")
        except AttributeError:
            self.logger.error("sensors_temperatures not supported by psutil on this system.")
            self.temperature_supported = False  # Disable future attempts to get temperatures
        except Exception as e:
            self.logger.error(f"Error getting temperature: {e}")
        
        return 65.0  # Return a default temperature if there are errors or no sensors

    def check_alerts(self):
        """Check if system metrics exceed thresholds and send alerts."""
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        temperature = self.get_temperature()

        if cpu_usage > self.cpu_threshold:
            self.logger.warning(f"CPU usage exceeded threshold: {cpu_usage}%")
            self.alert_user(f"CPU usage exceeded threshold: {cpu_usage}%")
            self.send_alert(f"CPU usage exceeded threshold: {cpu_usage}%")

        if memory_usage > self.memory_threshold:
            self.logger.warning(f"Memory usage exceeded threshold: {memory_usage}%")
            self.alert_user(f"Memory usage exceeded threshold: {memory_usage}%")
            self.send_alert(f"Memory usage exceeded threshold: {memory_usage}%")

        if temperature > self.temp_threshold:
            self.logger.warning(f"Temperature exceeded threshold: {temperature}°C")
            self.alert_user(f"Temperature exceeded threshold: {temperature}°C")
            self.send_alert(f"Temperature exceeded threshold: {temperature}°C")

    def alert_user(self, message: str):
        """Show an alert message to the user."""
        messagebox.showwarning("Alert", message)

    def create_monitor_ui(self):
        """Create the UI for monitoring the system."""
        self.root = tk.Tk()
        self.root.title("System Monitor")

        # UI Elements
        self.cpu_label = tk.Label(self.root, text="CPU Usage: ")
        self.cpu_label.pack()

        self.memory_label = tk.Label(self.root, text="Memory Usage: ")
        self.memory_label.pack()

        self.temp_label = tk.Label(self.root, text="Temperature: ")
        self.temp_label.pack()

    def monitor_system(self):
        """Monitor system metrics and update UI labels."""
        if not hasattr(self, 'root'):
            self.create_monitor_ui()

        self.update_ui()
        self.root.mainloop()

    def update_ui(self):
        """Update the UI with current system metrics."""
        self.check_alerts()
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        temperature = self.get_temperature()

        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.memory_label.config(text=f"Memory Usage: {memory_usage}%")
        self.temp_label.config(text=f"Temperature: {temperature}°C")

        if self.running:
            self.root.after(1000, self.update_ui)  # Update UI every second

    def log_metrics(self) -> None:
        """Log current CPU, memory, and disk usage."""
        self.log_cpu_usage()
        self.log_memory_usage()
        self.log_disk_usage()
        self.log_network_usage()
        self.log_running_processes()
        self.log_gpu_usage()
        self.fan_monitor.log_fan_speed()

    def log_cpu_usage(self) -> None:
        """Logs the current CPU usage."""
        current_cpu_usage = self.get_cpu_usage()
        self.cpu_usage.append(current_cpu_usage)
        logging.info(f"Current CPU usage: {current_cpu_usage}%")

    def log_memory_usage(self) -> None:
        """Logs the current memory usage."""
        current_memory_usage = self.get_memory_usage()
        self.memory_usage.append(current_memory_usage)
        logging.info(f"Current memory usage: {current_memory_usage}%")

    def log_disk_usage(self) -> None:
        """Logs the current disk usage."""
        current_disk_usage = psutil.disk_usage('/').percent
        self.disk_usage.append(current_disk_usage)
        logging.info(f"Current disk usage: {current_disk_usage}%")

    def log_network_usage(self) -> None:
        """Logs the current network usage."""
        net_io = psutil.net_io_counters()
        self.network_usage.append(net_io.bytes_sent + net_io.bytes_recv)
        logging.info(f"Current network usage: {net_io.bytes_sent + net_io.bytes_recv} bytes")

    def log_running_processes(self) -> None:
        """Logs currently running processes."""
        self.running_processes = [proc.name() for proc in psutil.process_iter()]
        self.process_stats = {}
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            self.process_stats[proc.info['name']] = {
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent']
            }
        logging.info(f"Running processes: {self.process_stats}")

    def log_gpu_usage(self) -> None:
        """Logs GPU usage if available."""
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                logging.info(f"GPU ID: {gpu.id}, GPU Usage: {gpu.load * 100}%, GPU Temp: {gpu.temperature}°C")
        except Exception as e:
            logging.error(f"Error getting GPU usage: {e}")

    def send_email(self, message: str) -> None:
        """Send an email with the specified message."""
        try:
            email_settings = self.settings['email']
            msg = MIMEText(message)
            msg['Subject'] = Config.EMAIL_SUBJECT
            msg['From'] = email_settings['from']
            msg['To'] = email_settings['to']

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(email_settings['from'], email_settings['password'])
                server.send_message(msg)
            logging.info("Email sent successfully.")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def send_alert(self, message: str) -> None:
        """Send an alert via email and desktop notification."""
        self.send_email(message)
        notification.notify(title='System Alert', message=message)

    def visualize_data(self):
        """Visualize logged CPU and memory usage data."""
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(self.cpu_usage, label='CPU Usage (%)')
        plt.axhline(y=self.cpu_threshold, color='r', linestyle='--', label='CPU Threshold')
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(self.memory_usage, label='Memory Usage (%)')
        plt.axhline(y=self.memory_threshold, color='r', linestyle='--', label='Memory Threshold')
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.legend()

        plt.tight_layout()
        plt.savefig(f"usage_data_{time.strftime('%Y%m%d_%H%M%S')}.png")
        plt.show()

    def schedule_reports(self, interval: int) -> None:
        """Schedule a report to be sent periodically."""
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.log_metrics, 'interval', seconds=interval)
        scheduler.start()


if __name__ == '__main__':
    try:
        monitor = SystemMonitor()
    except KeyboardInterrupt:
        logging.info("System Monitor stopped by user.")
    finally:
        if monitor:
            monitor.visualize_data()