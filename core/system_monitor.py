import clr  # For accessing .NET libraries from Python
import psutil
from plyer import notification
import os
import time
import pystray
from PIL import Image
import GPUtil
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import platform
import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
from core.mobile_integration import MobileIntegration
from core.config_loader import load_config
sys.path.append('S:/logs')
from core.logger import SnowballLogger

# Load OpenHardwareMonitor DLL for fan monitoring
dll_path = r"C:/Program Files/OpenHardwareMonitor/OpenHardwareMonitorLib.dll"
clr.AddReference(dll_path)

# Import the OpenHardwareMonitor classes
from OpenHardwareMonitor import Hardware

# Load the system thresholds from settings.json
settings = load_config('settings.json')
thresholds = settings['system_monitor_thresholds']

cpu_threshold = thresholds['cpu']
memory_threshold = thresholds['memory']
temperature_threshold = thresholds['temperature']

def check_system_health():
    # Use thresholds in your logic here
    if get_cpu_usage() > cpu_threshold:
        print("CPU usage is too high!")
    if get_memory_usage() > memory_threshold:
        print("Memory usage is too high!")
    if get_temperature() > temperature_threshold:
        print("System temperature is too high!")
        
class FanMonitor:
    def __init__(self):
        self.computer = Hardware.Computer()
        self.computer.FanControllerEnabled = True
        self.computer.Open()

    def get_fan_speeds(self):
        """Retrieve fan speeds from OpenHardwareMonitor."""
        fan_speeds = []
        for hardware in self.computer.Hardware:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == Hardware.SensorType.Fan:
                    fan_speeds.append((sensor.Name, sensor.Value))
        return fan_speeds

    def print_fan_speeds(self):
        speeds = self.get_fan_speeds()
        for fan, speed in speeds:
            print(f"{fan}: {speed} RPM")
        return speeds

# Windows Defender quick scan for malware/virus detection
def run_windows_defender_scan():
    """Run a quick scan using Windows Defender."""
    scan_command = 'powershell Start-MpScan -ScanType QuickScan'
    os.system(scan_command)

# Disk health check using chkdsk
def check_disk_health():
    """Schedule a chkdsk scan for the next reboot if the volume is in use."""
    check_command = 'chkdsk /f /r'
    print("Scheduling a chkdsk scan on the next reboot.")
    os.system(f'schtasks /create /tn "CheckDisk" /tr "{check_command}" /sc onstart')

# File system check using SFC
def run_sfc_scan():
    """Run an SFC scan to check for file integrity."""
    sfc_command = 'sfc /scannow'
    os.system(sfc_command)

