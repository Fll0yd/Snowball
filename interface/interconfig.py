import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, IntVar, ttk, messagebox, Scrollbar, filedialog
import json
import os
import sys

# Get the base directory of the project, which should be the Snowball directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
print(f"Base path: {base_dir}")  # Debugging path reference

# Add the base directory to sys.path if it's not already in it
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Print sys.path to debug if the core directory is visible
print(f"Current sys.path: {sys.path}")

# Import ConfigLoader and SnowballAI directly from core package
try:
    from core.config_loader import ConfigLoader
    from core.ai_agent import SnowballAI
except ModuleNotFoundError as e:
    messagebox.showerror("Error", f"ConfigLoader module not found. Please ensure the core directory is in the correct location. {str(e)}")
    sys.exit(1)  # Exit the script if the required module is not found

class ConfigInterface:
    def __init__(self, master, ai_instance):
        self.master = master
        # Set the window to the larger size
        self.master.geometry("1200x800")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")
        self.ai_instance = ai_instance

        # Load consolidated configuration files into a dictionary
        self.config_loader = ConfigLoader()  # Create an instance of ConfigLoader
        self.config_files = {}
        self.load_consolidated_files()

        # Create a frame for the sidebar with grid layout
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights to stretch the sidebar evenly
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=4)
        self.master.grid_rowconfigure(0, weight=1)

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

        # Create sidebar options for different configuration sections
        sidebar_options = [
            "AI Settings",
            "Interface Settings",
            "Game Preferences",
            "Mobile App Settings",
            "System Monitor Settings",
            "Plex Configuration",
            "Account Integrations",
            "Security and Privacy",
            "Logs",
            "Contact the Developer"
        ]

        # Create buttons dynamically and place them using grid layout
        for i, option in enumerate(sidebar_options):
            button = tk.Button(self.sidebar_frame, text=option, command=lambda opt=option: self.change_section(opt),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=18)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            self.sidebar_frame.grid_rowconfigure(i, weight=1)

    def save_and_apply_config(self):
        """
        Save changes made to the selected configuration file and apply the changes in real time.
        """
        selected_header = self.header_label.cget("text").replace(" Settings", "")
        selected_file = selected_header.lower().replace(" ", "_") + ".json"
        if selected_file in self.config_files:
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
                config_path = f'S:/Snowball/config/{selected_file}'
                with open(config_path, 'w') as f:
                    json.dump(updated_config, f, indent=4)
                self.config_files[selected_file] = updated_config
                messagebox.showinfo("Success", f"Configuration file '{selected_file}' saved successfully.")

                # Apply the changes to the AI instance
                if selected_header == "AI Settings":
                    self.ai_instance.reload_ai_settings()
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format. Please correct the format and try again.")
            except IOError:
                messagebox.showerror("Error", f"Unable to save changes to {selected_file}. Check permissions.")

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
            except FileNotFoundError:
                self.config_files[file_name] = None  # File not found
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error reading JSON from {file_name}. Please check the file.")

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

        if config_data is not None:
            # Dynamically create widgets based on the JSON structure for Interface Settings
            for key, value in config_data.items():
                formatted_key = key.replace('_', ' ').title()

                setting_frame = tk.LabelFrame(self.scrollable_frame, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
                setting_frame.pack(fill=tk.X, pady=5)

                if isinstance(value, bool):
                    var = BooleanVar(value=value)
                    checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
                    checkbox.var = var
                    checkbox.pack(side=tk.LEFT, padx=5)
                    setting_frame.children['input'] = checkbox

                elif isinstance(value, int):
                    slider = Scale(setting_frame, from_=0, to=100, orient="horizontal", bg="#2c2c2c", fg="white")
                    slider.set(value)
                    slider.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = slider

                elif isinstance(value, str):
                    if key in ["response_tone", "ui_theme", "language", "voice_gender", "theme_type", "voice_variant", "response_length"]:
                        # Create a dropdown for these specific keys
                        dropdown_values = self.get_dropdown_options(key)
                        combobox = ttk.Combobox(setting_frame, values=dropdown_values, font=("Arial", 10))
                        combobox.set(value.title())
                        combobox.pack(fill=tk.X, padx=5)
                        setting_frame.children['input'] = combobox
                    else:
                        # Create an entry for other string values
                        entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                        entry.insert(0, value)
                        entry.pack(fill=tk.X, padx=5)
                        setting_frame.children['input'] = entry

                elif isinstance(value, dict):
                    # Handle nested dictionaries
                    for nested_key, nested_value in value.items():
                        nested_formatted_key = f"{formatted_key} - {nested_key.replace('_', ' ').title()}"

                        nested_setting_frame = tk.LabelFrame(self.scrollable_frame, text=nested_formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
                        nested_setting_frame.pack(fill=tk.X, pady=5)

                        if isinstance(nested_value, bool):
                            var = BooleanVar(value=nested_value)
                            checkbox = tk.Checkbutton(nested_setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
                            checkbox.var = var
                            checkbox.pack(side=tk.LEFT, padx=5)
                            nested_setting_frame.children['input'] = checkbox

                        elif isinstance(nested_value, int):
                            slider = Scale(nested_setting_frame, from_=0, to=100, orient="horizontal", bg="#2c2c2c", fg="white")
                            slider.set(nested_value)
                            slider.pack(fill=tk.X, padx=5)
                            nested_setting_frame.children['input'] = slider

                        elif isinstance(nested_value, str):
                            entry = tk.Entry(nested_setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                            entry.insert(0, nested_value)
                            entry.pack(fill=tk.X, padx=5)
                            nested_setting_frame.children['input'] = entry

                # Add description
                description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c")
                description_label.pack(side=tk.BOTTOM, anchor='w', padx=5, pady=2)

    def get_dropdown_options(self, key):
        """
        Return a list of dropdown options based on the given key.
        """
        options = {
            "response_tone": ["Casual", "Formal", "Friendly", "Humorous", "Professional"],
            "ui_theme": ["Light", "Dark", "Blue", "Green"],
            "language": ["En", "Fr", "Es", "De", "It"],
            "voice_gender": ["Male", "Female"],
            "theme_type": ["Light", "Dark"],
            "voice_variant": ["En-US-Wavenet-A", "En-US-Wavenet-B", "En-GB-Wavenet-C"],
            "response_length": ["Concise", "Detailed"]
        }
        return options.get(key, [])

    def _on_mouse_wheel(self, event):
        """
        Handle mouse wheel scrolling for the canvas.
        """
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        """
        # Placeholder for reset functionality, similar to AI Settings reset logic
        messagebox.showinfo("Defaults Restored", "All settings have been restored to their default values.")

    def get_setting_description(self, key):
        """
        Return a brief description for each setting to explain what it does.
        """
        descriptions = {
            "nickname": "The nickname Snowball should use to refer to you.",
            "response_tone": "The tone that Snowball uses in responses.",
            "response_length": "The preferred length of responses.",
            "ui_theme": "The color theme of the user interface.",
            "font": "The font settings for the UI.",
            "color_scheme": "The color scheme for different UI elements.",
            "language": "The language used for the interface.",
            "voice_gender": "The preferred gender for the AI voice.",
            "theme": "The overall theme of the application.",
            "welcome_message_enabled": "Enable or disable the welcome message on startup.",
            "avatar_preferences": "Settings for the avatar's appearance and behavior.",
            "button_preferences": "Preferences for the appearance and behavior of buttons.",
            "notification_preferences": "Notification sound and pop-up preferences.",
            "keyboard_shortcuts": "Keyboard shortcuts for common actions.",
            "gesture_controls": "Enable or disable gesture-based controls.",
            "interface_scaling": "Settings for interface scaling and DPI awareness.",
            "customization_options": "Customization settings for background and other UI elements.",
            "menu_behavior": "Settings for menu expansion and collapse behavior.",
            "dark_mode": "Enable or configure automatic dark mode.",
            "status_bar_preferences": "Preferences for displaying items in the status bar.",
            "chat_interface": "Settings for the chat interface, such as avatar visibility and message alignment.",
            "voice_interface": "Settings for the voice interaction, including volume and speech rate."
        }
        return descriptions.get(key, "No description available for this setting.")

    def change_section(self, section_name):
        """
        Update the header label and load the corresponding configuration file.
        """
        if section_name == "Logs":
            self.header_label.config(text="Logs")
            for widget in self.config_widgets_frame.winfo_children():
                widget.destroy()  # Hide the config widgets
            self.display_log_buttons()
        else:
            self.header_label.config(text=f"{section_name} Settings")
            self.load_config_contents(section_name)
            if hasattr(self, 'log_buttons_frame'):
                self.log_buttons_frame.pack_forget()  # Hide log buttons if they are displayed

    def display_log_buttons(self):
        """
        Display buttons for each log file available, arranged in rows of three.
        """
        logs_path = 'S:/Snowball/storage/logs'
        if hasattr(self, 'log_buttons_frame'):
            self.log_buttons_frame.pack_forget()  # Remove any existing log buttons frame

        self.log_buttons_frame = tk.Frame(self.main_frame, bg="#2c2c2c")
        self.log_buttons_frame.pack(pady=10)

        log_file_mapping = {
            "Decision Log": "decision_logs/decision_log.txt",
            "Error Log": "error_logs/error_log.txt",
            "Event Log": "event_logs/event_log.txt",
            "File Log": "file_io_logs/file_io_log.txt",
            "Interaction Log": "interaction_logs/interaction_log.txt",
            "CPU Log": "system_health_logs/cpu_log.txt",
            "Memory Log": "system_health_logs/memory_log.txt",
            "Config Log": "config_logs/config_log.txt",
            "Security Log": "security_logs/security_log.txt",
            "Task Log": "task_logs/task_log.txt",
            "Warning Log": "warning_logs/warning_log.txt"
        }

        # Rearrange buttons into rows of three
        row = 0
        col = 0
        for log_name, log_file in log_file_mapping.items():
            button = tk.Button(self.log_buttons_frame, text=log_name, command=lambda lf=log_file: self.load_log_file(lf),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20, pady=5)
            button.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 2:  # Create a new row after every three buttons
                col = 0
                row += 1

    def load_log_file(self, log_file):
        """
        Load the contents of the selected log file into the text box.
        """
        logs_path = 'S:/Snowball/storage/logs'
        full_path = os.path.join(logs_path, log_file)

        if not os.access(full_path, os.R_OK):
            messagebox.showerror("Error", f"Cannot read log file: '{full_path}'. Check file permissions.")
            return

        try:
            with open(full_path, 'r') as f:
                log_content = f.read()
                for widget in self.config_widgets_frame.winfo_children():
                    widget.destroy()
                self.config_widgets_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
                text_box = tk.Text(self.config_widgets_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#3e3e3e", fg="white", relief="flat")
                text_box.insert(tk.END, log_content)
                text_box.pack(fill=tk.BOTH, expand=True)
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: '{full_path}'")
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: '{full_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root, SnowballAI)
    root.mainloop()