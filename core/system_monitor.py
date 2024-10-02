import psutil
import tkinter as tk
from tkinter import messagebox
import logging
import json
import time
import threading
import statistics
from logging.handlers import RotatingFileHandler
from plyer import notification
import GPUtil
import requests
import os
import smtplib
from email.mime.text import MIMEText
from matplotlib import pyplot as plt  # For data visualization
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import logging.config
from tkinter import Tk, Canvas, Label
from typing import List, Dict, Any

# Load configuration from settings.json
def load_settings() -> Dict[str, Any]:
    try:
        with open('settings.json') as f:
            settings = json.load(f)
            # Validate JSON structure
            if not all(key in settings["system_monitor_thresholds"] for key in ["cpu", "memory", "temperature"]):
                raise ValueError("Invalid settings format")
            return settings
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading settings: {e}")
        return {
            "system_monitor_thresholds": {
                "cpu": 80,
                "memory": 80,
                "temperature": 80
            }
        }

# Set up logging with rotation
def setup_logging() -> logging.Logger:
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
        self.logger = setup_logging()

        # Thresholds from settings
        self.cpu_threshold = self.settings["system_monitor_thresholds"]["cpu"]
        self.memory_threshold = self.settings["system_monitor_thresholds"]["memory"]
        self.temp_threshold = self.settings["system_monitor_thresholds"]["temperature"]

        self.root = tk.Tk()
        self.root.title("System Monitor")

        # UI Elements
        self.cpu_label = tk.Label(self.root, text="CPU Usage: ")
        self.cpu_label.pack()

        self.memory_label = tk.Label(self.root, text="Memory Usage: ")
        self.memory_label.pack()

        self.temp_label = tk.Label(self.root, text="Temperature: ")
        self.temp_label.pack()

        # Start monitoring
        self.running = True
        self.update_ui()

        # Initialize the fan monitor
        self.fan_monitor = self.FanMonitor()

    class FanMonitor:
        def __init__(self) -> None:
            self.fan_speeds: List[float] = []

        def get_fan_speed(self) -> float:
            try:
                fan_speed = psutil.sensors_fans()  # Example using psutil
                if fan_speed and fan_speed[0]:  # Ensure there's at least one fan detected
                    return fan_speed[0][0].current if fan_speed[0] else 0.0
            except Exception as e:
                logging.error(f"Error getting fan speed: {e}")
            return 0.0

        def log_fan_speed(self) -> None:
            """Logs the current fan speed and stores it for statistical analysis."""
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
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Error getting CPU usage: {e}")
            return 0

    def get_memory_usage(self) -> float:
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0

    def get_temperature(self) -> float:
        try:
            # This method may require platform-specific implementation or additional libraries
            return 65  # Placeholder for actual temperature reading
        except Exception as e:
            self.logger.error(f"Error getting temperature: {e}")
            return 0

    def check_alerts(self):
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        temperature = self.get_temperature()

        if cpu_usage > self.cpu_threshold:
            self.logger.warning(f"CPU usage exceeded threshold: {cpu_usage}%")
            messagebox.showwarning("Alert", f"CPU usage exceeded threshold: {cpu_usage}%")
            self.send_alert(f"CPU usage exceeded threshold: {cpu_usage}%")

        if memory_usage > self.memory_threshold:
            self.logger.warning(f"Memory usage exceeded threshold: {memory_usage}%")
            messagebox.showwarning("Alert", f"Memory usage exceeded threshold: {memory_usage}%")
            self.send_alert(f"Memory usage exceeded threshold: {memory_usage}%")

        if temperature > self.temp_threshold:
            self.logger.warning(f"Temperature exceeded threshold: {temperature}°C")
            messagebox.showwarning("Alert", f"Temperature exceeded threshold: {temperature}°C")
            self.send_alert(f"Temperature exceeded threshold: {temperature}°C")

    def update_ui(self):
        threading.Thread(target=self.monitor_system).start()
        self.root.after(1000, self.update_ui)  # Update UI every second

    def monitor_system(self):
        self.check_alerts()
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        temperature = self.get_temperature()

        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.memory_label.config(text=f"Memory Usage: {memory_usage}%")
        self.temp_label.config(text=f"Temperature: {temperature}°C")

    def log_cpu_usage(self) -> None:
        """Logs the current CPU usage and stores it for statistical analysis."""
        current_cpu_usage = psutil.cpu_percent(interval=1)
        self.cpu_usage.append(current_cpu_usage)
        logging.info(f"Current CPU usage: {current_cpu_usage}%")

    def log_memory_usage(self) -> None:
        """Logs the current memory usage and stores it for statistical analysis."""
        current_memory_usage = psutil.virtual_memory().percent
        self.memory_usage.append(current_memory_usage)
        logging.info(f"Current memory usage: {current_memory_usage}%")

    def log_disk_usage(self) -> None:
        """Logs the current disk usage and stores it for statistical analysis."""
        current_disk_usage = psutil.disk_usage('/').percent
        self.disk_usage.append(current_disk_usage)
        logging.info(f"Current disk usage: {current_disk_usage}%")

    def log_network_usage(self) -> None:
        """Logs the current network usage and stores it for statistical analysis."""
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
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                logging.info(f"GPU ID: {gpu.id}, GPU Usage: {gpu.load * 100}%, GPU Temp: {gpu.temperature}°C")
        except Exception as e:
            logging.error(f"Error logging GPU usage: {e}")

    def log_cpu_temperature(self) -> float:
        """Logs the CPU temperature if supported."""
        try:
            temp = psutil.sensors_temperatures()['coretemp'][0].current  # Adjust as per your system
            logging.info(f"Current CPU temperature: {temp}°C")
            return temp
        except Exception as e:
            logging.warning("Could not retrieve CPU temperature.")
            return None

    def send_email_report(self) -> None:
        """Sends an email report of system performance."""
        report = f"""
        System Performance Report:
        CPU Usage: {self.get_cpu_usage()}%
        Memory Usage: {self.get_memory_usage()}%
        Disk Usage: {psutil.disk_usage('/').percent}%
        Fan Speed: {self.fan_monitor.average_fan_speed()} RPM
        Network Usage: {self.network_usage[-1] if self.network_usage else 'No data'} bytes
        Running Processes: {self.process_stats}
        """
        msg = MIMEText(report)
        msg['Subject'] = 'System Performance Report'
        msg['From'] = 'YOUR_EMAIL@gmail.com'
        msg['To'] = 'RECIPIENT_EMAIL@gmail.com'

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('YOUR_EMAIL@gmail.com', 'YOUR_EMAIL_PASSWORD')
                server.send_message(msg)
            logging.info("Sent email report.")
        except Exception as e:
            logging.error(f"Error sending email report: {e}")

    def schedule_reports(self, interval: int) -> None:
        """Schedules regular reports of system performance."""
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.send_email_report, 'interval', seconds=interval)
        self.scheduler.start()
        logging.info(f"Scheduled reports every {interval} seconds.")

    def check_thresholds(self, cpu_threshold: float, memory_threshold: float, disk_threshold: float) -> None:
        """Checks system metrics against thresholds and sends alerts if exceeded."""
        if (self.average_cpu_usage() > self.cpu_threshold):
            self.send_alert("CPU usage exceeded threshold!")
        if (self.average_memory_usage() > self.memory_threshold):
            self.send_alert("Memory usage exceeded threshold!")
        if (self.average_disk_usage() > self.disk_threshold):
            self.send_alert("Disk usage exceeded threshold!")

    def send_alert(self, message: str) -> None:
        """Sends an alert to the mobile app or displays a desktop notification."""
        notification.notify(
            title="System Monitor Alert",
            message=message,
            app_name="System Monitor"
        )
        # Replace with your actual alert system (e.g., sending to a webhook)
        try:
            requests.post('YOUR_WEBHOOK_URL', json={"text": message})
            logging.info(f"Alert sent: {message}")
        except Exception as e:
            logging.error(f"Error sending alert: {e}")

        requests.post('YOUR_WEBHOOK_URL', json={"text": message})

    def average_cpu_usage(self) -> float:
        """Calculates the average CPU usage."""
        if self.cpu_usage:
            avg_cpu = statistics.mean(self.cpu_usage)
            logging.info(f"Average CPU usage: {avg_cpu}%")
            return avg_cpu
        logging.warning("No CPU usage data available for average calculation.")
        return 0.0

    def average_memory_usage(self) -> float:
        """Calculates the average memory usage."""
        if self.memory_usage:
            avg_memory = statistics.mean(self.memory_usage)
            logging.info(f"Average memory usage: {avg_memory}%")
            return avg_memory
        logging.warning("No memory usage data available for average calculation.")
        return 0.0

    def average_disk_usage(self) -> float:
        """Calculates the average disk usage."""
        if self.disk_usage:
            avg_disk = statistics.mean(self.disk_usage)
            logging.info(f"Average disk usage: {avg_disk}%")
            return avg_disk
        logging.warning("No disk usage data available for average calculation.")
        return 0.0

    def get_system_specs(self) -> None:
        """Logs the system specifications."""
        logging.info(f"System Specs: {os.uname()}")
        logging.info(f"CPU: {psutil.cpu_count(logical=True)} cores, {psutil.cpu_freq().current} MHz")
        logging.info(f"Memory: {psutil.virtual_memory().total / (1024 ** 3)} GB")
        logging.info(f"Disk: {psutil.disk_usage('/').total / (1024 ** 3)} GB")

    def visualize_data(self) -> None:
        """Visualizes the performance metrics using matplotlib."""
        plt.figure(figsize=(15, 10))

        plt.subplot(2, 2, 1)
        plt.plot(self.cpu_usage, label='CPU Usage (%)')
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time (intervals)')
        plt.ylabel('CPU Usage (%)')
        plt.legend()

        plt.subplot(2, 2, 2)
        plt.plot(self.memory_usage, label='Memory Usage (%)')
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time (intervals)')
        plt.ylabel('Memory Usage (%)')
        plt.legend()

        plt.subplot(2, 2, 3)
        plt.plot(self.disk_usage, label='Disk Usage (%)')
        plt.title('Disk Usage Over Time')
        plt.xlabel('Time (intervals)')
        plt.ylabel('Disk Usage (%)')
        plt.legend()

        plt.subplot(2, 2, 4)
        plt.plot(self.network_usage, label='Network Activity (bytes)')
        plt.title('Network Activity Over Time')
        plt.xlabel('Time (intervals)')
        plt.ylabel('Network Activity (bytes)')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def cleanup_resources(self) -> None:
        """Cleans up resources, stops the scheduler, and closes the program gracefully."""
        self.scheduler.shutdown()
        logging.info("Cleaned up resources and shut down the system monitor.")

    def display_ui(self) -> None:
        """ Displays a simple UI for monitoring system metrics. """
        root = Tk()
        root.title("System Monitor")

        canvas = Canvas(root, width=400, height=300)
        canvas.pack()

        Label(root, text="System Performance Metrics", font=("Helvetica", 16)).pack()
        Label(root, text=f"CPU Usage: {self.average_cpu_usage():.2f}%", font=("Helvetica", 14)).pack()
        Label(root, text=f"Memory Usage: {self.average_memory_usage():.2f}%", font=("Helvetica", 14)).pack()
        Label(root, text=f"Disk Usage: {self.average_disk_usage():.2f}%", font=("Helvetica", 14)).pack()

        root.mainloop()

    def run(self, report_interval: int = 5) -> None:
        """Main loop to log system metrics continuously."""
        self.root.mainloop()
        self.schedule_reports(report_interval)
        try:
            while True:
                self.log_cpu_usage()
                self.log_memory_usage()
                self.log_disk_usage()
                self.log_network_usage()
                self.log_running_processes()
                self.fan_monitor.log_fan_speed()
                self.log_gpu_usage()
                self.log_cpu_temperature()
                self.check_thresholds(cpu_threshold=80, memory_threshold=80, disk_threshold=90)
                time.sleep(report_interval)
        except KeyboardInterrupt:
            self.scheduler.shutdown()
            logger.info("System Monitor stopped.")
            self.cleanup_resources()

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.get_system_specs()
    monitor.run(report_interval=3600)  # Send an email report every hour
