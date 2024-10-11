import tkinter as tk
import os
import sys
import json

# Get the base directory of the project, which should be the Snowball directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Import the required classes
from interface.ai_config_interface import AIConfig
from interface.interface_config_interface import InterfaceConfig
from game_pref_config_interface import GamePreferencesConfig
from mobile_settings_interface import MobileAppSettingsConfig
from system_config_interface import SystemMonitorConfig
from plex_config_interface import PlexConfig
from accounts_config_interface import AccountIntegrationsConfig
from security_config_interface import SecurityPrivacyConfig
from view_logs import LogsConfig
from contact_developer_interface import ContactDeveloperConfig
from core.config_loader import ConfigLoader
from core.ai_agent import SnowballAI

# Load API keys from the JSON file
try:
    with open('S:/Snowball/config/account_integrations.json', 'r') as file:
        api_keys = json.load(file)

    # Check if the OpenAI API key is available
    openai_api_key = api_keys.get('api_keys', {}).get('openai_api_key')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in S:/Snowball/config/account_integrations.json")

    # Set environment variable for OpenAI key
    os.environ['OPENAI_API_KEY'] = openai_api_key

except FileNotFoundError:
    print("The API keys file was not found at S:/Snowball/config/account_integrations.json")
    sys.exit(1)
except json.JSONDecodeError:
    print("The API keys file is not in a valid JSON format")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

# Initialize SnowballAI with the API key
snowball_ai_instance = SnowballAI(api_key=openai_api_key)


class ConfigInterface:
    def __init__(self, master, ai_instance):
        self.master = master
        self.master.geometry("1200x800")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")
        self.ai_instance = ai_instance

        # Sidebar setup
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights to stretch the sidebar evenly
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=4)
        self.master.grid_rowconfigure(0, weight=1)

        # Create a frame for the main content
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Add sidebar options and their corresponding functions to load the correct settings
        sidebar_options = [
            ("AI Settings", self.load_ai_config),
            ("Interface Settings", self.load_interface_config),
            ("Game Preferences", self.load_game_preferences_config),
            ("Mobile App Settings", self.load_mobile_app_settings_config),
            ("System Monitor Settings", self.load_system_monitor_config),
            ("Plex Configuration", self.load_plex_config),
            ("Account Integrations", self.load_account_integrations_config),
            ("Security and Privacy", self.load_security_privacy_config),
            ("Logs", self.load_logs_config),
            ("Contact the Developer", self.load_contact_developer_config)
        ]

        # Create buttons dynamically and place them using grid layout
        for i, (label, command) in enumerate(sidebar_options):
            button = tk.Button(self.sidebar_frame, text=label, command=command,
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=18)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

    def clear_main_frame(self):
        """
        Clears the current main frame content before loading new configuration options.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def load_ai_config(self):
        """
        Load AI configuration UI.
        """
        self.clear_main_frame()
        AIConfig(self.main_frame, self.ai_instance)

    def load_interface_config(self):
        """
        Load Interface configuration UI.
        """
        self.clear_main_frame()
        InterfaceConfig(self.main_frame)

    def load_game_preferences_config(self):
        """
        Load Game Preferences configuration UI.
        """
        self.clear_main_frame()
        GamePreferencesConfig(self.main_frame)

    def load_mobile_app_settings_config(self):
        """
        Load Mobile App Settings configuration UI.
        """
        self.clear_main_frame()
        MobileAppSettingsConfig(self.main_frame)

    def load_system_monitor_config(self):
        """
        Load System Monitor Settings configuration UI.
        """
        self.clear_main_frame()
        SystemMonitorConfig(self.main_frame)

    def load_plex_config(self):
        """
        Load Plex Configuration UI.
        """
        self.clear_main_frame()
        PlexConfig(self.main_frame)

    def load_account_integrations_config(self):
        """
        Load Account Integrations configuration UI.
        """
        self.clear_main_frame()
        AccountIntegrationsConfig(self.main_frame)

    def load_security_privacy_config(self):
        """
        Load Security and Privacy configuration UI.
        """
        self.clear_main_frame()
        SecurityPrivacyConfig(self.main_frame)

    def load_logs_config(self):
        """
        Load Logs configuration UI.
        """
        self.clear_main_frame()
        LogsConfig(self.main_frame)

    def load_contact_developer_config(self):
        """
        Load Contact the Developer configuration UI.
        """
        self.clear_main_frame()
        ContactDeveloperConfig(self.main_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root, snowball_ai_instance)
    root.mainloop()
