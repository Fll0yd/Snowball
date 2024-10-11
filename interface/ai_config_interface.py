import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, IntVar, ttk, messagebox, Scrollbar, filedialog, colorchooser

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
            "daily_training_sessions": 2,
            "training_mode": "supervised",
            "epoch_count": 50,
            "batch_size": 32,
            "training_data_path": "S:/Snowball/data/training_dataset",
            "optimizer": "Adam",
            "personality_mode": "friendly",
            "performance_tracking": True,
            "save_training_logs": True,
            "auto_learning_mode": False,
            "privacy_protection_enabled": True
        }

    def create_widgets(self):
        # Add a scrollable frame
        canvas = tk.Canvas(self.master, bg="#2c2c2c")
        scrollbar = Scrollbar(self.master, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c2c2c")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * int((event.delta / 120)), "units"))

        # Add AI settings widgets to the scrollable frame
        tk.Label(scrollable_frame, text="AI Settings", font=("Arial", 16), fg="white", bg="#2c2c2c").pack(anchor="nw", pady=10)

        # Enable AI Checkbox
        self.enabled_var = BooleanVar(value=self.config.get("enabled", True))
        tk.Checkbutton(scrollable_frame, text="Enable AI", variable=self.enabled_var, bg="#2c2c2c", fg="white").pack(anchor="w")
        tk.Label(scrollable_frame, text="Enable or disable the AI.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Dynamic Learning Rate Checkbox
        self.dynamic_learning_rate_var = BooleanVar(value=self.config.get("dynamic_learning_rate", False))
        dynamic_learning_rate_checkbox = tk.Checkbutton(scrollable_frame, text="Dynamic Learning Rate", variable=self.dynamic_learning_rate_var,
                                                        bg="#2c2c2c", fg="white", command=self.toggle_dynamic_learning_rate)
        dynamic_learning_rate_checkbox.pack(anchor="w", pady=5)
        tk.Label(scrollable_frame, text="Allow the AI to adjust its learning rate dynamically.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Learning Rate Slider
        self.learning_rate_slider = Scale(scrollable_frame, from_=0.001, to=1.0, resolution=0.001, orient="horizontal",
                                          label="Learning Rate", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c",
                                          troughcolor="#ffffff")
        self.learning_rate_slider.set(self.config.get("learning_rate", 0.01))
        self.learning_rate_slider.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Set the learning rate for the AI's training process.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Learning Rate Decay Slider
        self.learning_rate_decay_slider = Scale(scrollable_frame, from_=0.001, to=0.1, resolution=0.001, orient="horizontal",
                                                label="Learning Rate Decay", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c",
                                                troughcolor="#ffffff")
        self.learning_rate_decay_slider.set(self.config.get("learning_rate_decay", 0.001))
        self.learning_rate_decay_slider.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Specify the rate at which the learning rate should decrease over time.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Daily Training Sessions
        self.daily_training_sessions_var = IntVar(value=self.config.get("daily_training_sessions", 2))
        tk.Label(scrollable_frame, text="Daily Training Sessions", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w")
        tk.Spinbox(scrollable_frame, from_=1, to=10, textvariable=self.daily_training_sessions_var, width=5).pack(anchor="w", padx=5, pady=5)
        tk.Label(scrollable_frame, text="Number of training sessions the AI should complete each day.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Epoch Count
        self.epoch_count_var = IntVar(value=self.config.get("epoch_count", 50))
        tk.Label(scrollable_frame, text="Epoch Count", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w")
        tk.Spinbox(scrollable_frame, from_=1, to=1000, textvariable=self.epoch_count_var, width=5).pack(anchor="w", padx=5, pady=5)
        tk.Label(scrollable_frame, text="Number of epochs (iterations) for training the AI model.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Batch Size
        self.batch_size_var = IntVar(value=self.config.get("batch_size", 32))
        tk.Label(scrollable_frame, text="Batch Size", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w")
        tk.Spinbox(scrollable_frame, from_=1, to=256, textvariable=self.batch_size_var, width=5).pack(anchor="w", padx=5, pady=5)
        tk.Label(scrollable_frame, text="Size of the batch used during training sessions.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Training Data Path
        tk.Label(scrollable_frame, text="Training Data Path", font=("Arial", 12), fg="white", bg="#2c2c2c").pack(anchor="w")
        self.training_data_entry = tk.Entry(scrollable_frame, font=("Arial", 10), bg="#4d4d4d", fg="white")
        self.training_data_entry.insert(0, self.config.get("training_data_path", "S:/Snowball/data/training_dataset"))
        self.training_data_entry.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(scrollable_frame, text="📁", command=self.browse_for_path, font=("Arial", 10), bg="#4d4d4d", fg="white").pack(anchor="w", padx=5, pady=5)
        tk.Label(scrollable_frame, text="Path to the training dataset for the AI.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Performance Tracking Checkbox
        self.performance_tracking_var = BooleanVar(value=self.config.get("performance_tracking", True))
        tk.Checkbutton(scrollable_frame, text="Enable Performance Tracking", variable=self.performance_tracking_var, bg="#2c2c2c", fg="white").pack(anchor="w", pady=5)
        tk.Label(scrollable_frame, text="Enable tracking of AI performance metrics.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Save Training Logs Checkbox
        self.save_training_logs_var = BooleanVar(value=self.config.get("save_training_logs", True))
        tk.Checkbutton(scrollable_frame, text="Save Training Logs", variable=self.save_training_logs_var, bg="#2c2c2c", fg="white").pack(anchor="w", pady=5)
        tk.Label(scrollable_frame, text="Save logs related to the training process.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Auto Learning Mode Checkbox
        self.auto_learning_mode_var = BooleanVar(value=self.config.get("auto_learning_mode", False))
        tk.Checkbutton(scrollable_frame, text="Enable Auto Learning Mode", variable=self.auto_learning_mode_var, bg="#2c2c2c", fg="white").pack(anchor="w", pady=5)
        tk.Label(scrollable_frame, text="Enable or disable automatic learning from interactions.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Privacy Protection Checkbox
        self.privacy_protection_var = BooleanVar(value=self.config.get("privacy_protection_enabled", True))
        tk.Checkbutton(scrollable_frame, text="Enable Privacy Protection", variable=self.privacy_protection_var, bg="#2c2c2c", fg="white").pack(anchor="w", pady=5)
        tk.Label(scrollable_frame, text="Enable protection of user privacy during AI operations.", font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c").pack(anchor="w")

        # Reset to Default Button
        reset_button = tk.Button(scrollable_frame, text="Reset to Default Settings", command=self.reset_to_defaults, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        reset_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=10)

        # Save and Apply Button
        save_button = tk.Button(scrollable_frame, text="Save and Apply Changes", command=self.save_changes, bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat")
        save_button.pack(side=tk.RIGHT, anchor="e", pady=10, padx=10)

    def toggle_dynamic_learning_rate(self):
        is_dynamic = self.dynamic_learning_rate_var.get()
        if is_dynamic:
            self.learning_rate_slider.set(self.default_settings()["learning_rate"])
            self.learning_rate_decay_slider.set(self.default_settings()["learning_rate_decay"])
            self.learning_rate_slider.configure(state="disabled", troughcolor="#5e5e5e")
            self.learning_rate_decay_slider.configure(state="disabled", troughcolor="#5e5e5e")
        else:
            self.learning_rate_slider.configure(state="normal", troughcolor="#ffffff")
            self.learning_rate_decay_slider.configure(state="normal", troughcolor="#ffffff")

    def browse_for_path(self):
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.training_data_entry.delete(0, tk.END)
            self.training_data_entry.insert(0, selected_path)

    def reset_to_defaults(self):
        default_values = self.default_settings()
        self.enabled_var.set(default_values["enabled"])
        self.learning_rate_slider.set(default_values["learning_rate"])
        self.dynamic_learning_rate_var.set(default_values["dynamic_learning_rate"])
        self.learning_rate_decay_slider.set(default_values["learning_rate_decay"])
        self.daily_training_sessions_var.set(default_values["daily_training_sessions"])
        self.epoch_count_var.set(default_values["epoch_count"])
        self.batch_size_var.set(default_values["batch_size"])
        self.training_data_entry.delete(0, tk.END)
        self.training_data_entry.insert(0, default_values["training_data_path"])
        self.performance_tracking_var.set(default_values["performance_tracking"])
        self.save_training_logs_var.set(default_values["save_training_logs"])
        self.auto_learning_mode_var.set(default_values["auto_learning_mode"])
        self.privacy_protection_var.set(default_values["privacy_protection_enabled"])
        self.toggle_dynamic_learning_rate()

    def save_changes(self):
        # Save changes to the configuration file
        updated_config = {
            "enabled": self.enabled_var.get(),
            "learning_rate": self.learning_rate_slider.get(),
            "dynamic_learning_rate": self.dynamic_learning_rate_var.get(),
            "learning_rate_decay": self.learning_rate_decay_slider.get(),
            "daily_training_sessions": self.daily_training_sessions_var.get(),
            "epoch_count": self.epoch_count_var.get(),
            "batch_size": self.batch_size_var.get(),
            "training_data_path": self.training_data_entry.get(),
            "performance_tracking": self.performance_tracking_var.get(),
            "save_training_logs": self.save_training_logs_var.get(),
            "auto_learning_mode": self.auto_learning_mode_var.get(),
            "privacy_protection_enabled": self.privacy_protection_var.get()
        }
        # Save the updated config to file
        self.config_loader.save_config("ai_settings.json", updated_config)
        messagebox.showinfo("Success", "AI settings saved successfully.")