import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
import time
import pygame
from datetime import datetime
import warnings

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Add project root to system path
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import core modules
from Snowball.core.system.logger import SnowballLogger
from Snowball.core.ai.chat_agent import SnowballAI
from Snowball.core.system.system_monitor import SystemMonitor, periodic_upload, DEFAULT_SETTINGS

class SnowballGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Snowball AI - Main Menu")
        self.master.geometry("1250x950")
        self.master.configure(bg="#e6e6e6")

        # Initialize logger
        self.logger = SnowballLogger()

        # Initialize components
        self.snowball_ai = SnowballAI(logger=self.logger)
        self.system_monitor = SystemMonitor()
        self.monitor_active = False

        # Load background image
        self.load_background()

        # Load avatar images
        self.load_avatar_images()

        # Chat display
        self.create_chat_display()

        # Input field
        self.create_input_field()

        # Buttons for functionalities
        self.create_functionality_buttons()

        # System Monitor Toggle
        self.create_system_monitor_toggle()

        # Start avatar animation and greeting
        self.start_avatar_entry()

    def initialize_chat_agent_triggers(self):
        """Initialize and link chat-agent triggers for decision-making."""
        try:
            self.snowball_ai.initialize_components(
                decision_maker="Snowball.core.ai.decision_maker",
                memory="Snowball.core.ai.memory",
                sentiment_analysis="Snowball.core.ai.sentiment_analysis"
            )
            self.logger.log_event("Chat agent components initialized.")
        except Exception as e:
            self.logger.log_error(f"Error initializing chat-agent triggers: {e}")

    def load_background(self):
        """Load the background image."""
        try:
            bg_image_path = os.path.join("S:/Snowball/icon/background.png")
            self.bg_image = ImageTk.PhotoImage(Image.open(bg_image_path))
            self.bg_label = tk.Label(self.master, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            self.logger.error("Background image not found. Using default background.")

    def load_avatar_images(self):
        """Load avatar images."""
        try:
            avatar_path = os.path.join("S:/Snowball/icon/avatar_placeholder.png")
            monitoring_path = os.path.join("S:/Snowball/icon/monitoring_placeholder.png")
            self.avatar_image = ImageTk.PhotoImage(Image.open(avatar_path))
            self.monitoring_image = ImageTk.PhotoImage(Image.open(monitoring_path))
            self.avatar_label = tk.Label(self.master, image=self.avatar_image, bd=0)
        except FileNotFoundError:
            self.logger.error("Avatar images not found.")

    def create_chat_display(self):
        """Create chat display area."""
        self.chat_frame = tk.Frame(self.master, bg="#2c2c2c", bd=2)
        self.chat_frame.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.25)

        self.chat_display = tk.Text(self.chat_frame, wrap=tk.WORD, bg="#2c2c2c", fg="white", font=("Consolas", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        scroll_bar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_input_field(self):
        """Create input field and send button."""
        self.input_frame = tk.Frame(self.master, bg="#1e1e1e")
        self.input_frame.place(relx=0.05, rely=0.95, relwidth=0.9, relheight=0.05)

        self.user_input = tk.Entry(self.input_frame, bg="#404040", fg="white", font=("Consolas", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        self.user_input.bind("<Return>", lambda event: self.send_input())

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_input, bg="#1e1e1e", fg="white")
        self.send_button.pack(side=tk.RIGHT, padx=(5, 10))

    def create_functionality_buttons(self):
        """Create functionality buttons."""
        button_frame = tk.Frame(self.master, bg="#4d4d4d", bd=0)
        button_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.05)

        buttons = ["Games", "Minecraft", "View Logs", "Config"]
        for index, button_name in enumerate(buttons):
            button = tk.Button(button_frame, text=button_name,
                               command=lambda name=button_name: self.handle_menu_action(name),
                               bg="#1e1e1e", fg="white", font=("Arial", 12),
                               activebackground="#3e3e3e", activeforeground="white")
            button.grid(row=0, column=index, padx=10, pady=5)

    def create_system_monitor_toggle(self):
        """Create a toggle for the System Monitor."""
        self.monitor_toggle = tk.IntVar()
        self.monitor_button = ttk.Checkbutton(
            self.master, text="Enable System Monitor",
            variable=self.monitor_toggle, command=self.toggle_system_monitor
        )
        self.monitor_button.place(relx=0.85, rely=0.07)

    def start_avatar_entry(self):
        """Animate the avatar entry and greet the user."""
        try:
            pygame.mixer.init()
            footsteps_path = os.path.join("S:/Snowball/storage/audio/footsteps.mp3")
            if os.path.exists(footsteps_path):
                pygame.mixer.music.load(footsteps_path)
                pygame.mixer.music.play()
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")

        self.avatar_label.place(relx=1.0, rely=0.2)  # Start off-screen
        self.master.after(50, lambda: self.move_avatar(target_x=0.35))

    def move_avatar(self, target_x, step=0.01):
        """Move the avatar into the frame."""
        current_x = self.avatar_label.winfo_x() / self.master.winfo_width()
        if current_x > target_x:
            new_x = max(current_x - step, target_x)
            self.avatar_label.place(relx=new_x, rely=0.2)
            self.master.after(50, lambda: self.move_avatar(target_x))
        else:
            self.greet_user()

    def greet_user(self):
        """Greet the user."""
        self.display_message("Hello! How can I assist you today?", sender="Snowball")

    def send_input(self):
        """Send user input to Snowball AI."""
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        self.display_message(user_message, sender="You")
        self.user_input.delete(0, tk.END)

        threading.Thread(target=self.process_input, args=(user_message,), daemon=True).start()

    def process_input(self, user_message):
        """Process user input using Snowball AI."""
        try:
            response = self.snowball_ai.get_combined_response(user_message)
            self.display_message(response, sender="Snowball")
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            self.display_message("Error processing input. Please try again.", sender="System")

    def toggle_system_monitor(self):
        """Toggle the system monitor on/off."""
        if self.monitor_toggle.get() == 1:
            self.start_system_monitor()
        else:
            self.stop_system_monitor()

    def start_system_monitor(self):
        """Start the system monitor."""
        self.display_message("System Monitor activated. Monitoring your system.", sender="Snowball")
        threading.Thread(target=self.system_monitor.monitor_system, daemon=True).start()

    def stop_system_monitor(self):
        """Stop the system monitor."""
        self.display_message("System Monitor deactivated.", sender="Snowball")
        self.system_monitor.stop()

    def handle_menu_action(self, action):
        """Handle menu button actions."""
        self.display_message(f"{action} feature coming soon!", sender="System")

    def display_message(self, message, sender):
        """Display a message in the chat."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SnowballGUI(root)
    root.mainloop()
