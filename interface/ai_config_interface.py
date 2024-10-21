import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, ttk, filedialog, messagebox

class AIConfig:
    def __init__(self, master, config_loader):
        self.master = master
        self.master.configure(bg="#2c2c2c")
        self.config_loader = config_loader
        self.training_mode_buttons = {}

        # Load current settings or use defaults
        self.config = config_loader.load_config("ai_settings.json") or self.default_settings()

        # Create widgets for AI settings
        self.create_widgets()

        # Display frame for config widgets
        self.config_widgets_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.config_widgets_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

    def create_widgets(self):
        # Create a scrollable frame for all settings
        self.widgets = {}

        # Variables to store references to sliders and checkbox
        self.training_mode_var = StringVar(value=self.config.get("training_mode", "supervised").lower())

        if self.config is not None:
            # Dynamically create widgets based on the JSON structure
            for key, value in self.config.items():
                formatted_key = key.replace('_', ' ').title()

                # Create a LabelFrame for each setting
                setting_frame = tk.LabelFrame(self.master, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
                setting_frame.pack(fill=tk.X, pady=5, padx=10, expand=True)

                # Create widgets for different settings
                if key == "enabled":
                    var = BooleanVar(value=value)
                    checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
                    checkbox.var = var
                    checkbox.grid(row=0, column=0, sticky="w", padx=5)
                    self.widgets[key] = checkbox

                    # Add description to the right of the checkbox, closer to the checkbox
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.grid(row=0, column=1, sticky="w", padx=5)

                elif key == "dynamic_learning_rate":
                    var = BooleanVar(value=value)
                    checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d", command=self.toggle_dynamic_learning_rate)
                    checkbox.var = var
                    checkbox.grid(row=0, column=0, sticky="w", padx=5)
                    self.widgets[key] = checkbox
                    self.dynamic_learning_rate_checkbox = var

                    # Add description to the right of the checkbox, closer to the checkbox
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.grid(row=0, column=1, sticky="w", padx=5)

                elif key in ["learning_rate", "learning_rate_decay"]:
                    slider = Scale(setting_frame, from_=0.001, to=1.0, resolution=0.001, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#5e5e5e", state="normal")
                    slider.set(value)
                    slider.pack(fill=tk.X, padx=5, expand=True)
                    setting_frame.children['input'] = slider
                    self.widgets[key] = slider

                    if key == "learning_rate":
                        self.learning_rate_slider = slider
                    elif key == "learning_rate_decay":
                        self.learning_rate_decay_slider = slider

                    # Add description beneath the slider inside the frame
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.pack(fill=tk.X, padx=5, pady=2)

                elif key in ["daily_training_sessions", "epoch_count", "batch_size", "memory_retention_limit", "max_consecutive_failures"]:
                    slider = Scale(setting_frame, from_=0, to=100, resolution=1, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#ffffff")
                    slider.set(value)
                    slider.pack(fill=tk.X, padx=5, expand=True)
                    setting_frame.children['input'] = slider
                    self.widgets[key] = slider

                    # Add description beneath the slider inside the frame
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.pack(fill=tk.X, padx=5, pady=2)

                elif key == "training_mode":
                    # Create training mode buttons and add them to the frame
                    button_frame = tk.Frame(setting_frame, bg="#2c2c2c")
                    button_frame.pack(fill=tk.X, padx=5, pady=2)

                    button_supervised = tk.Button(button_frame, text="Supervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value.lower() == "supervised" else "raised",
                                                  command=lambda: self.set_training_mode("supervised"))
                    button_unsupervised = tk.Button(button_frame, text="Unsupervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value.lower() == "unsupervised" else "raised",
                                                    command=lambda: self.set_training_mode("unsupervised"))
                    button_supervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
                    button_unsupervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
                    self.training_mode_buttons["supervised"] = button_supervised
                    self.training_mode_buttons["unsupervised"] = button_unsupervised

                    # Add description beneath the buttons inside the frame
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.pack(fill=tk.X, padx=5, pady=2)

                elif key == "training_data_path":
                    entry_frame = tk.Frame(setting_frame, bg="#2c2c2c")
                    entry_frame.pack(fill=tk.X, padx=5, pady=2)

                    entry = tk.Entry(entry_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                    entry.insert(0, value)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    setting_frame.children['input'] = entry
                    button_browse = tk.Button(entry_frame, text="📁", font=("Arial", 10), command=lambda e=entry: self.browse_for_path(e), relief="flat", bg="#4d4d4d", fg="white")
                    button_browse.pack(side=tk.LEFT, padx=5)

                    # Add description beneath the entry and button inside the frame
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.pack(fill=tk.X, padx=5, pady=2)

                elif key in ["optimizer", "model_type", "evaluation_frequency", "personality_mode", "response_speed"]:
                    dropdown_values = self.get_dropdown_options(key)
                    combobox = ttk.Combobox(setting_frame, values=[v.title() for v in dropdown_values], font=("Arial", 10))
                    combobox.set(value.title())
                    combobox.pack(fill=tk.X, padx=5, expand=True)
                    setting_frame.children['input'] = combobox
                    self.widgets[key] = combobox

                    # Add description beneath the combobox inside the frame
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.pack(fill=tk.X, padx=5, pady=2)

                elif key in ["performance_tracking", "save_training_logs", "allow_casual_conversation", "knowledge_expansion", "auto_learning", "safe_mode", "privacy_protection"]:
                    var = BooleanVar(value=value)
                    checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
                    checkbox.var = var
                    checkbox.grid(row=0, column=0, sticky="w", padx=5)
                    self.widgets[key] = checkbox

                    # Add description to the right of the checkbox, closer to the checkbox
                    description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
                    description_label.grid(row=0, column=1, sticky="w", padx=5)

    def browse_for_path(self, entry_widget):
        """
        Open file explorer to select a folder and set the path in the entry widget.
        """
        selected_path = filedialog.askdirectory()
        if selected_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_path)

    def set_training_mode(self, mode):
        """
        Set the training mode, ensuring that only one button is depressed at a time.
        """
        self.training_mode_var.set(mode)

        # Update button styles accordingly
        for mode_key, button in self.training_mode_buttons.items():
            if mode_key == mode:
                button.configure(relief="sunken")
            else:
                button.configure(relief="raised")

    def get_dropdown_options(self, key):
        """
        Return a list of dropdown options based on the given key.
        """
        options = {
            "optimizer": ["Adam", "SGD", "RMSProp", "Adagrad"],
            "model_type": ["Neural Network", "Decision Tree", "Random Forest"],
            "evaluation_frequency": ["Hourly", "Daily", "Weekly", "Bi-Weekly"],
            "personality_mode": ["Friendly", "Professional", "Humorous", "Formal"],
            "response_speed": ["Instant", "Delayed", "Normal"]
        }
        return options.get(key, [])

    def reset_to_default_settings(self):
        """Reset the current settings to the default values."""
        self.config = self.default_settings()
        self.update_widgets()
        # Trigger dynamic learning rate toggle to ensure sliders are updated correctly
        self.toggle_dynamic_learning_rate()

    def update_widgets(self):
        """Update the widgets with the new values in `self.config`."""
        for key, value in self.config.items():
            widget = self.widgets.get(key)
            
            if isinstance(widget, tk.Checkbutton):
                # Update the value of the checkbox
                widget.var.set(value)
            elif isinstance(widget, Scale):
                # Update the value of the slider
                widget.set(value)
            elif isinstance(widget, ttk.Combobox):
                # Update the combobox value
                widget.set(value.title())
            elif isinstance(widget, tk.Entry):
                # Update the entry widget
                widget.delete(0, tk.END)
                widget.insert(0, value)

        # Update training mode buttons separately
        if "training_mode" in self.config:
            mode = self.config["training_mode"].lower()
            for mode_key, button in self.training_mode_buttons.items():
                if mode_key == mode:
                    button.configure(relief="sunken")
                else:
                    button.configure(relief="raised")

    def default_settings(self):
        """Return default settings for the AI configuration."""
        return {
            "enabled": True,
            "learning_rate": 0.01,
            "dynamic_learning_rate": True,
            "learning_rate_decay": 0.001,
            "daily_training_sessions": 5,
            "training_mode": "supervised",
            "epoch_count": 50,
            "batch_size": 32,
            "training_data_path": "S:/Snowball/data/training_dataset",
            "optimizer": "Adam",
            "model_type": "Neural Network",
            "performance_tracking": True,
            "save_training_logs": True,
            "evaluation_frequency": "Daily",
            "personality_mode": "Friendly",
            "allow_casual_conversation": True,
            "response_speed": "Instant",
            "knowledge_expansion": True,
            "memory_retention_limit": 1000,
            "auto_learning": True,
            "safe_mode": True,
            "max_consecutive_failures": 3,
            "privacy_protection": True
        }

    def toggle_dynamic_learning_rate(self):
        """
        Toggle the state of learning rate sliders based on the dynamic learning rate checkbox.
        """
        if self.dynamic_learning_rate_checkbox and self.dynamic_learning_rate_checkbox.get():
            # Disable sliders, set them to default values, and change the trough color to grey
            if self.learning_rate_slider:
                self.learning_rate_slider.set(self.default_settings()["learning_rate"])
                self.learning_rate_slider.configure(state="disabled", troughcolor="#5e5e5e")
            if self.learning_rate_decay_slider:
                self.learning_rate_decay_slider.set(self.default_settings()["learning_rate_decay"])
                self.learning_rate_decay_slider.configure(state="disabled", troughcolor="#5e5e5e")
        else:
            # Enable sliders and set trough color back to white
            if self.learning_rate_slider:
                self.learning_rate_slider.configure(state="normal", troughcolor="#ffffff")
            if self.learning_rate_decay_slider:
                self.learning_rate_decay_slider.configure(state="normal", troughcolor="#ffffff")

    def get_setting_description(self, key):
        """
        Return a brief description for each setting to explain what it does.
        """
        descriptions = {
            "enabled": "Enable or disable the AI.",
            "learning_rate": "Set the learning rate for the AI's training process.",
            "dynamic_learning_rate": "Allow the AI to adjust its learning rate dynamically.",
            "learning_rate_decay": "Specify the rate at which the learning rate should decrease over time.",
            "daily_training_sessions": "Number of training sessions the AI should complete each day.",
            "training_mode": "Define the training mode (e.g., supervised, unsupervised).",
            "epoch_count": "Number of epochs (iterations) for training the AI model.",
            "batch_size": "Size of the batch used during training sessions.",
            "training_data_path": "Path to the training dataset for the AI.",
            "optimizer": "Algorithm used to optimize the AI model (e.g., Adam, SGD).",
            "model_type": "Specify the type of model used by the AI (e.g., neural network).",
            "performance_tracking": "Enable tracking of AI performance metrics.",
            "save_training_logs": "Save logs related to the training process.",
            "evaluation_frequency": "Frequency at which the AI should be evaluated (e.g., daily).",
            "personality_mode": "Set the AI's personality mode (e.g., friendly, formal).",
            "allow_casual_conversation": "Allow the AI to engage in casual conversation.",
            "response_speed": "Specify the speed at which the AI responds (e.g., instant, delayed).",
            "knowledge_expansion": "Allow the AI to continuously expand its knowledge base.",
            "memory_retention_limit": "Set the limit for how much information the AI retains.",
            "auto_learning": "Enable or disable automatic learning from interactions.",
            "safe_mode": "Ensure that the AI operates within safe boundaries.",
            "max_consecutive_failures": "Maximum number of consecutive failures allowed before taking corrective action.",
            "privacy_protection": "Enable protection of user privacy during AI operations."
        }
        return descriptions.get(key, "No description available for this setting.")
