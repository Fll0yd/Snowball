import tkinter as tk
from tkinter import ttk, BooleanVar, Scale, filedialog, messagebox
import json
import os

CONFIG_PATH = "S:/Snowball/config/system_monitor_settings.json"

class SystemMonitorConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")

        # Load configuration settings from JSON
        self.config = self.load_config()

        # Header label
        tk.Label(self.master, text="System Monitor Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Frame for configuration widgets
        self.config_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.config_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Create UI widgets for each setting
        self.create_widgets()

        # Save button
        save_button = tk.Button(self.master, text="Save Settings", command=self.save_settings, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(side=tk.BOTTOM, anchor="e", pady=10, padx=10)

    def load_config(self):
        """Load configuration from the JSON file."""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format in system_monitor_settings.json")
        return self.default_config()

    def default_config(self):
        """Return default configuration if the JSON file doesn't exist."""
        return {
            "cpu_monitoring": True,
            "memory_monitoring": True,
            "disk_monitoring": True,
            "temperature_monitoring": False,
            "monitor_interval": 10,
            "alert_threshold_cpu": 85,
            "alert_threshold_memory": 80,
            "alert_threshold_disk": 90
        }

    def create_widgets(self):
        """Create UI widgets for each setting in the configuration."""
        # CPU Monitoring Toggle
        self.cpu_monitoring_var = BooleanVar(value=self.config.get("cpu_monitoring", True))
        self.create_toggle("CPU Monitoring", self.cpu_monitoring_var)

        # Memory Monitoring Toggle
        self.memory_monitoring_var = BooleanVar(value=self.config.get("memory_monitoring", True))
        self.create_toggle("Memory Monitoring", self.memory_monitoring_var)

        # Disk Monitoring Toggle
        self.disk_monitoring_var = BooleanVar(value=self.config.get("disk_monitoring", True))
        self.create_toggle("Disk Monitoring", self.disk_monitoring_var)

        # Temperature Monitoring Toggle
        self.temperature_monitoring_var = BooleanVar(value=self.config.get("temperature_monitoring", False))
        self.create_toggle("Temperature Monitoring", self.temperature_monitoring_var)

        # Monitoring Interval Slider
        self.monitor_interval_slider = self.create_slider("Monitoring Interval (seconds)", 1, 60, self.config.get("monitor_interval", 10))

        # Alert Threshold for CPU Usage Slider
        self.alert_threshold_cpu_slider = self.create_slider("CPU Alert Threshold (%)", 50, 100, self.config.get("alert_threshold_cpu", 85))

        # Alert Threshold for Memory Usage Slider
        self.alert_threshold_memory_slider = self.create_slider("Memory Alert Threshold (%)", 50, 100, self.config.get("alert_threshold_memory", 80))

        # Alert Threshold for Disk Usage Slider
        self.alert_threshold_disk_slider = self.create_slider("Disk Alert Threshold (%)", 50, 100, self.config.get("alert_threshold_disk", 90))

    def create_toggle(self, label_text, variable):
        """Create a toggle switch (Checkbutton) for boolean settings."""
        frame = tk.Frame(self.config_frame, bg="#2c2c2c")
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        toggle = tk.Checkbutton(frame, variable=variable, bg="#2c2c2c", fg="white", selectcolor="#4d4d4d", font=("Arial", 10))
        toggle.pack(side=tk.RIGHT)

    def create_slider(self, label_text, min_value, max_value, initial_value):
        """Create a slider for integer settings."""
        frame = tk.Frame(self.config_frame, bg="#2c2c2c")
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w")
        slider = Scale(frame, from_=min_value, to=max_value, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#4d4d4d")
        slider.set(initial_value)
        slider.pack(fill=tk.X, padx=5)
        return slider

    def save_settings(self):
        """Save the current settings to the JSON file."""
        self.config["cpu_monitoring"] = self.cpu_monitoring_var.get()
        self.config["memory_monitoring"] = self.memory_monitoring_var.get()
        self.config["disk_monitoring"] = self.disk_monitoring_var.get()
        self.config["temperature_monitoring"] = self.temperature_monitoring_var.get()
        self.config["monitor_interval"] = self.monitor_interval_slider.get()
        self.config["alert_threshold_cpu"] = self.alert_threshold_cpu_slider.get()
        self.config["alert_threshold_memory"] = self.alert_threshold_memory_slider.get()
        self.config["alert_threshold_disk"] = self.alert_threshold_disk_slider.get()

        try:
            with open(CONFIG_PATH, 'w') as file:
                json.dump(self.config, file, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("System Monitor Configuration")
    app = SystemMonitorConfig(root)
    root.mainloop()