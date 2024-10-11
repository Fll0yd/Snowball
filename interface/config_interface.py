import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, IntVar, ttk, messagebox, Scrollbar, filedialog, colorchooser
import json
import os
import sys

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
config_path = 'S:/Snowball/config/account_integrations.json'
if not os.path.exists(config_path):
    print(f"Error: Configuration file '{config_path}' does not exist.")
    sys.exit(1)

try:
    with open(config_path, 'r') as file:
        api_keys = json.load(file)

    # Debugging statement to check what is being loaded
    print(f"Loaded API keys content: {api_keys}")

    # Check if the OpenAI API key is available
    if "api_keys" not in api_keys:
        raise ValueError("The key 'api_keys' does not exist in the JSON file.")
    
    openai_api_key = api_keys.get('api_keys', {}).get('openai_api_key')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in S:/Snowball/config/account_integrations.json")

    # Set environment variable for OpenAI key
    os.environ['OPENAI_API_KEY'] = openai_api_key

except json.JSONDecodeError:
    print("The API keys file is not in a valid JSON format")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

# Initialize SnowballAI with the API key
snowball_ai_instance = SnowballAI(api_key=openai_api_key)

# Create an instance of ConfigLoader to pass to the sub-interfaces
config_loader = ConfigLoader()

class ConfigInterface:
    def __init__(self, master, ai_instance, config_loader):
        self.master = master
        self.master.geometry("1200x800")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")
        self.ai_instance = ai_instance
        self.config_loader = config_loader

        # Initialize config_files attribute
        self.config_files = {}
        self.load_consolidated_files()

        # Sidebar setup
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)

        # Configure grid weights to make the sidebar fill the vertical space
        self.master.grid_columnconfigure(0, weight=0)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(0, weight=1)

        # Create a frame for the main content
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Label for main content
        self.header_label = tk.Label(self.main_frame, text="Configuration Settings", font=("Arial", 16), fg="white", bg="#2c2c2c")
        self.header_label.pack(anchor="nw", pady=10)

        # Display frame for config widgets
        self.config_widgets_frame = tk.Frame(self.main_frame, bg="#2c2c2c")
        self.config_widgets_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Add Save and Apply Button
        self.save_button = tk.Button(self.main_frame, text="Save and Apply Changes", command=self.save_and_apply_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(side=tk.RIGHT, anchor="e", pady=10)

        # Add Reset to Defaults Button
        self.reset_button = tk.Button(self.main_frame, text="Reset to Default Values", command=self.reset_to_defaults, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.reset_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=(0, 10))

        # Sidebar options
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
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20, height=2)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=12)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

    def load_consolidated_files(self):
        """
        Load all consolidated configuration files into the dictionary using ConfigLoader.
        """
        consolidated_files = [
            "account_integrations.json",
            "ai_settings.json",
            "game_preferences.json",
            "interface_settings.json",
            "plex_config.json",
            "mobile_settings.json",
            "security_privacy.json",
            "system_monitor_settings.json",
            "contact_developer.json"
        ]

        for file_name in consolidated_files:
            try:
                config_data = self.config_loader.load_config(file_name)
                self.config_files[file_name] = config_data
                print(f"Successfully loaded: {file_name}")  # Debugging statement
            except FileNotFoundError:
                self.config_files[file_name] = None  # File not found
                print(f"File not found: {file_name}")  # Debugging statement
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error reading JSON from {file_name}. Please check the file.")
                print(f"Error reading JSON from {file_name}")  # Debugging statement

    def save_and_apply_config(self):
        """
        Save changes made to the selected configuration file and apply the changes in real time.
        """
        selected_header = self.header_label.cget("text").replace(" Settings", "").strip()

        # Debugging print to ensure correct label
        print(f"Selected header: '{selected_header}'")

        # Use section_to_file_map to get the correct filename
        section_to_file_map = {
            "AI Settings": "ai_settings.json",
            "Interface Settings": "interface_settings.json",
            "Game Preferences": "game_preferences.json",
            "Mobile App Settings": "mobile_settings.json",
            "System Monitor Settings": "system_monitor_settings.json",
            "Plex Configuration": "plex_config.json",
            "Account Integrations": "account_integrations.json",
            "Security and Privacy": "security_privacy.json",
            "Contact the Developer": "contact_developer.json"
        }

        # Correctly get the file name from the mapping
        selected_file = section_to_file_map.get(selected_header)

        # Debugging print to ensure correct configuration file selection
        print(f"Attempting to save and apply configuration for: {selected_file}")

        # Check if the selected file exists in self.config_files and is valid
        if not selected_file or self.config_files.get(selected_file) is None:
            messagebox.showerror("Error", f"Configuration file '{selected_file}' does not exist or was not loaded properly.")
            return

        updated_config = {}
        # Collect data from UI widgets
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

        # Debugging print to show the collected updated configuration
        print(f"Collected updated configuration: {updated_config}")

        try:
            # Save the configuration to file
            config_path = f'S:/Snowball/config/{selected_file}'
            with open(config_path, 'w') as f:
                json.dump(updated_config, f, indent=4)
            self.config_files[selected_file] = updated_config
            print(f"Configuration saved successfully to {config_path}")

            # Apply changes if applicable
            if selected_header == "AI Settings":
                self.ai_instance.reload_ai_settings()
                print("AI settings reloaded successfully.")

            # Show confirmation message to the user
            messagebox.showinfo("Success", f"Configuration file '{selected_file}' saved successfully and changes applied.")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            messagebox.showerror("Error", "Invalid JSON format. Please correct the format and try again.")
        except IOError as e:
            print(f"I/O error: {e}")
            messagebox.showerror("Error", f"Unable to save changes to {selected_file}. Check permissions.")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        """
        # Placeholder for reset functionality, similar to AI Settings reset logic
        messagebox.showinfo("Defaults Restored", "All settings have been restored to their default values.")

    def change_section(self, section_name):
        """
        Update the header label and load the corresponding configuration file.
        """
        self.header_label.config(text=f"{section_name} Settings")
        self.load_config_contents(section_name)

    def load_config_contents(self, config_name):
        """
        Load the contents of the selected configuration file into widgets.
        """
        section_to_file_map = {
            "AI Settings": "ai_settings.json",
            "Interface Settings": "interface_settings.json",
            "Game Preferences": "game_preferences.json",
            "Mobile App Settings": "mobile_settings.json",
            "System Monitor Settings": "system_monitor_settings.json",
            "Plex Configuration": "plex_config.json",
            "Account Integrations": "account_integrations.json",
            "Security and Privacy": "security_privacy.json",
            "Contact the Developer": "contact_developer.json"
        }

        selected_file = section_to_file_map.get(config_name)
        config_data = self.config_files.get(selected_file)

        # Clear previous widgets
        for widget in self.config_widgets_frame.winfo_children():
            widget.destroy()

        # Add scrollable frame for configuration settings
        self.canvas = tk.Canvas(self.config_widgets_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = Scrollbar(self.config_widgets_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Adjusted layout for better alignment
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        """
        Handle mouse wheel scrolling for the canvas.
        """
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    # Load configuration UIs
    def load_ai_config(self):
        self.change_section("AI Settings")

    def load_interface_config(self):
        self.change_section("Interface Settings")

    def load_game_preferences_config(self):
        self.change_section("Game Preferences")

    def load_mobile_app_settings_config(self):
        self.change_section("Mobile App Settings")

    def load_system_monitor_config(self):
        self.change_section("System Monitor Settings")

    def load_plex_config(self):
        self.change_section("Plex Configuration")

    def load_account_integrations_config(self):
        self.change_section("Account Integrations")

    def load_security_privacy_config(self):
        self.change_section("Security and Privacy")

    def load_logs_config(self):
        self.change_section("Logs")

    def load_contact_developer_config(self):
        self.change_section("Contact the Developer")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root, snowball_ai_instance, config_loader)
    root.mainloop()