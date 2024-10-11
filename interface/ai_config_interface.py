import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk, filedialog, Scale

class AIConfig:
    def __init__(self, master, config_loader):
        self.master = master
        self.config_loader = config_loader

        # Load current settings or use defaults
        self.config = config_loader.load_config("ai_settings.json") or self.default_settings()

        # Create widgets for AI settings
        self.create_widgets()

    def default_settings(self):
        return {
            "enabled": True,
            "learning_rate": 0.01,
            "dynamic_learning_rate": False,
            "learning_rate_decay": 0.001,
            "training_mode": "supervised",
            "optimizer": "Adam",
            "training_data_path": "S:/Snowball/data/training_dataset",
            # Add more default settings as needed
        }

    def create_widgets(self):
        tk.Label(self.master, text="AI Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Enable AI Checkbox
        self.enabled_var = BooleanVar(value=self.config.get("enabled", True))
        tk.Checkbutton(self.master, text="Enable AI", variable=self.enabled_var, bg="#2c2c2c", fg="white").pack(anchor="w")

        # Dynamic Learning Rate
        self.dynamic_learning_rate_var = BooleanVar(value=self.config.get("dynamic_learning_rate", False))
        dynamic_learning_rate_checkbox = tk.Checkbutton(self.master, text="Dynamic Learning Rate", variable=self.dynamic_learning_rate_var,
                                                        bg="#2c2c2c", fg="white", command=self.toggle_dynamic_learning_rate)
        dynamic_learning_rate_checkbox.pack(anchor="w", pady=5)

        # Learning Rate Slider
        self.learning_rate_slider = Scale(self.master, from_=0.001, to=1.0, resolution=0.001, orient="horizontal",
                                          label="Learning Rate", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c",
                                          troughcolor="#ffffff")
        self.learning_rate_slider.set(self.config.get("learning_rate", 0.01))
        self.learning_rate_slider.pack(fill=tk.X, padx=5, pady=5)

        # Learning Rate Decay Slider
        self.learning_rate_decay_slider = Scale(self.master, from_=0.001, to=0.1, resolution=0.001, orient="horizontal",
                                                label="Learning Rate Decay", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c",
                                                troughcolor="#ffffff")
        self.learning_rate_decay_slider.set(self.config.get("learning_rate_decay", 0.001))
        self.learning_rate_decay_slider.pack(fill=tk.X, padx=5, pady=5)

        # Training Mode Selection
        self.training_mode_var = StringVar(value=self.config.get("training_mode", "supervised"))
        training_mode_frame = tk.Frame(self.master, bg="#2c2c2c")
        training_mode_frame.pack(anchor="w", pady=5)

        supervised_button = tk.Button(training_mode_frame, text="Supervised", font=("Arial", 12), fg="white", bg="#4d4d4d",
                                      relief="sunken" if self.training_mode_var.get() == "supervised" else "raised",
                                      command=lambda: self.set_training_mode("supervised"))
        supervised_button.pack(side=tk.LEFT, padx=5)

        unsupervised_button = tk.Button(training_mode_frame, text="Unsupervised", font=("Arial", 12), fg="white", bg="#4d4d4d",
                                        relief="sunken" if self.training_mode_var.get() == "unsupervised" else "raised",
                                        command=lambda: self.set_training_mode("unsupervised"))
        unsupervised_button.pack(side=tk.LEFT, padx=5)

        self.training_mode_buttons = {"supervised": supervised_button, "unsupervised": unsupervised_button}

        # Optimizer Selection
        optimizer_label = tk.Label(self.master, text="Optimizer", font=("Arial", 12), fg="white", bg="#2c2c2c")
        optimizer_label.pack(anchor="w")
        optimizer_options = ["Adam", "SGD", "RMSProp", "Adagrad"]
        self.optimizer_combobox = ttk.Combobox(self.master, values=optimizer_options, font=("Arial", 10))
        self.optimizer_combobox.set(self.config.get("optimizer", "Adam"))
        self.optimizer_combobox.pack(fill=tk.X, padx=5, pady=5)

        # Training Data Path
        training_data_label = tk.Label(self.master, text="Training Data Path", font=("Arial", 12), fg="white", bg="#2c2c2c")
        training_data_label.pack(anchor="w")
        self.training_data_entry = tk.Entry(self.master, font=("Arial", 10), bg="#4d4d4d", fg="white")
        self.training_data_entry.insert(0, self.config.get("training_data_path", "S:/Snowball/data/training_dataset"))
        self.training_data_entry.pack(fill=tk.X, padx=5, pady=5)

        browse_button = tk.Button(self.master, text="Browse", command=self.browse_for_path, font=("Arial", 10), bg="#4d4d4d", fg="white")
        browse_button.pack(anchor="w", padx=5, pady=5)

    def set_training_mode(self, mode):
        self.training_mode_var.set(mode)
        for mode_key, button in self.training_mode_buttons.items():
            button.configure(relief="sunken" if mode_key == mode else "raised")

    def toggle_dynamic_learning_rate(self):
        is_dynamic = self.dynamic_learning_rate_var.get()
        self.learning_rate_slider.configure(state="disabled" if is_dynamic else "normal")
        self.learning_rate_decay_slider.configure(state="disabled" if is_dynamic else "normal")

    def browse_for_path(self):
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.training_data_entry.delete(0, tk.END)
            self.training_data_entry.insert(0, selected_path)
