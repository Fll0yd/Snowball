import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, PhotoImage, BooleanVar, Scale
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

        # Initialize the window
        self.master.geometry("1300x900")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")

        # Add the tray icon
        self.master.iconphoto(False, PhotoImage(file="S:/Snowball/icon/trayicon.png"))
        self.ai_instance = ai_instance
        self.config_loader = config_loader

        # Sidebar setup
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)

        # Configure grid weights to make the sidebar fill the vertical space
        self.master.grid_columnconfigure(0, weight=0)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Create a frame for the main content
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)

        # Add header label to indicate the current section
        self.header_label = tk.Label(self.main_frame, text="", font=("Arial", 24, "bold"), fg="white", bg="#2c2c2c")
        self.header_label.grid(row=0, column=0, sticky="nw", pady=(0, 10))

        # Scrollable canvas for configuration content
        self.canvas = tk.Canvas(self.main_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        # Link the scrollable frame to the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1020)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Configure grid to allow expansion
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Add scrolling with the mouse wheel (cross-platform solution)
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        # This will help make sure all new widgets are added to the scrollable frame
        self.config_widgets_frame = self.scrollable_frame

        # Add Save and Apply Button at the bottom of the main_frame
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

        # Sidebar options
        sidebar_options = [
            ("AI Settings", AIConfig),
            ("Interface Settings", InterfaceConfig),
            ("Game Preferences", GamePreferencesConfig),
            ("Mobile App Settings", MobileAppSettingsConfig),
            ("System Monitor Settings", SystemMonitorConfig),
            ("Plex Configuration", PlexConfig),
            ("Account Integrations", AccountIntegrationsConfig),
            ("Security and Privacy", SecurityPrivacyConfig),
            ("Logs", LogsConfig),
            ("Contact the Developer", ContactDeveloperConfig)
        ]

        # Create buttons dynamically and place them using grid layout
        for i, (label, config_class) in enumerate(sidebar_options):
            button = tk.Button(self.sidebar_frame, text=label,
                               command=lambda c=config_class, l=label: self.change_section(l, c),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20, height=2)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

        # Load the default section (first one in sidebar)
        self.change_section("AI Settings", AIConfig)

    def _on_mouse_wheel(self, event):
        """
        Handle mouse wheel scrolling for the canvas. Adjusting for cross-platform consistency.
        """
        if event.num == 5 or event.delta == -120 or event.delta == -1:  # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120 or event.delta == 1:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
    
    def change_section(self, section_name, interface_class):
        """
        Update the header label and load the corresponding configuration interface.
        """
        # Update header label
        self.header_label.config(text=section_name)

        # Clear all existing widgets in the config_widgets_frame to avoid duplicates
        for widget in self.config_widgets_frame.winfo_children():
            widget.destroy()

        # Create the interface for the selected section
        interface = interface_class(self.config_widgets_frame, self.config_loader)

    def save_and_apply_config(self):
        """
        Save changes made to the selected configuration file and apply the changes in real time.
        """
        selected_header = self.header_label.cget("text").replace(" Settings", "").strip()

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

        if not selected_file:
            messagebox.showerror("Error", f"Configuration file '{selected_file}' does not exist or was not loaded properly.")
            return

        updated_config = {}
        # Collect data from UI widgets
        for widget in self.config_widgets_frame.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                key = widget.cget("text").replace(' ', '_').lower()
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
            # Save the configuration to file
            config_path = f'S:/Snowball/config/{selected_file}'
            with open(config_path, 'w') as f:
                json.dump(updated_config, f, indent=4)
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

    def default_settings(self, section_name):
        """
        Get the default settings for the given configuration section.
        """
        # Normalize section_name to ensure it matches the dictionary keys
        section_name = section_name.strip().lower()

        section_to_class_map = {
            "ai settings": AIConfig,
            "interface settings": InterfaceConfig,
            "game preferences": GamePreferencesConfig,
            "mobile app settings": MobileAppSettingsConfig,
            "system monitor settings": SystemMonitorConfig,
            "plex configuration": PlexConfig,
            "account integrations": AccountIntegrationsConfig,
            "security and privacy": SecurityPrivacyConfig,
            "logs": LogsConfig,
            "contact the developer": ContactDeveloperConfig
        }

        # Get the class corresponding to the normalized section name
        config_class = section_to_class_map.get(section_name)

        if not config_class:
            raise ValueError(f"No configuration class found for section '{section_name}'")

        # Instantiate the class temporarily to get default settings
        temp_instance = config_class(self.master, self.config_loader)
        return temp_instance.default_settings()

    def reset_to_defaults(self):
        """
        Reset the selected section to its default values.
        """
        selected_header = self.header_label.cget("text").replace(" Settings", "").strip()

        try:
            default_values = self.default_settings(selected_header)

            # Clear previous widgets to avoid duplication
            for widget in self.config_widgets_frame.winfo_children():
                widget.destroy()

            # Load default values into the UI
            self.create_widgets_from_config(default_values)

            messagebox.showinfo("Defaults Restored", f"Settings for '{selected_header}' have been restored to their default values.")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while resetting to defaults: {e}")

    def create_widgets_from_config(self, config):
        """
        Create widgets from a given configuration dictionary.
        """
        self.widgets = {}

        for key, value in config.items():
            formatted_key = key.replace('_', ' ').title()

            # Set the border color to white
            setting_frame = tk.LabelFrame(self.config_widgets_frame, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c",
                                          labelanchor='nw', bd=2, relief="solid")
            setting_frame.pack(fill=tk.X, padx=5, pady=5)

            if isinstance(value, bool):
                var = BooleanVar(value=value)
                checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10),
                                          selectcolor="#4d4d4d", command=self.toggle_dynamic_learning_rate if key == "dynamic_learning_rate" else None)
                checkbox.var = var
                checkbox.pack(side=tk.LEFT, padx=5, anchor='w')
                setting_frame.children['input'] = checkbox
                self.widgets[key] = checkbox

            elif isinstance(value, int) or isinstance(value, float):
                slider = Scale(setting_frame, from_=0, to=1, resolution=0.001, orient="horizontal",
                               bg="#2c2c2c", fg="white", troughcolor="white")
                slider.set(value)
                slider.pack(fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = slider
                self.widgets[key] = slider

            elif isinstance(value, str):
                entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                entry.insert(0, value)
                entry.pack(fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = entry
                self.widgets[key] = entry

            # Add description for each setting
            description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10),
                                         fg="#a9a9a9", bg="#2c2c2c", anchor='w')
            description_label.pack(anchor='w', padx=5)

    def load_ai_config(self):
        self.change_section("AI Settings", AIConfig)

    def load_interface_config(self):
        self.change_section("Interface Settings", InterfaceConfig)

    def load_game_preferences_config(self):
        self.change_section("Game Preferences", GamePreferencesConfig)

    def load_mobile_app_settings_config(self):
        self.change_section("Mobile App Settings", MobileAppSettingsConfig)

    def load_system_monitor_config(self):
        self.change_section("System Monitor Settings", SystemMonitorConfig)

    def load_plex_config(self):
        self.change_section("Plex Configuration", PlexConfig)

    def load_account_integrations_config(self):
        self.change_section("Account Integrations", AccountIntegrationsConfig)

    def load_security_privacy_config(self):
        self.change_section("Security and Privacy", SecurityPrivacyConfig)

    def load_logs_config(self):
        self.change_section("Logs", LogsConfig)

    def load_contact_developer_config(self):
        self.change_section("Contact the Developer", ContactDeveloperConfig)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root, snowball_ai_instance, config_loader)
    root.mainloop()