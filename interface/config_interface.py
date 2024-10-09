import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

# Assuming 'core' is in the parent directory of the current script
core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../core'))
sys.path.insert(0, core_path)

try:
    from config_loader import ConfigLoader
except ModuleNotFoundError:
    messagebox.showerror("Error", "ConfigLoader module not found. Please ensure the core directory is in the correct location.")

class ConfigInterface:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1000x700")
        self.master.title("Snowball Configuration")
        self.master.configure(bg="#2c2c2c")

        # Load consolidated configuration files into a dictionary
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

        # Display selected config content
        self.config_text = tk.Text(self.main_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#3e3e3e", fg="white", relief="flat")
        self.config_text.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Save Button
        self.save_button = tk.Button(self.main_frame, text="Save Changes", command=self.save_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        self.save_button.pack(anchor="e", pady=10)

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
                config_data = ConfigLoader.load_config(file_name)
                self.config_files[file_name] = config_data
            except FileNotFoundError:
                self.config_files[file_name] = None  # File not found
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Error reading JSON from {file_name}. Please check the file.")

    def load_config_contents(self, config_name):
        """
        Load the contents of the selected configuration file into the text box.
        """
        # Define the mapping between section name and actual filenames
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

        # Get the correct filename based on the selected section
        selected_file = section_to_file_map.get(config_name)

        # Retrieve the loaded configuration data
        config_data = self.config_files.get(selected_file)

        if config_data is not None:
            config_json = json.dumps(config_data, indent=4)
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(tk.END, config_json)
        else:
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(tk.END, "No configuration file available.")

    def save_config(self):
        """
        Save changes made to the selected configuration file.
        """
        selected_header = self.header_label.cget("text").replace(" Settings", "")
        selected_file = selected_header.lower().replace(" ", "_") + ".json"
        if selected_file in self.config_files:
            try:
                updated_config = json.loads(self.config_text.get(1.0, tk.END))
                config_path = f'S:/Snowball/config/{selected_file}'
                with open(config_path, 'w') as f:
                    json.dump(updated_config, f, indent=4)
                self.config_files[selected_file] = updated_config
                messagebox.showinfo("Success", f"Configuration file '{selected_file}' saved successfully.")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format. Please correct the format and try again.")
            except IOError:
                messagebox.showerror("Error", f"Unable to save changes to {selected_file}. Check permissions.")

    def change_section(self, section_name):
        """
        Update the header label and load the corresponding configuration file.
        """
        if section_name == "Logs":
            self.header_label.config(text="Logs")
            self.config_text.pack_forget()  # Hide the config text box
            self.save_button.pack_forget()  # Hide the save button
            self.display_log_buttons()
        else:
            self.header_label.config(text=f"{section_name} Settings")
            self.config_text.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
            self.save_button.pack(anchor="e", pady=10)
            self.load_config_contents(section_name)
            if hasattr(self, 'log_buttons_frame'):
                self.log_buttons_frame.pack_forget()  # Hide log buttons if they are displayed

    def display_log_buttons(self):
        """
        Display buttons for each log file available, arranged in two rows of three.
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
            "Memory Log": "system_health_logs/memory_log.txt"
        }

        # Rearrange buttons into two rows of three
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
                self.config_text.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
                self.save_button.pack_forget()  # Hide the save button when viewing logs
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(tk.END, log_content)
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: '{full_path}'")
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: '{full_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigInterface(root)
    root.mainloop()
