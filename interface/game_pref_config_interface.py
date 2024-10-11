import tkinter as tk
from tkinter import ttk, BooleanVar, Scale, messagebox
import json
import os

class GamePreferencesConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")
        self.config_path = 'S:/Snowball/config/game_preferences.json'

        # Load current settings or use defaults
        self.config = self.load_config() or self.default_settings()

        # Create widgets for Game Preferences settings
        self.create_widgets()

    def load_config(self):
        """
        Load the game preferences configuration file.
        """
        try:
            with open(self.config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "game_preferences.json not found. Using default settings.")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error reading game_preferences.json. Please check the file format.")
            return None

    def default_settings(self):
        """
        Default game preferences settings.
        """
        return {
            "difficulty_level": 1,
            "enable_power_ups": True,
            "max_enemies": 10,
            "game_speed": 5,
            "graphics_quality": "High"
        }

    def create_widgets(self):
        """
        Create and display widgets for modifying game preferences settings.
        """
        tk.Label(self.master, text="Game Preferences Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Create a frame for settings
        settings_frame = tk.Frame(self.master, bg="#2c2c2c")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Difficulty Level Slider
        self.difficulty_var = tk.IntVar(value=self.config.get("difficulty_level", 1))
        self.create_slider(settings_frame, "Difficulty Level", self.difficulty_var, 1, 5)

        # Enable Power-Ups Checkbox
        self.power_ups_var = BooleanVar(value=self.config.get("enable_power_ups", True))
        self.create_checkbox(settings_frame, "Enable Power-Ups", self.power_ups_var)

        # Max Enemies Slider
        self.max_enemies_var = tk.IntVar(value=self.config.get("max_enemies", 10))
        self.create_slider(settings_frame, "Max Enemies", self.max_enemies_var, 1, 50)

        # Game Speed Slider
        self.game_speed_var = tk.IntVar(value=self.config.get("game_speed", 5))
        self.create_slider(settings_frame, "Game Speed", self.game_speed_var, 1, 10)

        # Graphics Quality Dropdown
        self.graphics_quality_var = tk.StringVar(value=self.config.get("graphics_quality", "High"))
        self.create_dropdown(settings_frame, "Graphics Quality", self.graphics_quality_var, ["Low", "Medium", "High"])

        # Save Button
        save_button = tk.Button(self.master, text="Save Changes", command=self.save_changes, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=10)

    def create_slider(self, parent, label, variable, min_val, max_val):
        """
        Create a slider for numeric settings.
        """
        frame = tk.LabelFrame(parent, text=label, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
        frame.pack(fill=tk.X, pady=5)
        slider = Scale(frame, from_=min_val, to=max_val, orient="horizontal", variable=variable, bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#5e5e5e")
        slider.pack(fill=tk.X, padx=5)

    def create_checkbox(self, parent, label, variable):
        """
        Create a checkbox for boolean settings.
        """
        frame = tk.Frame(parent, bg="#2c2c2c")
        frame.pack(fill=tk.X, pady=5)
        checkbox = tk.Checkbutton(frame, text=label, variable=variable, bg="#2c2c2c", fg="white", font=("Arial", 12), selectcolor="#4d4d4d")
        checkbox.pack(anchor='w', padx=5)

    def create_dropdown(self, parent, label, variable, options):
        """
        Create a dropdown menu for selecting from a list of options.
        """
        frame = tk.LabelFrame(parent, text=label, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
        frame.pack(fill=tk.X, pady=5)
        combobox = ttk.Combobox(frame, textvariable=variable, values=options, font=("Arial", 10))
        combobox.pack(fill=tk.X, padx=5)

    def save_changes(self):
        """
        Save the changes made to the configuration file.
        """
        updated_config = {
            "difficulty_level": self.difficulty_var.get(),
            "enable_power_ups": self.power_ups_var.get(),
            "max_enemies": self.max_enemies_var.get(),
            "game_speed": self.game_speed_var.get(),
            "graphics_quality": self.graphics_quality_var.get()
        }

        try:
            with open(self.config_path, 'w') as file:
                json.dump(updated_config, file, indent=4)
            messagebox.showinfo("Success", "Game preferences saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GamePreferencesConfig(root)
    root.mainloop()