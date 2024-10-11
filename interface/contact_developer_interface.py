import tkinter as tk
from tkinter import BooleanVar, ttk, messagebox, Scale
import json
import os

# Define the path to the configuration file
CONFIG_FILE_PATH = 'S:/Snowball/config/contact_developer.json'

class ContactDeveloperConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")

        # Load current settings or use defaults
        self.config = self.load_config() or self.default_settings()

        # Create widgets for contact information and settings
        self.create_widgets()

    def default_settings(self):
        return {
            "developer_name": "Your Name",
            "email": "your.email@example.com",
            "phone_number": "123-456-7890",
            "notifications_enabled": True,
            "support_response_time": 24,
            "auto_reply_enabled": False
        }

    def load_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to load configuration file. Invalid JSON format.")
        return None

    def save_config(self):
        try:
            with open(CONFIG_FILE_PATH, 'w') as file:
                json.dump(self.config, file, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except IOError:
            messagebox.showerror("Error", "Failed to save configuration file. Please check file permissions.")

    def create_widgets(self):
        tk.Label(self.master, text="Contact Developer Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Developer Name
        self.developer_name_var = tk.StringVar(value=self.config.get("developer_name", ""))
        self.create_entry("Developer Name", self.developer_name_var)

        # Email
        self.email_var = tk.StringVar(value=self.config.get("email", ""))
        self.create_entry("Email", self.email_var)

        # Phone Number
        self.phone_number_var = tk.StringVar(value=self.config.get("phone_number", ""))
        self.create_entry("Phone Number", self.phone_number_var)

        # Notifications Enabled
        self.notifications_enabled_var = BooleanVar(value=self.config.get("notifications_enabled", True))
        self.create_switch("Enable Notifications", self.notifications_enabled_var)

        # Support Response Time (Slider)
        self.support_response_time_var = tk.IntVar(value=self.config.get("support_response_time", 24))
        self.create_slider("Support Response Time (hrs)", self.support_response_time_var, 1, 72)

        # Auto Reply Enabled
        self.auto_reply_enabled_var = BooleanVar(value=self.config.get("auto_reply_enabled", False))
        self.create_switch("Enable Auto Reply", self.auto_reply_enabled_var)

        # Save Button
        save_button = tk.Button(self.master, text="Save Settings", command=self.save_settings, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(pady=10)

    def create_entry(self, label_text, variable):
        frame = tk.Frame(self.master, bg="#2c2c2c")
        frame.pack(fill="x", pady=5)
        label = tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c")
        label.pack(side="left", padx=5)
        entry = tk.Entry(frame, textvariable=variable, font=("Arial", 12), bg="#4d4d4d", fg="white", relief="flat")
        entry.pack(side="right", fill="x", expand=True, padx=5)

    def create_switch(self, label_text, variable):
        frame = tk.Frame(self.master, bg="#2c2c2c")
        frame.pack(fill="x", pady=5)
        label = tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c")
        label.pack(side="left", padx=5)
        checkbutton = tk.Checkbutton(frame, variable=variable, bg="#2c2c2c", fg="white", font=("Arial", 12), selectcolor="#4d4d4d")
        checkbutton.pack(side="right", padx=5)

    def create_slider(self, label_text, variable, min_value, max_value):
        frame = tk.Frame(self.master, bg="#2c2c2c")
        frame.pack(fill="x", pady=5)
        label = tk.Label(frame, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c")
        label.pack(side="left", padx=5)
        slider = Scale(frame, from_=min_value, to=max_value, orient="horizontal", variable=variable, bg="#2c2c2c", fg="white", font=("Arial", 10), highlightbackground="#2c2c2c", troughcolor="#4d4d4d")
        slider.pack(side="right", fill="x", expand=True, padx=5)

    def save_settings(self):
        # Update the config dictionary with current values
        self.config["developer_name"] = self.developer_name_var.get()
        self.config["email"] = self.email_var.get()
        self.config["phone_number"] = self.phone_number_var.get()
        self.config["notifications_enabled"] = self.notifications_enabled_var.get()
        self.config["support_response_time"] = self.support_response_time_var.get()
        self.config["auto_reply_enabled"] = self.auto_reply_enabled_var.get()

        # Save to file
        self.save_config()

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactDeveloperConfig(root)
    root.mainloop()