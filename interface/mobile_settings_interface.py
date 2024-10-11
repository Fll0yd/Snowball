import tkinter as tk
from tkinter import ttk, BooleanVar, Scale, messagebox
import json
import os
import sys

# Get the base directory of the project, which should be the Snowball directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Import the required modules
from core.mobile_integration import MobileIntegration

class MobileAppSettingsConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")
        self.config_path = 'S:/Snowball/config/mobile_settings.json'
        self.load_config()

        # Header label
        self.header_label = tk.Label(self.master, text="Mobile App Settings", font=("Arial", 16), fg="white", bg="#2c2c2c")
        self.header_label.pack(anchor="nw", pady=10)

        # Frame for the widgets
        self.config_widgets_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.config_widgets_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Add Save and Apply Button
        self.save_button = tk.Button(self.master, text="Save and Apply Changes", command=self.save_and_apply_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=(0, 10))

        # Add Reset to Defaults Button
        self.reset_button = tk.Button(self.master, text="Reset to Default Values", command=self.reset_to_defaults, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.reset_button.pack(side=tk.RIGHT, anchor="e", pady=10)

        # Create widgets based on the loaded configuration
        self.create_widgets()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Configuration file not found: {self.config_path}")
            self.config = {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format. Please check the configuration file.")
            self.config = {}

    def save_and_apply_config(self):
        updated_config = {}
        for widget in self.config_widgets_frame.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                key = widget.cget("text")
                input_widget = widget.children.get('input')
                if isinstance(input_widget, tk.Entry):
                    updated_config[key] = input_widget.get()
                elif isinstance(input_widget, tk.Scale):
                    updated_config[key] = input_widget.get()
                elif isinstance(input_widget, tk.Checkbutton):
                    updated_config[key] = input_widget.var.get()
                elif isinstance(input_widget, ttk.Combobox):
                    updated_config[key] = input_widget.get()

        try:
            with open(self.config_path, 'w') as file:
                json.dump(updated_config, file, indent=4)
            messagebox.showinfo("Success", "Mobile settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Unable to save configuration: {e}")

    def reset_to_defaults(self):
        # Placeholder for reset functionality, which can be customized
        default_values = {
            "push_notifications": True,
            "update_frequency": 60,
            "data_sync": True,
            "mobile_api_key": "",
            "theme": "Light"
        }
        self.update_widgets(default_values)
        messagebox.showinfo("Defaults Restored", "All settings have been restored to their default values.")

    def create_widgets(self):
        for key, value in self.config.items():
            formatted_key = key.replace('_', ' ').title()
            setting_frame = tk.LabelFrame(self.config_widgets_frame, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
            setting_frame.pack(fill=tk.X, pady=5)

            if isinstance(value, bool):
                var = BooleanVar(value=value)
                checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
                checkbox.var = var
                checkbox.pack(side=tk.LEFT, padx=5)
                setting_frame.children['input'] = checkbox

            elif isinstance(value, int):
                slider = Scale(setting_frame, from_=1, to=120, orient="horizontal", bg="#2c2c2c", fg="white")
                slider.set(value)
                slider.pack(fill=tk.X, padx=5)
                setting_frame.children['input'] = slider

            elif isinstance(value, str):
                entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                entry.insert(0, value)
                entry.pack(fill=tk.X, padx=5)
                setting_frame.children['input'] = entry

    def update_widgets(self, updated_config):
        for widget in self.config_widgets_frame.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                key = widget.cget("text").lower().replace(" ", "_")
                input_widget = widget.children.get('input')
                if input_widget and key in updated_config:
                    value = updated_config[key]
                    if isinstance(input_widget, tk.Entry):
                        input_widget.delete(0, tk.END)
                        input_widget.insert(0, str(value))
                    elif isinstance(input_widget, tk.Scale):
                        input_widget.set(value)
                    elif isinstance(input_widget, tk.Checkbutton):
                        input_widget.var.set(value)

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileAppSettingsConfig(root)
    root.mainloop()