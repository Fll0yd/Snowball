import tkinter as tk
from tkinter import ttk, colorchooser

class InterfaceConfig:
    def __init__(self, master, config_loader):
        self.master = master
        self.config_loader = config_loader

        # Load current settings or use defaults
        self.config = config_loader.load_config("interface_settings.json") or self.default_settings()

        # Create widgets for Interface settings
        self.create_widgets()

    def default_settings(self):
        return {
            "ui_theme": "Light",
            "font": {
                "font_style": "Arial",
                "font_size": 16
            },
            "color_scheme": {
                "background_color": "#e6e6e6",
                "primary_button_color": "#4d4d4d",
                "secondary_button_color": "#1e1e1e",
                "text_color": "white"
            }
        }

    def create_widgets(self):
        tk.Label(self.master, text="Interface Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # UI Theme
        theme_label = tk.Label(self.master, text="UI Theme:", font=("Arial", 12), fg="white", bg="#2c2c2c")
        theme_label.pack(anchor="w")
        theme_options = ["Light", "Dark", "Blue"]
        self.theme_combobox = ttk.Combobox(self.master, values=theme_options, font=("Arial", 10))
        self.theme_combobox.set(self.config.get("ui_theme", "Light"))
        self.theme_combobox.pack(anchor="w", padx=5, pady=5)

        # Font Style and Size
        font_label = tk.Label(self.master, text="Font Style and Size", font=("Arial", 12), fg="white", bg="#2c2c2c")
        font_label.pack(anchor="w")
        font_styles = ["Arial", "Courier", "Times New Roman", "Verdana"]
        self.font_style_combobox = ttk.Combobox(self.master, values=font_styles, font=("Arial", 10))
        self.font_style_combobox.set(self.config["font"].get("font_style", "Arial"))
        self.font_style_combobox.pack(fill=tk.X, padx=5, pady=5)

        font_sizes = [8, 10, 12, 14, 16, 18, 20]
        self.font_size_combobox = ttk.Combobox(self.master, values=font_sizes, font=("Arial", 10))
        self.font_size_combobox.set(self.config["font"].get("font_size", 16))
        self.font_size_combobox.pack(fill=tk.X, padx=5, pady=5)

        # Color Scheme
        color_keys = ["background_color", "primary_button_color", "secondary_button_color", "text_color"]
        for color_key in color_keys:
            color_label = tk.Label(self.master, text=color_key.replace("_", " ").title(), font=("Arial", 12), fg="white", bg="#2c2c2c")
            color_label.pack(anchor="w", padx=5, pady=5)

            color_value = self.config["color_scheme"].get(color_key, "#ffffff")
            color_entry = tk.Entry(self.master, font=("Arial", 10), bg="#4d4d4d", fg="white")
            color_entry.insert(0, color_value)
            color_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)

            def choose_color(entry_widget=color_entry):
                color_code = colorchooser.askcolor(title="Choose color")[1]
                if color_code:
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, color_code)

            color_button = tk.Button(self.master, text="Choose", command=choose_color, font=("Arial", 10), bg="#4d4d4d", fg="white")
            color_button.pack(side=tk.LEFT, padx=5)