# System Monitoring Class
class SystemMonitor:
    def __init__(self, cpu_threshold=80, memory_threshold=80, temp_threshold=80):
        # Initialize logger
        self.logger = SnowballLogger()
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.temp_threshold = temp_threshold
        self.platform = platform.system().lower()
        self.temp_supported = self.check_temp_support()  # Check for temperature sensor support
        self.fan_monitor = FanMonitor()  # Initialize fan monitoring
        self._monitor_lock = threading.Lock()  # Lock for thread-safe system monitoring
        self.mobile_integration = MobileIntegration()  # Initialize mobile integration
        self.notifications_sent = {"cpu": False, "memory": False, "temp": False}  # Track sent notifications

    def start_system_monitoring(self):
        """Continuously monitor the system's CPU, memory, and temperature."""
        while True:
            self.check_system_metrics()
            time.sleep(10)  # Adjust monitoring interval

    def check_system_metrics(self):
        """Check CPU, memory, and temperature, and send alerts if thresholds are exceeded."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        temp = psutil.sensors_temperatures().get('coretemp', [{'current': 0}])[0]['current']
        temperatures = psutil.sensors_temperatures().get('coretemp', [{'current': 0}])
        temperature = temperatures[0]['current'] if temperatures else 0

        if cpu_usage > self.cpu_threshold and not self.notifications_sent['cpu']:
            self.mobile_integration.send_alert(f"Warning: CPU usage is high at {cpu_usage}%")
            self.send_alert(f"CPU usage is high at {cpu_usage}%")
            self.notifications_sent['cpu'] = True  # Prevent spamming

        if memory_usage > self.memory_threshold and not self.notifications_sent['memory']:
            self.mobile_integration.send_alert(f"Warning: Memory usage is high at {memory_usage}%")
            self.send_alert(f"Memory usage is high at {memory_usage}%")
            self.notifications_sent['memory'] = True

        if temp > self.temp_threshold and not self.notifications_sent['temp']:
            self.mobile_integration.send_alert(f"Warning: System temperature is high at {temperature}°C")
            self.send_alert(f"System temperature is high at {temp}°C")
            self.notifications_sent['temp'] = True

    def send_alert(self, message):
        """Send alerts via mobile and desktop notification."""
        print(f"Sending alert: {message}")
        notification.notify(title="System Alert", message=message, timeout=5)
        self.mobile_integration.send_alert(message)

    def send_notifications_if_needed(self):
        """Monitor system health and send push notifications if thresholds are exceeded."""
        self.check_system_metrics()

    def adjust_thresholds(self, cpu_threshold=None, memory_threshold=None, temp_threshold=None):
        """Allow customization of thresholds via mobile app."""
        if cpu_threshold:
            self.cpu_threshold = cpu_threshold
        if memory_threshold:
            self.memory_threshold = memory_threshold
        if temp_threshold:
            self.temp_threshold = temp_threshold
        print(f"New thresholds: CPU {self.cpu_threshold}%, Memory {self.memory_threshold}%, Temp {self.temp_threshold}°C")
        
    def monitor_system(self):
        """Monitor the system health and log system metrics."""
        while True:
            with self._monitor_lock:  # Thread safety
                cpu_usage = self.check_cpu_usage()
                memory_usage = self.check_memory_usage()
                temperature = self.check_temperature()

                # Log the system health metrics
                self.logger.log_system_health(cpu_usage, memory_usage, temperature)

                # Trigger real-time alerts if thresholds are exceeded
                self.check_thresholds(cpu_usage, memory_usage, temperature)

            time.sleep(5)  # Sleep before next check

    def check_temp_support(self):
        """Check if temperature monitoring is supported."""
        if hasattr(psutil, 'sensors_temperatures'):
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    return True
                else:
                    self.logger.log_warning("No temperature sensors found on this system.")
            except Exception as e:
                self.logger.log_warning(f"Error reading temperatures: {str(e)}")
        self.logger.log_warning("Temperature monitoring not supported on this system.")
        return False

    def set_temp_threshold(self, new_threshold):
        """Set a new temperature threshold."""
        self.temp_threshold = new_threshold
    
    def set_temp_threshold(self, new_threshold):
        """Set a new temperature threshold."""
        self.temp_threshold = new_threshold
        self.logger.log_interaction("Temp Threshold Set", f"New temperature threshold: {self.temp_threshold}°C")

    def check_thresholds(self, cpu_usage, memory_usage, temp):
        """Check if any system metrics exceed defined thresholds."""
        if cpu_usage > self.cpu_threshold:
            self.logger.log_warning(f"High CPU Usage: {cpu_usage}%")
            self.notify_user("High CPU Usage", f"CPU usage exceeded: {cpu_usage}%")
        if memory_usage > self.memory_threshold:
            self.logger.log_warning(f"High Memory Usage: {memory_usage}%")
            self.notify_user("High Memory Usage", f"Memory usage exceeded: {memory_usage}%")
        if temp and temp > self.temp_threshold:
            self.logger.log_warning(f"High Temperature: {temp}°C")
            self.notify_user("High Temperature", f"System temperature exceeded: {temp}°C")
    
    def check_backup_status():
        backup_file = '/path/to/backup'  # Replace with actual backup path
        if not os.path.exists(backup_file):
            self.logger.notify_user("Backup Issue", "Backup file not found. Please check your backup routine.")

    def monitor_network_spikes(self):
        """Detect network traffic spikes."""
        net_io_start = psutil.net_io_counters()
        time.sleep(5)  # Check after 5 seconds
        net_io_end = psutil.net_io_counters()

        bytes_sent_diff = net_io_end.bytes_sent - net_io_start.bytes_sent
        bytes_recv_diff = net_io_end.bytes_recv - net_io_start.bytes_recv

        if bytes_sent_diff > 10**6 or bytes_recv_diff > 10**6:  # Customize threshold as needed
            print("Network traffic spike detected!")
            print(f"Bytes Sent: {bytes_sent_diff}, Bytes Received: {bytes_recv_diff}")

    def detect_memory_leak(self):
        """Detect if there are any memory leaks by checking processes using high memory."""
        processes = [(p.info['pid'], p.info['name'], p.info['memory_percent']) 
                    for p in psutil.process_iter(['pid', 'name', 'memory_percent'])]
        
        # Identify processes using more than 10% of memory (adjust threshold as needed)
        high_memory_usage_processes = [proc for proc in processes if proc[2] > 10.0]
        
        if high_memory_usage_processes:
            for proc in high_memory_usage_processes:
                print(f"High memory usage: PID: {proc[0]}, Name: {proc[1]}, Memory: {proc[2]}%")
        else:
            print("No memory leaks detected.")

    def check_smart_status(self):
        """Check SMART status for drives using smartctl (requires smartmontools)."""
        command = ["C:/Program Files/smartmontools/bin/smartctl.exe", "-a", "/dev/sda"]
        
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Print and return the SMART status output
                print(result.stdout)
                return result.stdout
            else:
                # Print any error messages captured from stderr
                print(f"Error: {result.stderr}")
                return None
        except FileNotFoundError as e:
            print(f"Command not found: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def show_gpu_usage_tray(self):
        gpu_usage, gpu_temp = self.check_gpu_usage()
        if gpu_usage is not None and gpu_temp is not None:
            print(f"GPU Usage: {gpu_usage}%, GPU Temp: {gpu_temp}°C")
        else:
            print

    def check_cpu_usage(self):
        """Check CPU usage and log if it exceeds the threshold."""
        cpu_usage = psutil.cpu_percent(interval=1)  # Use a 1-second interval
        if cpu_usage > self.cpu_threshold:
            self.logger.notify_user("High CPU Usage", f"CPU usage is at {cpu_usage}%")
        return cpu_usage

    def check_memory_usage(self):
        """Check memory usage and log if it exceeds the threshold."""
        memory_info = psutil.virtual_memory()
        if memory_info.percent > self.memory_threshold:
            self.logger.notify_user("High Memory Usage", f"Memory usage is at {memory_info.percent}%")
        return memory_info.percent

    def check_disk_usage(self):
        """Check disk usage across partitions."""
        partitions = psutil.disk_partitions()
        disk_data = []
        for partition in partitions:
            try:
                if not os.path.exists(partition.mountpoint):  # Check if the mountpoint exists
                    print(f"{partition.device} not mounted.")
                    continue
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"Disk usage for {partition.device}: {usage.percent}%")
                disk_data.append((partition.device, usage.percent))
            except (PermissionError, FileNotFoundError, OSError) as e:
                print(f"Could not access {partition.device}: {e}")
                self.logger.log_error(f"Error accessing {partition.device}: {e}")
        return disk_data

    def check_network_activity(self):
        """Check network activity (bytes sent/received)."""
        net_io = psutil.net_io_counters()
        print(f"Bytes Sent: {net_io.bytes_sent}, Bytes Received: {net_io.bytes_recv}")
        return net_io.bytes_sent, net_io.bytes_recv

    def check_running_processes(self):
        """Check running processes and display the top 5 by CPU usage."""
        processes = [(p.info['pid'], p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
        processes = sorted(processes, key=lambda x: x[2], reverse=True)[:5]
        print("Top 5 processes by CPU usage:")
        for proc in processes:
            print(f"PID: {proc[0]}, Name: {proc[1]}, CPU Usage: {proc[2]}%")
        return processes

    def check_application_logs(self):
        """Check for critical errors in system logs."""
        log_command = 'wevtutil qe System /c:5 /q:"*[System[(Level=1 or Level=2)]]" /f:text'
        os.system(log_command)

    def check_fan_speeds(self):
        """Check and display fan speeds."""
        return self.fan_monitor.print_fan_speeds()

    def check_temperature(self):
        """Check system temperature if supported."""
        if not self.temp_supported:
            return None  # Exit if not supported
        try:
            temps = psutil.sensors_temperatures()
            for name, entries in temps.items():
                for entry in entries:
                    print(f"{name} Temperature: {entry.current}°C")
                    if entry.current > self.temp_threshold:
                        self.logger.notify_user(f"High {name} Temperature", f"{name} temperature: {entry.current}°C")
                        return entry.current
        except Exception as e:
            self.logger.log_error(f"Temperature check failed: {e}")
        return None

    def check_gpu_usage(self):
        """Check GPU usage and temperature."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:  # Check if any GPUs are available
                gpu = gpus[0]  # Consider only the first GPU for simplicity
                gpu_usage = gpu.load * 100
                gpu_temp = gpu.temperature
                if gpu_usage > self.cpu_threshold or gpu_temp > self.temp_threshold:
                    self.logger.notify_user(
                        "High GPU Usage or Temperature",
                        f"GPU {gpu.name}: {gpu_usage:.1f}% load, {gpu_temp}°C"
                    )
                print(f"GPU: {gpu.name}, Load: {gpu_usage:.1f}%, Temp: {gpu_temp}°C")
                return gpu_usage, gpu_temp
        except Exception as e:
            self.logger.log_error(f"GPU monitoring not available: {e}")
        return None, None

    def notify_user(self, title, message):
        """Send a desktop notification for critical events."""
        truncated_message = (message[:252] + '...') if len(message) > 256 else message
        notification.notify(
            title=title,
            message=truncated_message,
            timeout=5  # Notification timeout in seconds
        )

    def start_system_tray_with_duck_icon(self):
        """Start the system tray with the Snowball duck icon."""
        icon = pystray.Icon("Snowball AI")
        with Image.open('S:/icon/trayicon.png') as icon_image:
            icon.icon = icon_image
        icon.menu = pystray.Menu(
            pystray.MenuItem('Show CPU Usage', lambda: print(f"CPU Usage: {self.check_cpu_usage()}%")),
            pystray.MenuItem('Show Memory Usage', lambda: print(f"Memory Usage: {self.check_memory_usage()}%")),
            pystray.MenuItem('Show GPU Usage', lambda: self.check_gpu_usage()),
            pystray.MenuItem('Show Disk Usage', lambda: print(f"Disk Usage: {self.check_disk_usage()}")),
            pystray.MenuItem('Show Network Activity', lambda: print(f"Network Activity: {self.check_network_activity()}")),
            pystray.MenuItem('Show Running Processes', lambda: print(f"Running Processes: {self.check_running_processes()}")),
            pystray.MenuItem('Show Fan Speeds', lambda: self.check_fan_speeds()),
            pystray.MenuItem('Exit', self.exit_program)
        )
        icon.run()
        
    def exit_program(self, icon, item):
        """Exit the system tray app."""
        icon.stop()

    def monitor_system(self):
        """Continuously monitor the system."""
        while True:
            self.check_cpu_usage()
            self.check_memory_usage()
            self.check_disk_usage()
            self.check_network_activity()
            self.check_running_processes()
            self.check_temperature()
            self.check_gpu_usage()
            self.check_fan_speeds()
            time.sleep(10)  # Wait 10 seconds before the next check

