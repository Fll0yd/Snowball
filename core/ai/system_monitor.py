# system_monitor.py (S:/Snowball/core)

import psutil
import tkinter as tk
from tkinter import messagebox
import logging
import time
import statistics
from logging.handlers import RotatingFileHandler
from plyer import notification
import GPUtil
import requests
import smtplib
from email.mime.text import MIMEText
from matplotlib import pyplot as plt
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Dict, Any
import os
import json
import threading

from core.initializer import SnowballInitializer

class Config:
    EMAIL_SUBJECT = 'System Performance Report'
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    @staticmethod
    def load_settings() -> Dict[str, Any]:
        """Load configuration from system_monitor_settings.json."""
        logger = logging.getLogger("SystemMonitor")
        try:
            with open("system_monitor_settings.json", "r") as config_file:
                settings = json.load(config_file)
            if "resource_thresholds" not in settings:
                raise ValueError("Missing 'resource_thresholds' in settings.")
            return settings
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading settings: {e}")
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

    @staticmethod
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
    def __init__(self, initializer):
        # Use components from SnowballInitializer
        self.logger = initializer.logger
        self.config_loader = initializer.config_loader

        # Load configuration settings for system monitoring
        self.settings = self.config_loader.load_config("system_monitor_settings.json")

        # Ensure settings contain the expected keys
        if "resource_thresholds" not in self.settings:
            self.settings["resource_thresholds"] = {
                "cpu": 90,  # Default CPU threshold
                "memory": 80  # Default Memory threshold
            }

        # Extract thresholds from settings
        thresholds = self.settings["resource_thresholds"]
        self.disk_threshold = thresholds.get("disk_space_percent", {}).get("critical_threshold", 95)
        self.temperature_threshold = thresholds.get("temperature_celsius", {}).get("critical_threshold", 90)

        # Set default thresholds
        self.cpu_threshold = self.settings.get('cpu_usage_percent', {}).get('critical_threshold', 90)
        self.memory_threshold = self.settings.get('memory_usage_percent', {}).get('critical_threshold', 85)

        # Log that the system monitor has been initialized
        self.logger.info("SystemMonitor initialized.")

        # Start monitoring
        self.running = True
        self.schedule_reports(interval=60)

    def monitor_system(self):
        threading.Thread(target=self.update_metrics, daemon=True).start()
        
        # Initialize metrics lists for logging
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.disk_usage: List[float] = []
        self.network_usage: List[float] = []

        # Flags for tracking unsupported features
        self.temperature_supported = True

        # Start monitoring
        self.running = True
        self.schedule_reports(interval=60)  # Schedule reports every minute

    class FanMonitor:
        def __init__(self) -> None:
            self.logger = SnowballLogger()
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
                self.logger.log_error(f"Error getting fan speed: {e}")
            return 0.0

        def log_fan_speed(self) -> None:
            """Logs the current fan speed."""
            current_fan_speed = self.get_fan_speed()
            self.fan_speeds.append(current_fan_speed)
            self.logger.log_system_health(cpu_usage=0, temp=0, disk_usage=0, network_bandwidth=0, memory_usage=0)

        def average_fan_speed(self) -> float:
            """Calculates the average fan speed."""
            if self.fan_speeds:
                avg_speed = statistics.mean(self.fan_speeds)
                self.logger.log_event(f"Average fan speed: {avg_speed} RPM")
                return avg_speed
            self.logger.log_warning("No fan speed data available for average calculation.")
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
            return 65.0  # Return a default temperature when unsupported

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    for entry in entries:
                        if entry.current:
                            return entry.current
            self.logger.warning("Temperature sensors not available on this system.")
        except AttributeError:
            self.logger.warning("sensors_temperatures not supported by psutil on this system.")
            self.temperature_supported = False
        except Exception as e:
            self.logger.error(f"Error getting temperature: {e}")

        return 65.0

    def check_alerts(self):
        """Check if system metrics exceed thresholds and send alerts."""
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        temperature = self.get_temperature()

        if cpu_usage > self.cpu_threshold:
            self.logger.warning(f"CPU usage exceeded threshold: {cpu_usage}%")
            self.send_alert(f"CPU usage exceeded threshold: {cpu_usage}%")

        if memory_usage > self.memory_threshold:
            self.logger.warning(f"Memory usage exceeded threshold: {memory_usage}%")
            self.send_alert(f"Memory usage exceeded threshold: {memory_usage}%")

        if temperature > self.temperature_threshold:
            self.logger.warning(f"Temperature exceeded threshold: {temperature}°C")
            self.send_alert(f"Temperature exceeded threshold: {temperature}°C")

    def monitor_system(self):
        """Monitor system metrics without creating a UI."""
        # Run the update method on a separate thread to keep the GUI responsive
        threading.Thread(target=self.update_metrics, daemon=True).start()

    def update_metrics(self):
        while self.running:
            self.check_alerts()
            time.sleep(5)  # Adjust this sleep interval to reduce the frequency of metric collection

    def schedule_reports(self, interval: int) -> None:
        """Schedule a report to be logged periodically without a UI."""
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.log_metrics, 'interval', seconds=interval)
        scheduler.start()
        self.logger.info("Schedule Reports: Scheduled with interval {} seconds".format(interval))

    def log_metrics(self) -> None:
        """Log current CPU, memory, and disk usage."""
        self.logger.info(f"CPU Usage: {self.get_cpu_usage()}%")
        self.logger.info(f"Memory Usage: {self.get_memory_usage()}%")
        self.logger.info(f"Temperature: {self.get_temperature()}°C")

    def alert_user(self, message: str):
        """Show an alert message to the user."""
        messagebox.showwarning("Alert", message)

    def create_monitor_ui(self):
        """Create the UI for monitoring the system."""
        self.master = tk.Tk()
        self.master.title("System Monitor")

        # UI Elements
        self.cpu_label = tk.Label(self.master, text="CPU Usage: ")
        self.cpu_label.pack()

        self.memory_label = tk.Label(self.master, text="Memory Usage: ")
        self.memory_label.pack()

        self.temp_label = tk.Label(self.master, text="Temperature: ")
        self.temp_label.pack()

    def update_ui(self):
        """Update the UI with current system metrics."""
        if not self.running:
            return  # Stop updating if the monitoring is not running

        # Run system metrics collection on a separate thread to reduce UI lag
        threading.Thread(target=self.update_metrics).start()

        # Schedule the next update only if the window is still open
        if self.running:
            self.master.after(1000, self.update_ui)

    def log_cpu_usage(self) -> None:
        """Logs the current CPU usage."""
        current_cpu_usage = self.get_cpu_usage()
        self.cpu_usage.append(current_cpu_usage)
        self.logger.info(f"Current CPU usage: {current_cpu_usage}%")

    def log_memory_usage(self) -> None:
        """Logs the current memory usage."""
        current_memory_usage = self.get_memory_usage()
        self.memory_usage.append(current_memory_usage)
        self.logger.info(f"Current memory usage: {current_memory_usage}%")

    def log_disk_usage(self) -> None:
        """Logs the current disk usage."""
        current_disk_usage = psutil.disk_usage('/').percent
        self.disk_usage.append(current_disk_usage)
        self.logger.info(f"Current disk usage: {current_disk_usage}%")

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
            self.logger.log_error(f"Error getting network usage: {e}")
            return 0

    def send_email(self, message: str) -> None:
        """Send an email with the specified message."""
        try:
            email_settings = self.settings.get('email', {})
            msg = MIMEText(message)
            msg['Subject'] = Config.EMAIL_SUBJECT
            msg['From'] = email_settings.get('from', '')
            msg['To'] = email_settings.get('to', '')

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(email_settings.get('from', ''), email_settings.get('password', ''))
                server.send_message(msg)
            self.logger.log_event("Email sent successfully.")
        except Exception as e:
            self.logger.log_error(f"Error sending email: {e}")

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

    def send_alert(self, message: str) -> None:
        """Send an alert via desktop notification."""
        notification.notify(title='System Alert', message=message)
        self.logger.info("Send Alert: Completed")

    def stop(self):
        """Stop monitoring gracefully."""
        self.running = False
        self.logger.info("System monitoring stopped.")

if __name__ == '__main__':
    try:
        initializer = SnowballInitializer()  # Initialize components
        monitor = SystemMonitor(initializer)
        monitor.monitor_system()
    except KeyboardInterrupt:
        initializer.logger.info("System Monitor stopped.")
    finally:
        if monitor:
            monitor.stop()
