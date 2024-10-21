import tkinter as tk
from tkinter import Scale, BooleanVar, StringVar, ttk, filedialog, colorchooser
import sys
import os

# Add the root 'S:/Snowball' directory to sys.path
sys.path.append(os.path.abspath("S:/Snowball"))

from core.config_loader import ConfigLoader  # Correct import for config_loader

class InterfaceConfig:
    def __init__(self, master, config_loader):
        self.master = master
        self.master.configure(bg="#2c2c2c")
        self.config_loader = config_loader
        self.config_file_path = "interface_settings.json"

        # Load current settings or use defaults
        self.config = self.config_loader.load_config(self.config_file_path) or self.default_settings()

        # Create widgets for Interface settings
        self.create_widgets()

    def default_settings(self):
        return {
            "nickname": "Ken",
            "response_tone": "casual",
            "response_length": "concise",
            "ui_theme": {
                "theme_type": "light",
                "theme_color": "blue"
            },
            "font": {
                "font_style": "Arial",
                "font_size": 16
            },
            "color_scheme": {
                "background_color": "#e6e6e6",
                "primary_button_color": "#4d4d4d",
                "secondary_button_color": "#1e1e1e",
                "text_color": "#ffffff"
            },
            "layout_preferences": {
                "sidebar_position": "left",  
                "sidebar_width": 250,
                "main_panel_width": "auto",
                "content_spacing": 20
            },
            "language": "en",
            "voice_gender": "female",
            "voice_variant": "en-US-Wavenet-A",
            "theme": "dark",
            "welcome_message_enabled": True,
            "animation_effects": {
                "avatar_entry_animation": "slide",
                "system_alert_animation": "blink"
            },
            "avatar_preferences": {
                "avatar_type": "robotic",
                "animations_enabled": True
            },
            "button_preferences": {
                "button_scale": 1.0,
                "button_corner_radius": 10,
                "button_click_effect": "highlight"
            },
            "notification_preferences": {
                "sound_enabled": True,
                "pop_up_enabled": True,
                "notification_tone": "default",
                "notification_position": "top-right"
            },
            "keyboard_shortcuts": {
                "toggle_sidebar": "CTRL+B",
                "send_message": "ENTER",
                "open_settings": "CTRL+S"
            },
            "gesture_controls": {
                "swipe_enabled": True,
                "swipe_to_open_close_sidebar": True
            },
            "interface_scaling": {
                "dpi_awareness": "auto",
                "scaling_factor": 1.0
            },
            "customization_options": {
                "custom_background_image_enabled": True,
                "background_image_path": "S:/Snowball/icon/background.png"
            },
            "menu_behavior": {
                "expand_on_hover": True,
                "collapse_after_action": False
            },
            "dark_mode": {
                "enabled": False,
                "automatic_toggle": {
                    "enabled": True,
                    "start_time": "18:00",
                    "end_time": "06:00"
                }
            },
            "status_bar_preferences": {
                "show_clock": True,
                "show_date": False,
                "show_system_status": True
            },
            "chat_interface": {
                "typing_animation": True,
                "show_avatar": True,
                "message_alignment": "left",
                "message_spacing": 10
            },
            "voice_interface": {
                "language": "en-US",
                "volume": 70,
                "dynamic_volume_adjustment": True,
                "speech_rate": 1.0,
                "voice_gender": "female",
                "engine": "gTTS",
                "voice_variant": "en-US-Wavenet-A",
                "pitch": 1.2,
                "output_device": "default",
                "response_delay": 0.2,
                "error_handling": {
                    "message": "Sorry, I didn't catch that.",
                    "retries": 2,
                    "timeout_response": "Still not getting it. Please try again later."
                },
                "fallback_language": "en",
                "accent": "US",
                "mute": False,
                "speech_style": "friendly"
            }
        }

    def create_widgets(self):
        # Create Widgets for Each Setting Section
        self.create_nickname_widget(self.master)
        self.create_response_preferences_widgets(self.master)
        self.create_ui_theme_widgets(self.master)
        self.create_font_widgets(self.master)
        self.create_color_scheme_widgets(self.master)
        self.create_layout_preferences_widgets(self.master)
        self.create_notification_preferences_widgets(self.master)
        self.create_chat_interface_widgets(self.master)
        self.create_voice_interface_widgets(self.master)
        self.create_keyboard_shortcuts_widgets(self.master)
        self.create_gesture_controls_widgets(self.master)
        self.create_interface_scaling_widgets(self.master)
        self.create_customization_options_widgets(self.master)
        self.create_menu_behavior_widgets(self.master)
        self.create_dark_mode_widgets(self.master)
        self.create_status_bar_preferences_widgets(self.master)
        self.create_welcome_message_widget(self.master)
        self.create_animation_effects_widgets(self.master)
        self.create_avatar_preferences_widgets(self.master)
        self.create_button_preferences_widgets(self.master)

    def create_nickname_widget(self, parent):
        nickname_frame = self.create_labeled_section("Nickname", parent)
        self.create_labeled_entry(
            label_text="Nickname", 
            default_value=self.config.get("nickname", "Ken"), 
            frame=nickname_frame
        )
        self.add_description(nickname_frame, "The nickname used by the program to address the user.")

    def create_response_preferences_widgets(self, parent):
        response_frame = self.create_labeled_section("Response Preferences", parent)
        self.create_labeled_combobox(
            label_text="Response Tone", 
            options=["Casual", "Formal"],
            default_value=self.config.get("response_tone", "Casual").capitalize(), 
            frame=response_frame
        )
        self.create_labeled_combobox(
            label_text="Response Length", 
            options=["Concise", "Detailed"],
            default_value=self.config.get("response_length", "Concise").capitalize(), 
            frame=response_frame
        )
        self.add_description(response_frame, "Controls how the program responds to user inputs in terms of tone and length.")

    def create_ui_theme_widgets(self, parent):
        ui_frame = self.create_labeled_section("UI Theme", parent)
        self.create_labeled_combobox(
            label_text="Theme Type", options=["Light", "Dark", "Blue"],
            default_value=self.config.get("ui_theme", {}).get("theme_type", "Light").capitalize(),
            frame=ui_frame
        )
        self.create_labeled_combobox(
            label_text="Theme Color", options=["Blue", "Red", "Green"],
            default_value=self.config.get("ui_theme", {}).get("theme_color", "Blue").capitalize(),
            frame=ui_frame
        )
        self.add_description(ui_frame, "Select the overall theme type and color for the interface.")

    def create_font_widgets(self, parent):
        font_frame = self.create_labeled_section("Font Settings", parent)
        font_styles = ["Arial", "Courier", "Times New Roman", "Verdana"]
        self.create_labeled_combobox(
            label_text="Font Style", options=[style.title() for style in font_styles],
            default_value=self.config["font"].get("font_style", "Arial").title(),
            frame=font_frame
        )
        font_sizes = [8, 10, 12, 14, 16, 18, 20]
        self.create_labeled_combobox(
            label_text="Font Size", options=[str(size) for size in font_sizes],
            default_value=str(self.config["font"].get("font_size", 16)),
            frame=font_frame
        )
        self.add_description(font_frame, "Configure the font style and size used in the interface.")

    def create_color_scheme_widgets(self, parent):
        color_scheme_frame = self.create_labeled_section("Color Scheme", parent)
        color_keys = ["background_color", "primary_button_color", "secondary_button_color", "text_color"]
        for color_key in color_keys:
            color_value = self.config["color_scheme"].get(color_key, "#ffffff")
            self.create_labeled_entry_with_button(
                label_text=color_key.replace("_", " ").title(), default_value=color_value, frame=color_scheme_frame
            )
        self.add_description(color_scheme_frame, "Customize the color scheme for different elements of the interface.")

    def create_layout_preferences_widgets(self, parent):
        layout_frame = self.create_labeled_section("Layout Preferences", parent)
        self.create_labeled_combobox(
            label_text="Sidebar Position", options=["Left", "Right"],
            default_value=self.config["layout_preferences"].get("sidebar_position", "Left").capitalize(),
            frame=layout_frame
        )
        self.create_labeled_entry(
            label_text="Sidebar Width", default_value=self.config["layout_preferences"].get("sidebar_width", 250),
            frame=layout_frame
        )
        self.create_labeled_combobox(
            label_text="Main Panel Width", options=["Auto", "Fixed"],
            default_value=self.config["layout_preferences"].get("main_panel_width", "Auto").capitalize(),
            frame=layout_frame
        )
        self.create_labeled_entry(
            label_text="Content Spacing", default_value=self.config["layout_preferences"].get("content_spacing", 20),
            frame=layout_frame
        )
        self.add_description(layout_frame, "Configure the sidebar and main panel layout preferences.")

    def create_notification_preferences_widgets(self, parent):
        notification_frame = self.create_labeled_section("Notification Preferences", parent)
        self.create_labeled_checkbox(
            label_text="Sound Enabled", default_value=self.config["notification_preferences"].get("sound_enabled", True), frame=notification_frame
        )
        self.create_labeled_checkbox(
            label_text="Pop-up Enabled", default_value=self.config["notification_preferences"].get("pop_up_enabled", True), frame=notification_frame
        )
        self.create_labeled_combobox(
            label_text="Notification Tone", options=["Default", "Chime", "Alert"],
            default_value=self.config["notification_preferences"].get("notification_tone", "Default").capitalize(), frame=notification_frame
        )
        self.create_labeled_combobox(
            label_text="Notification Position", options=["Top-Right", "Top-Left", "Bottom-Right", "Bottom-Left"],
            default_value=self.config["notification_preferences"].get("notification_position", "Top-Right").capitalize(), frame=notification_frame
        )
        self.add_description(notification_frame, "Configure notification settings for alerts and tones.")

    def create_chat_interface_widgets(self, parent):
        chat_interface_frame = self.create_labeled_section("Chat Interface", parent)
        self.create_labeled_checkbox(
            label_text="Typing Animation", default_value=self.config["chat_interface"].get("typing_animation", True), frame=chat_interface_frame
        )
        self.create_labeled_checkbox(
            label_text="Show Avatar", default_value=self.config["chat_interface"].get("show_avatar", True), frame=chat_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Message Alignment", options=["Left", "Right"],
            default_value=self.config["chat_interface"].get("message_alignment", "Left").capitalize(), frame=chat_interface_frame
        )
        self.create_labeled_entry(
            label_text="Message Spacing", default_value=self.config["chat_interface"].get("message_spacing", 10), frame=chat_interface_frame
        )
        self.add_description(chat_interface_frame, "Configure chat interface preferences including animations and alignment.")

    def create_voice_interface_widgets(self, parent):
        voice_interface_frame = self.create_labeled_section("Voice Interface", parent)
        self.create_labeled_entry(
            label_text="Language", default_value=self.config["voice_interface"].get("language", "en-US"), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Volume", default_value=self.config["voice_interface"].get("volume", 70), frame=voice_interface_frame
        )
        self.create_labeled_checkbox(
            label_text="Dynamic Volume Adjustment", default_value=self.config["voice_interface"].get("dynamic_volume_adjustment", True), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Speech Rate", default_value=self.config["voice_interface"].get("speech_rate", 1.0), frame=voice_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Voice Gender", options=["Male", "Female"],
            default_value=self.config["voice_interface"].get("voice_gender", "Female").capitalize(), frame=voice_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Voice Engine", options=["gTTS", "Other"],
            default_value=self.config["voice_interface"].get("engine", "gTTS").capitalize(), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Voice Variant", default_value=self.config["voice_interface"].get("voice_variant", "en-US-Wavenet-A"), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Pitch", default_value=self.config["voice_interface"].get("pitch", 1.2), frame=voice_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Output Device", options=["Default", "Other"],
            default_value=self.config["voice_interface"].get("output_device", "Default").capitalize(), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Response Delay", default_value=self.config["voice_interface"].get("response_delay", 0.2), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Error Message", default_value=self.config["voice_interface"].get("error_handling", {}).get("message", "Sorry, I didn't catch that."), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Retries", default_value=self.config["voice_interface"].get("error_handling", {}).get("retries", 2), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Timeout Response", default_value=self.config["voice_interface"].get("error_handling", {}).get("timeout_response", "Still not getting it. Please try again later."), frame=voice_interface_frame
        )
        self.create_labeled_entry(
            label_text="Fallback Language", default_value=self.config["voice_interface"].get("fallback_language", "en"), frame=voice_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Accent", options=["US", "UK", "AU"],
            default_value=self.config["voice_interface"].get("accent", "US"), frame=voice_interface_frame
        )
        self.create_labeled_checkbox(
            label_text="Mute", default_value=self.config["voice_interface"].get("mute", False), frame=voice_interface_frame
        )
        self.create_labeled_combobox(
            label_text="Speech Style", options=["Friendly", "Formal", "Casual"],
            default_value=self.config["voice_interface"].get("speech_style", "Friendly").capitalize(), frame=voice_interface_frame
        )
        self.add_description(voice_interface_frame, "Configure voice interface settings, such as volume, gender, engine, and other speech properties.")
        self.add_description(voice_interface_frame, "Configure voice interface settings, such as volume, gender, engine, and other speech properties.")
        self.add_description(voice_interface_frame, "Configure the voice interface settings including volume and speech rate.")

    def create_avatar_preferences_widgets(self, parent):
        avatar_frame = self.create_labeled_section("Avatar Preferences", parent)
        self.create_labeled_combobox(
            label_text="Avatar Type", options=["Robotic", "Humanlike"],
            default_value=self.config["avatar_preferences"].get("avatar_type", "Robotic").capitalize(), frame=avatar_frame
        )
        self.create_labeled_checkbox(
            label_text="Animations Enabled", default_value=self.config["avatar_preferences"].get("animations_enabled", True), frame=avatar_frame
        )
        self.add_description(avatar_frame, "Configure avatar settings such as type and animations.")

    def create_animation_effects_widgets(self, parent):
        animation_frame = self.create_labeled_section("Animation Effects", parent)
        self.create_labeled_combobox(
            label_text="Avatar Entry Animation", options=["Slide", "Fade", "None"],
            default_value=self.config["animation_effects"].get("avatar_entry_animation", "Slide").capitalize(), frame=animation_frame
        )
        self.create_labeled_combobox(
            label_text="System Alert Animation", options=["Blink", "Pulse", "None"],
            default_value=self.config["animation_effects"].get("system_alert_animation", "Blink").capitalize(), frame=animation_frame
        )
        self.add_description(animation_frame, "Configure animation effects for avatar entry and system alerts.")

    def create_button_preferences_widgets(self, parent):
        button_frame = self.create_labeled_section("Button Preferences", parent)
        self.create_labeled_entry(
            label_text="Button Scale", default_value=self.config["button_preferences"].get("button_scale", 1.0), frame=button_frame
        )
        self.create_labeled_entry(
            label_text="Button Corner Radius", default_value=self.config["button_preferences"].get("button_corner_radius", 10), frame=button_frame
        )
        self.create_labeled_combobox(
            label_text="Button Click Effect", options=["Highlight", "Shadow", "None"],
            default_value=self.config["button_preferences"].get("button_click_effect", "Highlight").capitalize(), frame=button_frame
        )
        self.add_description(button_frame, "Configure button preferences such as scale, corner radius, and click effects.")

    def create_keyboard_shortcuts_widgets(self, parent):
        shortcut_frame = self.create_labeled_section("Keyboard Shortcuts", parent)
        for key, value in self.config["keyboard_shortcuts"].items():
            self.create_labeled_entry(
                label_text=key.replace("_", " ").title(), default_value=value, frame=shortcut_frame
            )
        self.add_description(shortcut_frame, "Configure keyboard shortcuts for quick actions.")

    def create_gesture_controls_widgets(self, parent):
        gesture_frame = self.create_labeled_section("Gesture Controls", parent)
        self.create_labeled_checkbox(
            label_text="Swipe Enabled", default_value=self.config["gesture_controls"].get("swipe_enabled", True), frame=gesture_frame
        )
        self.create_labeled_checkbox(
            label_text="Swipe To Open/Close Sidebar", default_value=self.config["gesture_controls"].get("swipe_to_open_close_sidebar", True), frame=gesture_frame
        )
        self.add_description(gesture_frame, "Configure gesture control settings including swipe actions.")

    def create_interface_scaling_widgets(self, parent):
        scaling_frame = self.create_labeled_section("Interface Scaling", parent)
        self.create_labeled_combobox(
            label_text="DPI Awareness", options=["Auto", "High", "Low"],
            default_value=self.config["interface_scaling"].get("dpi_awareness", "Auto").capitalize(), frame=scaling_frame
        )
        self.create_labeled_entry(
            label_text="Scaling Factor", default_value=self.config["interface_scaling"].get("scaling_factor", 1.0), frame=scaling_frame
        )
        self.add_description(scaling_frame, "Configure interface scaling settings including DPI awareness.")

    def create_customization_options_widgets(self, parent):
        customization_frame = self.create_labeled_section("Customization Options", parent)
        self.create_labeled_checkbox(
            label_text="Custom Background Image Enabled", default_value=self.config["customization_options"].get("custom_background_image_enabled", True), frame=customization_frame
        )
        self.create_labeled_entry_with_folder_button(
            label_text="Background Image Path", default_value=self.config["customization_options"].get("background_image_path", ""), frame=customization_frame
        )
        self.add_description(customization_frame, "Enable and select a custom background image for the interface.")

    def create_menu_behavior_widgets(self, parent):
        menu_frame = self.create_labeled_section("Menu Behavior", parent)
        self.create_labeled_checkbox(
            label_text="Expand On Hover", default_value=self.config["menu_behavior"].get("expand_on_hover", True), frame=menu_frame
        )
        self.create_labeled_checkbox(
            label_text="Collapse After Action", default_value=self.config["menu_behavior"].get("collapse_after_action", False), frame=menu_frame
        )
        self.add_description(menu_frame, "Configure menu behavior including expansion and collapsing settings.")

    def create_dark_mode_widgets(self, parent):
        dark_mode_frame = self.create_labeled_section("Dark Mode", parent)
        self.create_labeled_checkbox(
            label_text="Dark Mode Enabled", default_value=self.config["dark_mode"].get("enabled", False), frame=dark_mode_frame
        )
        self.create_labeled_checkbox(
            label_text="Automatic Toggle Enabled", default_value=self.config["dark_mode"].get("automatic_toggle", {}).get("enabled", True), frame=dark_mode_frame
        )
        self.create_labeled_entry(
            label_text="Start Time", default_value=self.config["dark_mode"].get("automatic_toggle", {}).get("start_time", "18:00"), frame=dark_mode_frame
        )
        self.create_labeled_entry(
            label_text="End Time", default_value=self.config["dark_mode"].get("automatic_toggle", {}).get("end_time", "06:00"), frame=dark_mode_frame
        )
        self.add_description(dark_mode_frame, "Configure dark mode settings and automatic toggle times.")

    def create_status_bar_preferences_widgets(self, parent):
        status_bar_frame = self.create_labeled_section("Status Bar Preferences", parent)
        self.create_labeled_checkbox(
            label_text="Show Clock", default_value=self.config["status_bar_preferences"].get("show_clock", True), frame=status_bar_frame
        )
        self.create_labeled_checkbox(
            label_text="Show Date", default_value=self.config["status_bar_preferences"].get("show_date", False), frame=status_bar_frame
        )
        self.create_labeled_checkbox(
            label_text="Show System Status", default_value=self.config["status_bar_preferences"].get("show_system_status", True), frame=status_bar_frame
        )
        self.add_description(status_bar_frame, "Configure what information is displayed in the status bar.")

    def create_welcome_message_widget(self, parent):
        welcome_message_frame = self.create_labeled_section("Welcome Message", parent)
        self.create_labeled_checkbox(
            label_text="Welcome Message Enabled", default_value=self.config.get("welcome_message_enabled", True), frame=welcome_message_frame
        )
        self.add_description(welcome_message_frame, "Enable or disable the welcome message when starting the application.")

    def create_animation_effects_widgets(self, parent):
        animation_frame = self.create_labeled_section("Animation Effects", parent)
        self.create_labeled_combobox(
            label_text="Avatar Entry Animation", options=["Slide", "Fade", "None"],
            default_value=self.config["animation_effects"].get("avatar_entry_animation", "Slide").capitalize(), frame=animation_frame
        )
        self.create_labeled_combobox(
            label_text="System Alert Animation", options=["Blink", "Flash", "None"],
            default_value=self.config["animation_effects"].get("system_alert_animation", "Blink").capitalize(), frame=animation_frame
        )
        self.add_description(animation_frame, "Configure animations for avatar entry and system alerts.")

    def create_button_preferences_widgets(self, parent):
        button_frame = self.create_labeled_section("Button Preferences", parent)
        self.create_labeled_entry(
            label_text="Button Scale", default_value=self.config["button_preferences"].get("button_scale", 1.0), frame=button_frame
        )
        self.create_labeled_entry(
            label_text="Button Corner Radius", default_value=self.config["button_preferences"].get("button_corner_radius", 10), frame=button_frame
        )
        self.create_labeled_combobox(
            label_text="Button Click Effect", options=["Highlight", "Shrink", "None"],
            default_value=self.config["button_preferences"].get("button_click_effect", "Highlight").capitalize(), frame=button_frame
        )
        self.add_description(button_frame, "Configure button scaling, corner radius, and click effects.")

    def create_labeled_section(self, label_text, parent):
        section_frame = tk.LabelFrame(parent, text=label_text, font=("Arial", 12), fg="white", bg="#2c2c2c", labelanchor='nw')
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        return section_frame

    def create_labeled_entry(self, label_text, default_value, frame):
        entry_frame = tk.Frame(frame, bg="#2c2c2c")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        label = tk.Label(entry_frame, text=label_text, font=("Arial", 10), fg="white", bg="#2c2c2c")
        label.pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(entry_frame, font=("Arial", 10), bg="#cfcfcf", fg="black")  # Lighter gray background for active look
        entry.insert(0, default_value)
        entry.pack(fill=tk.X, padx=5, expand=True)

    def create_labeled_entry_with_button(self, label_text, default_value, frame):
        entry_frame = tk.Frame(frame, bg="#2c2c2c")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        label = tk.Label(entry_frame, text=label_text, font=("Arial", 10), fg="white", bg="#2c2c2c")
        label.pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(entry_frame, font=("Arial", 10), bg="#cfcfcf", fg="black")
        entry.insert(0, default_value)
        entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)

        def choose_color(entry_widget=entry):
            color_code = colorchooser.askcolor(title="Choose color")[1]
            if color_code:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, color_code)

        button = tk.Button(entry_frame, text="Choose", command=choose_color, font=("Arial", 10), bg="#4d4d4d", fg="white")
        button.pack(side=tk.LEFT, padx=5)

    def create_labeled_entry_with_folder_button(self, label_text, default_value, frame):
        entry_frame = tk.Frame(frame, bg="#2c2c2c")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        label = tk.Label(entry_frame, text=label_text, font=("Arial", 10), fg="white", bg="#2c2c2c")
        label.pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(entry_frame, font=("Arial", 10), bg="#cfcfcf", fg="black")
        entry.insert(0, default_value)
        entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)

        def choose_file(entry_widget=entry):
            file_path = filedialog.askopenfilename(title="Select Background Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if file_path:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, file_path)

        button = tk.Button(entry_frame, text="Choose", command=choose_file, font=("Arial", 10), bg="#4d4d4d", fg="white")
        button.pack(side=tk.LEFT, padx=5)

    def create_labeled_checkbox(self, label_text, default_value, frame):
        var = BooleanVar(value=default_value)
        checkbox = tk.Checkbutton(frame, text=label_text, variable=var, bg="#2c2c2c", fg="white", font=("Arial", 10), selectcolor="#4d4d4d")
        checkbox.pack(anchor="w", padx=5, pady=5)

    def create_labeled_combobox(self, label_text, options, default_value, frame):
        combobox_frame = tk.Frame(frame, bg="#2c2c2c")
        combobox_frame.pack(fill=tk.X, padx=5, pady=5)

        label = tk.Label(combobox_frame, text=label_text, font=("Arial", 10), fg="white", bg="#2c2c2c")
        label.pack(side=tk.LEFT, padx=5)

        combobox = ttk.Combobox(combobox_frame, values=options, font=("Arial", 10))
        combobox.set(default_value)
        combobox.pack(fill=tk.X, padx=5, expand=True)

    def add_description(self, frame, description_text):
        description_label = tk.Label(frame, text=description_text, font=("Arial", 10), fg="#a9a9a9", bg="#2c2c2c", anchor='w')
        description_label.pack(fill=tk.X, padx=5, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1450x1000")  # Slightly increased window size for better content visibility
    root.configure(bg="#2c2c2c")
    config_loader = ConfigLoader()  # Properly initialize the ConfigLoader instance
    app = InterfaceConfig(root, config_loader)
    root.mainloop()