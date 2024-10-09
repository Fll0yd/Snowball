import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ConfigInterface:
    def __init__(self, master):
        self.master = master
        self.master.geometry("900x600")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")

        # Load consolidated configuration files into a dictionary
        self.config_files = {}
        self.load_consolidated_files()

        # Create a frame for the sidebar
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=200)
        self.sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

        # Create a frame for the main content
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Label for main content
        self.header_label = tk.Label(self.main_frame, text="Configuration Settings", font=("Arial", 16), fg="white", bg="#2c2c2c")
        self.header_label.pack(anchor="nw", pady=10)

        # Create dropdown to select configuration file (shown in main panel for selected configs)
        self.config_selector_label = tk.Label(self.main_frame, text="Select Configuration File:", font=("Arial", 12), fg="white", bg="#2c2c2c")
        self.config_selector_label.pack(anchor="nw", pady=5)

        self.selected_config = tk.StringVar()
        self.config_selector = ttk.Combobox(self.main_frame, textvariable=self.selected_config, state="readonly")
        self.config_selector['values'] = list(self.config_files.keys())
        self.config_selector.pack(anchor="nw", pady=5, padx=10)
        self.config_selector.bind("<<ComboboxSelected>>", self.load_config_contents)

        # Display selected config content
        self.config_text = tk.Text(self.main_frame, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10), bg="#3e3e3e", fg="white", relief="flat")
        self.config_text.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Save Button
        self.save_button = tk.Button(self.main_frame, text="Save Changes", command=self.save_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(anchor="e", pady=10)

        # Create sidebar options for different configuration sections
        sidebar_options = [
            "AI Settings",
            "Game Preferences",
            "Interface Settings",
            "Chat Settings",
            "Plex Configuration",
            "Mobile App Settings",
            "Security and Privacy",
            "Account Integrations",
            "Logs",
            "Contact the Developer"
        ]

        for option in sidebar_options:
            button = tk.Button(self.sidebar_frame, text=option, command=lambda opt=option: self.change_header(opt),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=18, pady=10)
            button.pack(pady=5)

    def load_consolidated_files(self):
        """
        Load all consolidated configuration files into the dictionary.
        """
        config_path = 'S:/Snowball/config/'
        consolidated_files = [
            "account_integrations.json",
            "ai_settings.json",
            "game_preferences.json",
            "interface_settings.json",
            "chat_settings.json",
            "plex_config.json",
            "mobile_app_settings.json",
            "security_privacy.json",
            "error_reporting.json"
        ]

        for file_name in consolidated_files:
            full_path = os.path.join(config_path, file_name)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    self.config_files[file_name] = json.load(f)

    def load_config_contents(self, event):
        """
        Load the contents of the selected configuration file into the text box.
        """
        selected_file = self.selected_config.get()
        if selected_file:
            config_data = self.config_files[selected_file]
            config_json = json.dumps(config_data, indent=4)
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(tk.END, config_json)

    def save_config(self):
        """
        Save changes made to the selected configuration file.
        """
        selected_file = self.selected_config.get()
        if selected_file:
            try:
                updated_config = json.loads(self.config_text.get(1.0, tk.END))
                config_path = f'S:/Snowball/config/{selected_file}'
                with open(config_path, 'w') as f:
                    json.dump(updated_config, f, indent=4)
                self.config_files[selected_file] = updated_config
                messagebox.showinfo("Success", f"Configuration file '{selected_file}' saved successfully.")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format. Please correct the format and try again.")

    def change_header(self, section_name):
        """
        Placeholder method to handle sidebar button interactions.
        """
        self.header_label.config(text=f"{section_name} Settings")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root)
    root.mainloop()
