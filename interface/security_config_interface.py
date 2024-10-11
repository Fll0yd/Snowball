import tkinter as tk
from tkinter import ttk, BooleanVar, filedialog, messagebox
import json
import os

class SecurityPrivacyConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")
        self.config_file_path = 'S:/Snowball/config/security_privacy.json'

        # Load current settings or use defaults
        self.config = self.load_config() or self.default_settings()

        # Create widgets for Security and Privacy settings
        self.create_widgets()

    def load_config(self):
        try:
            with open(self.config_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "The configuration file was not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "The configuration file is not in a valid JSON format.")
        return None

    def save_config(self):
        try:
            with open(self.config_file_path, 'w') as file:
                json.dump(self.config, file, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the configuration: {e}")

    def default_settings(self):
        return {
            "encryption_enabled": True,
            "auto_logout": 10,
            "firewall_enabled": True,
            "vpn_required": False,
            "data_retention_period": 30
        }

    def create_widgets(self):
        tk.Label(self.master, text="Security and Privacy Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Encryption Enabled
        self.encryption_var = BooleanVar(value=self.config.get("encryption_enabled", True))
        encryption_checkbox = tk.Checkbutton(self.master, text="Enable Encryption", variable=self.encryption_var, bg="#2c2c2c", fg="white", selectcolor="#4d4d4d", font=("Arial", 12))
        encryption_checkbox.pack(anchor="w", pady=5)

        # Auto Logout (in minutes)
        tk.Label(self.master, text="Auto Logout (minutes):", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w", pady=5)
        self.auto_logout_slider = tk.Scale(self.master, from_=1, to=60, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#ffffff")
        self.auto_logout_slider.set(self.config.get("auto_logout", 10))
        self.auto_logout_slider.pack(fill="x", padx=10, pady=5)

        # Firewall Enabled
        self.firewall_var = BooleanVar(value=self.config.get("firewall_enabled", True))
        firewall_checkbox = tk.Checkbutton(self.master, text="Enable Firewall", variable=self.firewall_var, bg="#2c2c2c", fg="white", selectcolor="#4d4d4d", font=("Arial", 12))
        firewall_checkbox.pack(anchor="w", pady=5)

        # VPN Required
        self.vpn_var = BooleanVar(value=self.config.get("vpn_required", False))
        vpn_checkbox = tk.Checkbutton(self.master, text="Require VPN", variable=self.vpn_var, bg="#2c2c2c", fg="white", selectcolor="#4d4d4d", font=("Arial", 12))
        vpn_checkbox.pack(anchor="w", pady=5)

        # Data Retention Period (in days)
        tk.Label(self.master, text="Data Retention Period (days):", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w", pady=5)
        self.data_retention_slider = tk.Scale(self.master, from_=1, to=365, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#ffffff")
        self.data_retention_slider.set(self.config.get("data_retention_period", 30))
        self.data_retention_slider.pack(fill="x", padx=10, pady=5)

        # Save Button
        save_button = tk.Button(self.master, text="Save Settings", command=self.save_settings, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(anchor="e", pady=10, padx=10)

    def save_settings(self):
        self.config["encryption_enabled"] = self.encryption_var.get()
        self.config["auto_logout"] = self.auto_logout_slider.get()
        self.config["firewall_enabled"] = self.firewall_var.get()
        self.config["vpn_required"] = self.vpn_var.get()
        self.config["data_retention_period"] = self.data_retention_slider.get()
        self.save_config()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Security and Privacy Settings")
    app = SecurityPrivacyConfig(root)
    root.mainloop()