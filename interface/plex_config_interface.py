import tkinter as tk
from tkinter import ttk, BooleanVar, filedialog, messagebox
import json
import os

class PlexConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")

        # Load Plex configuration
        self.config_path = 'S:/Snowball/config/plex_config.json'
        self.config_data = self.load_config()

        # Create the GUI layout
        self.create_widgets()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Configuration file not found: {self.config_path}")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in plex_config.json")
            return {}

    def save_config(self):
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config_data, file, indent=4)
            messagebox.showinfo("Success", "Plex configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the configuration: {e}")

    def create_widgets(self):
        # Header label
        tk.Label(self.master, text="Plex Configuration", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Scrollable frame for settings
        self.canvas = tk.Canvas(self.master, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Dynamically create widgets based on config data
        for key, value in self.config_data.items():
            formatted_key = key.replace('_', ' ').title()

            setting_frame = tk.LabelFrame(self.scrollable_frame, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
            setting_frame.pack(fill=tk.X, pady=5)

            if isinstance(value, bool):
                var = BooleanVar(value=value)
                checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d", command=lambda k=key, v=var: self.update_config(k, v.get()))
                checkbox.pack(side=tk.LEFT, padx=5)

            elif isinstance(value, int):
                slider = tk.Scale(setting_frame, from_=0, to=100, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#ffffff", command=lambda val, k=key: self.update_config(k, int(val)))
                slider.set(value)
                slider.pack(fill=tk.X, padx=5)

            elif isinstance(value, str):
                entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                entry.insert(0, value)
                entry.pack(fill=tk.X, padx=5)
                entry.bind("<FocusOut>", lambda e, k=key, w=entry: self.update_config(k, w.get()))

                if "directory" in key.lower() or "path" in key.lower():
                    folder_button = tk.Button(setting_frame, text="📁", command=lambda e=entry: self.browse_directory(e), relief="flat", bg="#4d4d4d", fg="white")
                    folder_button.pack(side=tk.LEFT, padx=5)

        # Save button
        save_button = tk.Button(self.master, text="Save Configuration", command=self.save_config, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(pady=10)

    def update_config(self, key, value):
        self.config_data[key] = value

    def browse_directory(self, entry_widget):
        selected_path = filedialog.askdirectory()
        if selected_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_path)
            entry_widget.event_generate("<FocusOut>")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = PlexConfig(root)
    root.mainloop()