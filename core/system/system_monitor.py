import psutil
import json
import time
import logging
import os
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from azure.storage.blob import BlobServiceClient
import matplotlib.pyplot as plt
from plyer import notification
import GPUtil
from email.mime.text import MIMEText
import smtplib

# Get the base directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the log directory relative to the Snowball project structure
LOG_DIR = os.path.join(BASE_DIR, '../../storage/logs/system_health_logs')
LOG_FILE = os.path.join(LOG_DIR, 'system_health_log.json')

# Ensure the directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Configuration for alerts and thresholds
DEFAULT_SETTINGS = {
    "resource_thresholds": {
        "cpu_usage_percent": {"critical_threshold": 90},
        "memory_usage_percent": {"critical_threshold": 85},
        "disk_space_percent": {"critical_threshold": 95},
        "gpu_usage_percent": {"critical_threshold": 90},
        "temperature_celsius": {"critical_threshold": 80}
    },
    "email_settings": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email_from": "your_email@gmail.com",
        "email_to": "recipient_email@gmail.com",
        "email_password": "your_password"
    },
    "monitoring_frequency": 5,  # in seconds
    "upload_frequency": 300  # in seconds
}

def load_connection_string(config_path="S:/Snowball/config/account_integrations.json"):
    """
    Load the Azure connection string from the account_integrations.json file.
    """
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config["api_keys"]["azure_connection_string"]
    except KeyError as e:
        raise KeyError(f"Missing key in configuration: {e}")
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file not found.")

class AzureUploader:
    def __init__(self, container_name, config_path="S:/Snowball/config/account_integrations.json"):
        connection_string = load_connection_string(config_path)
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

        if not self.container_client.exists():
            raise Exception(f"Container '{container_name}' does not exist in Azure Storage.")

    def upload_log_file(self, file_path, blob_name):
        try:
            with open(file_path, "rb") as data:
                self.container_client.upload_blob(name=blob_name, data=data, overwrite=True)
            logging.info(f"Uploaded {file_path} to Azure as {blob_name}")
        except Exception as e:
            logging.error(f"Azure upload failed: {e}")

class SystemMonitor:
    def __init__(self, settings=DEFAULT_SETTINGS):
        self.cpu_threshold = settings["resource_thresholds"]["cpu_usage_percent"]["critical_threshold"]
        self.memory_threshold = settings["resource_thresholds"]["memory_usage_percent"]["critical_threshold"]
        self.disk_threshold = settings["resource_thresholds"]["disk_space_percent"]["critical_threshold"]
        self.gpu_threshold = settings["resource_thresholds"]["gpu_usage_percent"]["critical_threshold"]
        self.temperature_threshold = settings["resource_thresholds"]["temperature_celsius"]["critical_threshold"]
        self.email_settings = settings["email_settings"]
        self.monitoring_frequency = settings["monitoring_frequency"]

        # Logger setup
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.info("SystemMonitor initialized.")

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        return psutil.virtual_memory().percent

    def get_disk_usage(self):
        return psutil.disk_usage('/').percent

    def get_gpu_usage(self):
        try:
            gpus = GPUtil.getGPUs()
            return max(gpu.load * 100 for gpu in gpus) if gpus else 0
        except Exception as e:
            self.logger.error(f"Error getting GPU usage: {e}")
            return 0

    def get_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            for _, entries in temps.items():
                for entry in entries:
                    if entry.current:
                        return entry.current
            return 0
        except Exception as e:
            self.logger.error(f"Error getting temperature: {e}")
            return 0

    def send_alert(self, message):
        notification.notify(title="System Alert", message=message)
        self.logger.warning(message)

    def send_email_alert(self, message):
        try:
            msg = MIMEText(message)
            msg['Subject'] = "System Alert"
            msg['From'] = self.email_settings["email_from"]
            msg['To'] = self.email_settings["email_to"]

            with smtplib.SMTP(self.email_settings["smtp_server"], self.email_settings["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_settings["email_from"], self.email_settings["email_password"])
                server.send_message(msg)
            self.logger.info("Email alert sent successfully.")
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")

    def log_metrics(self):
        metrics = {
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "disk_usage": self.get_disk_usage(),
            "gpu_usage": self.get_gpu_usage(),
            "temperature": self.get_temperature(),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(json.dumps(metrics) + "\n")
        self.logger.info(f"Logged metrics: {metrics}")

        # Trigger alerts if thresholds are exceeded
        if metrics["cpu_usage"] > self.cpu_threshold:
            self.send_alert(f"High CPU usage: {metrics['cpu_usage']}%")
        if metrics["memory_usage"] > self.memory_threshold:
            self.send_alert(f"High memory usage: {metrics['memory_usage']}%")
        if metrics["disk_usage"] > self.disk_threshold:
            self.send_alert(f"Low Disk Space: {metrics['disk_usage']}%")
        if metrics["gpu_usage"] > self.gpu_threshold:
            self.send_alert(f"High GPU usage: {metrics['gpu_usage']}%")
        if metrics["temperature"] > self.temperature_threshold:
            self.send_alert(f"High Temperature: {metrics['temperature']}°C")

    def visualize_data(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.get_cpu_usage(), label="CPU Usage")
        plt.plot(self.get_memory_usage(), label="Memory Usage")
        plt.legend()
        plt.show()

def periodic_upload():
    uploader = AzureUploader(container_name="system-health-logs")
    while True:
        time.sleep(DEFAULT_SETTINGS["upload_frequency"])
        blob_name = f"system_health_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        uploader.upload_log_file(LOG_FILE, blob_name)

if __name__ == "__main__":
    threading.Thread(target=periodic_upload, daemon=True).start()
    monitor = SystemMonitor()
    try:
        while True:
            monitor.log_metrics()
            time.sleep(DEFAULT_SETTINGS["monitoring_frequency"])
    except KeyboardInterrupt:
        print("Stopping System Monitor.")