# Visualization Class for Real-Time Graphs
class VisualMonitor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("System Performance Monitor")
        self.create_graphs()

    def create_graphs(self):
        """Create graphs for CPU and Memory usage."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 5))

        # CPU usage graph
        self.cpu_usage = [0] * 10
        ax1.set_title("CPU Usage (%)")
        self.cpu_line, = ax1.plot(self.cpu_usage)
        ax1.set_ylim(0, 100)  # Set y-axis limits for CPU usage

        # Memory usage graph
        self.memory_usage = [0] * 10
        ax2.set_title("Memory Usage (%)")
        self.memory_line, = ax2.plot(self.memory_usage)
        ax2.set_ylim(0, 100)  # Set y-axis limits for Memory usage

        # Embed the plots in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().pack()

        # Call the update function every second
        self.update_graphs()  # Directly call the method once to set it off

    def update_graphs(self):
        """Update the graphs with live data."""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        # Update CPU usage graph
        self.cpu_usage = self.cpu_usage[1:] + [cpu]
        self.cpu_line.set_ydata(self.cpu_usage)

        # Update memory usage graph
        self.memory_usage = self.memory_usage[1:] + [memory]
        self.memory_line.set_ydata(self.memory_usage)

        # Redraw the figure
        plt.draw()

        # Schedule the next update
        self.window.after(1000, self.update_graphs)

# Main Execution
if __name__ == "__main__":
    monitor = SystemMonitor(cpu_threshold=50, memory_threshold=50, temp_threshold=75)
    visual_monitor = VisualMonitor()

    # Run the system tray and monitor in separate threads
    tray_thread = threading.Thread(target=monitor.start_system_tray_with_duck_icon)
    tray_thread.start()

    monitor_thread = threading.Thread(target=monitor.monitor_system)
    monitor_thread.start()
    
    # Start the Tkinter visual monitor
    visual_monitor.window.mainloop()
