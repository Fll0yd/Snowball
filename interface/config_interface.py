# config_interface.py (S:/Snowball/interface)
 
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, PhotoImage
import json
import os
import sys

# Set up the base directory for importing modules
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Import necessary interfaces and utilities
from interface.ai_config_interface import AIConfig
from interface.interface_config_interface import InterfaceConfig
from interface.game_pref_config_interface import GamePreferencesConfig
from interface.mobile_settings_interface import MobileAppSettingsConfig
from interface.system_config_interface import SystemMonitorConfig
from interface.plex_config_interface import PlexConfig
from interface.accounts_config_interface import AccountIntegrationsConfig
from interface.security_config_interface import SecurityPrivacyConfig
from interface.view_logs import LogsConfig
from interface.contact_developer_interface import ContactDeveloperConfig
from Snowball.core.system.config_loader import ConfigLoader

# Load API keys from the JSON file
config_path = 'S:/Snowball/config/account_integrations.json'

if not os.path.exists(config_path):
    print(f"Error: Configuration file '{config_path}' does not exist.")
    sys.exit(1)

try:
    with open(config_path, 'r') as file:
        api_keys = json.load(file)

    if "api_keys" not in api_keys:
        raise ValueError("The key 'api_keys' does not exist in the JSON file.")
    
    openai_api_key = api_keys.get('api_keys', {}).get('openai_api_key')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in S:/Snowball/config/account_integrations.json")

    os.environ['OPENAI_API_KEY'] = openai_api_key

except json.JSONDecodeError:
    print("The API keys file is not in a valid JSON format")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

config_loader = ConfigLoader()

class ConfigInterface:
    def __init__(self, master, ai_instance, config_loader):
        self.master = master
        self.ai_instance = ai_instance
        self.config_loader = config_loader

        # Window properties
        self.master.geometry("1000x800")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")

        # Add the application icon
        try:
            img = PhotoImage(file="S:/Snowball/icon/trayicon.png")
            self.master.iconphoto(False, img)
        except Exception as e:
            print(f"Failed to load image for icon: {e}")

        self.create_sidebar()
        self.create_main_frame()
        self.create_buttons()

        self.current_interface = None
        self.change_section("AI Settings", AIConfig)

    def create_sidebar(self):
        """Create a sidebar for navigation."""
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)

        self.master.grid_columnconfigure(0, weight=0)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Create sidebar options dynamically
        self.sidebar_options = {
            "AI Settings": AIConfig,
            "Interface Settings": InterfaceConfig,
            "Game Preferences": GamePreferencesConfig,
            "Mobile App Settings": MobileAppSettingsConfig,
            "System Monitor Settings": SystemMonitorConfig,
            "Plex Configuration": PlexConfig,
            "Account Integrations": AccountIntegrationsConfig,
            "Security and Privacy": SecurityPrivacyConfig,
            "Logs": LogsConfig,
            "Contact the Developer": ContactDeveloperConfig
        }

        for i, (label, config_class) in enumerate(self.sidebar_options.items()):
            button = tk.Button(self.sidebar_frame, text=label,
                               command=lambda c=config_class, l=label: self.change_section(l, c),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20, height=2)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

    def create_main_frame(self):
        """Create the main content frame for displaying settings."""
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.header_label = tk.Label(self.main_frame, text="", font=("Arial", 24, "bold"), fg="white", bg="#2c2c2c")
        self.header_label.grid(row=0, column=0, sticky="nw", pady=(0, 10))

        # Scrollable area
        self.canvas = tk.Canvas(self.main_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.config_widgets_frame = self.scrollable_frame

    def create_buttons(self):
        """Create save and reset buttons."""
        self.button_frame = tk.Frame(self.main_frame, bg="#2c2c2c")
        self.button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 10))

        self.reset_button = tk.Button(self.button_frame, text="Reset to Default Values",
                                      command=self.reset_to_defaults, bg="#4d4d4d",
                                      fg="white", font=("Arial", 12), relief="flat")
        self.reset_button.pack(side=tk.RIGHT, anchor="e", padx=(0, 10))

        self.save_button = tk.Button(self.button_frame, text="Save and Apply Changes",
                                     command=self.save_and_apply_config, bg="#4d4d4d",
                                     fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(side=tk.RIGHT, anchor="e", padx=(0, 10))

    def _on_mouse_wheel(self, event):
        if event.num == 5 or event.delta == -120 or event.delta == -1:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120 or event.delta == 1:
            self.canvas.yview_scroll(-1, "units")

    def change_section(self, section_name, interface_class):
        self.header_label.config(text=section_name)
        for widget in self.config_widgets_frame.winfo_children():
            widget.destroy()
        self.current_interface = interface_class(self.config_widgets_frame, self.config_loader)

    def save_and_apply_config(self):
        if self.current_interface:
            try:
                config_data = self.current_interface.get_current_config()
                config_name = self.header_label.cget("text").replace(" Settings", "").strip().lower() + ".json"
                self.config_loader.save_config(config_name, config_data)
                messagebox.showinfo("Success", "Configuration changes saved and applied successfully.")
                if config_name == "ai_settings.json":
                    self.ai_instance.reload_ai_settings()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving: {e}")

    def reset_to_defaults(self):
        if self.current_interface:
            try:
                self.current_interface.reset_to_default_settings()
                messagebox.showinfo("Defaults Restored", "Default settings restored successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while resetting to defaults: {e}")

if __name__ == "__main__":
    master = tk.Tk()
    app = ConfigInterface(master, None, config_loader)
    master.mainloop()
