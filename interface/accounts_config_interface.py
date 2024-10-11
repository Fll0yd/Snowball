import tkinter as tk
from tkinter import messagebox
import json
import os

class AccountIntegrationsConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")

        # Load current settings or use defaults
        self.config_path = 'S:/Snowball/config/account_integrations.json'
        self.config = self.load_config()

        # Create widgets for account integrations
        self.create_widgets()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "The account integrations configuration file was not found.")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "The account integrations configuration file is not in a valid JSON format.")
            return {}

    def create_widgets(self):
        # Title label
        tk.Label(self.master, text="Account Integrations", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Frame to hold the integration settings
        self.integration_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.integration_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create textboxes for each account integration
        self.entry_widgets = {}
        if 'api_keys' in self.config:
            for account, key in self.config['api_keys'].items():
                self.add_integration_field(account, key)

        # Add Save Button
        self.save_button = tk.Button(self.master, text="Save Changes", command=self.save_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=10)

    def add_integration_field(self, account, key):
        # Create label and entry for account
        frame = tk.Frame(self.integration_frame, bg="#2c2c2c")
        frame.pack(fill=tk.X, pady=5)

        tk.Label(frame, text=f"{account} API Key:", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat", width=50)
        entry.insert(0, key)
        entry.pack(side=tk.RIGHT, padx=5)

        self.entry_widgets[account] = entry

    def save_config(self):
        # Get updated values from entries
        updated_keys = {}
        for account, entry in self.entry_widgets.items():
            updated_keys[account] = entry.get()

        # Update config
        self.config['api_keys'] = updated_keys

        # Save to file
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config, file, indent=4)
            messagebox.showinfo("Success", "Account integrations have been updated successfully.")
        except IOError:
            messagebox.showerror("Error", "Unable to save changes. Check if the file is accessible.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountIntegrationsConfig(root)
    root.mainloop()