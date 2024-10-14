import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, ttk, filedialog, messagebox


class AIConfig:
    def __init__(self, master, config_loader):
        self.master = master
        self.config_loader = config_loader
        self.training_mode_buttons = {}  # Add this line to initialize the dictionary

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
        self.learning_rate_slider = None
        self.learning_rate_decay_slider = None
        self.dynamic_learning_rate_checkbox = None
        self.training_mode_switch = None

        # Default values for learning rate and decay rate
        self.default_learning_rate = 0.01
        self.default_learning_rate_decay = 0.001

        # Use `self.config` instead of `config_data`
        if self.config is not None:
            # Dynamically create widgets based on the JSON structure
            for key, value in self.config.items():
                formatted_key = key.replace('_', ' ').title()

                setting_frame = tk.LabelFrame(self.master, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
                setting_frame.pack(fill=tk.X, pady=5)

                if key == "response_length":
                    options = ["Concise", "Detailed", "Balanced"]
                    combobox = ttk.Combobox(setting_frame, values=options, font=("Arial", 10))
                    
                if key == "dynamic_learning_rate":
                    var = BooleanVar(value=value)
                    checkbox = tk.Checkbutton(setting_frame, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d", command=self.toggle_dynamic_learning_rate)
                    checkbox.var = var
                    checkbox.pack(side=tk.LEFT, padx=5)
                    self.dynamic_learning_rate_checkbox = checkbox

                elif key in ["learning_rate", "learning_rate_decay"]:
                    # Create slider with a "disabled" color if dynamic learning is enabled
                    slider = Scale(setting_frame, from_=0.001, to=1.0, resolution=0.001, orient="horizontal", bg="#2c2c2c", fg="white", highlightbackground="#2c2c2c", troughcolor="#ffffff")
                    slider.set(value)
                    slider.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = slider

                    if key == "learning_rate":
                        self.learning_rate_slider = slider
                    elif key == "learning_rate_decay":
                        self.learning_rate_decay_slider = slider

                elif key == "training_mode":
                    # Create two buttons for 'Supervised' and 'Unsupervised'
                    self.training_mode_var = StringVar(value=value)

                    button_supervised = tk.Button(setting_frame, text="Supervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value == "supervised" else "raised",
                                                  command=lambda: self.set_training_mode("supervised"))
                    button_unsupervised = tk.Button(setting_frame, text="Unsupervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value == "unsupervised" else "raised",
                                                    command=lambda: self.set_training_mode("unsupervised"))

                    button_supervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
                    button_unsupervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

                    # Store references to these buttons for later updates
                    self.training_mode_buttons["supervised"] = button_supervised
                    self.training_mode_buttons["unsupervised"] = button_unsupervised

                elif key == "training_data_path":
                    entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                    entry.insert(0, value)
                    entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)
                    setting_frame.children['input'] = entry

                    # Add a button to open file explorer
                    button_browse = tk.Button(setting_frame, text="📁", font=("Arial", 10), command=lambda e=entry: self.browse_for_path(e), relief="flat", bg="#4d4d4d", fg="white")
                    button_browse.pack(side=tk.LEFT, padx=5)

                elif key == "optimizer":
                    optimizers = ["Adam", "SGD", "RMSProp", "Adagrad"]  # List of optimizers
                    combobox = ttk.Combobox(setting_frame, values=optimizers, font=("Arial", 10))
                    combobox.set(value.capitalize())
                    combobox.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = combobox

                elif key == "model_type":
                    model_types = ["Neural Network", "Decision Tree", "Random Forest"]  # List of model types
                    combobox = ttk.Combobox(setting_frame, values=model_types, font=("Arial", 10))
                    combobox.set(value.replace('_', ' ').title())
                    combobox.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = combobox

                elif key == "evaluation_frequency":
                    frequencies = ["Hourly", "Daily", "Weekly", "Bi-Weekly"]
                    combobox = ttk.Combobox(setting_frame, values=frequencies, font=("Arial", 10))
                    combobox.set(value.title())
                    combobox.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = combobox

                elif key == "personality_mode":
                    modes = ["Friendly", "Formal", "Humorous", "Sarcastic", "Professional", "Casual"]
                    combobox = ttk.Combobox(setting_frame, values=modes, font=("Arial", 10))
                    combobox.set(value.title())
                    combobox.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = combobox

                elif key == "response_speed":
                    speeds = ["Instant", "Delayed", "Normal"]
                    combobox = ttk.Combobox(setting_frame, values=speeds, font=("Arial", 10))
                    combobox.set(value.title())
                    combobox.pack(fill=tk.X, padx=5)
                    setting_frame.children['input'] = combobox
                    
            for key, value in self.config.items():
                formatted_key = key.replace('_', ' ').title()

                # Set the border color to white
                setting_frame = tk.LabelFrame(self.master, text=formatted_key, font=("Arial", 12), fg="white", bg="#2c2c2c",
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

            elif key in ["learning_rate", "learning_rate_decay"]:
                slider = Scale(setting_frame, from_=0, to=1, resolution=0.001, orient="horizontal",
                               bg="#2c2c2c", fg="white", troughcolor="white")
                slider.set(value)
                slider.pack(fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = slider

                # Store reference for dynamic adjustment
                if key == "learning_rate":
                    self.learning_rate_slider = slider
                elif key == "learning_rate_decay":
                    self.learning_rate_decay_slider = slider

                self.widgets[key] = slider

            elif key in ["daily_training_sessions", "epoch_count", "batch_size"]:
                slider = Scale(setting_frame, from_=0, to=100, orient="horizontal", bg="#2c2c2c", fg="white",
                               troughcolor="white")
                slider.set(value)
                slider.pack(fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = slider
                self.widgets[key] = slider

            elif key == "training_mode":
                # Create two buttons for 'Supervised' and 'Unsupervised'
                self.training_mode_var = StringVar(value=value)

                button_supervised = tk.Button(setting_frame, text="Supervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value == "Supervised" else "raised",
                                              command=lambda: self.set_training_mode("Supervised"))
                button_unsupervised = tk.Button(setting_frame, text="Unsupervised", font=("Arial", 12), fg="white", bg="#4d4d4d", relief="sunken" if value == "Unsupervised" else "raised",
                                                command=lambda: self.set_training_mode("Unsupervised"))

                button_supervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
                button_unsupervised.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

                # Store references to these buttons for later updates
                self.training_mode_buttons = {"Supervised": button_supervised, "Unsupervised": button_unsupervised}
                self.widgets[key] = self.training_mode_var

            elif key == "training_data_path":
                entry = tk.Entry(setting_frame, font=("Arial", 10), bg="#4d4d4d", fg="white", relief="flat")
                entry.insert(0, value)
                entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = entry

                # Add folder icon button to browse for path
                folder_button = tk.Button(setting_frame, text="📁", command=lambda: self.browse_for_path(entry),
                                          font=("Arial", 12), fg="white", bg="#2c2c2c", relief="flat")
                folder_button.pack(side=tk.LEFT, padx=5)
                self.widgets[key] = entry

            elif key in ["optimizer", "model_type", "evaluation_frequency", "personality_mode", "response_speed"]:
                dropdown_values = self.get_dropdown_options(key)
                combobox = ttk.Combobox(setting_frame, values=[v.title() for v in dropdown_values], font=("Arial", 10))
                combobox.set(value.title())
                combobox.pack(fill=tk.X, padx=5, expand=True)
                setting_frame.children['input'] = combobox
                self.widgets[key] = combobox

            # Add the description for each setting
            description_label = tk.Label(setting_frame, text=self.get_setting_description(key), font=("Arial", 10),
                                         fg="#a9a9a9", bg="#2c2c2c", anchor='w')
            description_label.pack(anchor='w', padx=5)

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

    def default_values(self):
        """
        Reset all settings to their default values.
        """
        default_values = {
            "enabled": True,
            "learning_rate": 0.01,
            "dynamic_learning_rate": True,
            "learning_rate_decay": 0.001,
            "daily_training_sessions": 5,
            "training_mode": "Supervised",
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
            "auto_learning_mode": True,
            "safe_mode": True,
            "max_consecutive_failures": 3,
            "privacy_protection_enabled": True
        }

    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        """
        default_values = self.default_settings()

        for key, widget in self.widgets.items():
            default_value = default_values.get(key)

            if default_value is not None:
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(default_value))
                elif isinstance(widget, tk.Scale):
                    widget.set(default_value)
                elif isinstance(widget, tk.Checkbutton):
                    widget.var.set(default_value)
                elif isinstance(widget, ttk.Combobox):
                    widget.set(default_value)
                elif isinstance(widget, StringVar):  # For Training Mode
                    widget.set(default_value.title())

        # Update Learning Rate sliders if Dynamic Learning Rate is changed
        self.toggle_dynamic_learning_rate()

        messagebox.showinfo("Defaults Restored", "Settings have been restored to their default values.")

    def toggle_dynamic_learning_rate(self):
        """
        Toggle the state of learning rate sliders based on the dynamic learning rate checkbox.
        """
        if self.dynamic_learning_rate_checkbox and self.dynamic_learning_rate_checkbox.var.get():
            # Disable sliders, set them to default values, and change the trough color to grey
            if self.learning_rate_slider:
                self.learning_rate_slider.set(self.default_learning_rate)
                self.learning_rate_slider.configure(state="disabled", troughcolor="#5e5e5e")
            if self.learning_rate_decay_slider:
                self.learning_rate_decay_slider.set(self.default_learning_rate_decay)
                self.learning_rate_decay_slider.configure(state="disabled", troughcolor="#5e5e5e")
        else:
            # Enable sliders and set trough color back to white
            if self.learning_rate_slider:
                self.learning_rate_slider.configure(state="normal", troughcolor="#ffffff")
            if self.learning_rate_decay_slider:
                self.learning_rate_decay_slider.configure(state="normal", troughcolor="#ffffff")

    def format_key(self, key):
        """
        Convert snake_case keys to Title Case for display.
        """
        return key.replace('_', ' ').title()

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
            "auto_learning_mode": "Enable or disable automatic learning from interactions.",
            "safe_mode": "Ensure that the AI operates within safe boundaries.",
            "max_consecutive_failures": "Maximum number of consecutive failures allowed before taking corrective action.",
            "privacy_protection_enabled": "Enable protection of user privacy during AI operations."
        }
        return descriptions.get(key, "No description available for this setting.")
