import time
import threading
import pygame
import json
import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import ImageTk, Image
import tensorflow as tf
import warnings
import os
import sys

# Add the core directory to the system path to resolve module imports
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Debugging: Print the sys.path to verify that the project root has been added
print("Current sys.path:")
for path in sys.path:
    print(f" - {path}")

# Import core modules explicitly
try:
    from core.initializer import SnowballInitializer
    from interface.config_interface import ConfigInterface
    from interface.game_interface import GameInterface
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure that 'core' and 'interface' directories exist and are accessible.")
    sys.exit(1)

# Suppress TensorFlow and general warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow INFO and WARNING messages
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Initialize the Tkinter master window
master = tk.Tk()

class SnowballGUI:
    def __init__(self, master):
        self.master = master

        # Set up the GUI
        self.master.title("Snowball AI - Main Menu")
        self.master.geometry("1250x950")
        self.master.configure(bg="#e6e6e6")

        # Load the background image for a futuristic feel
        try:
            self.bg_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/background.png"))
            self.bg_label = tk.Label(master, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            print("Background image not found at S:/Snowball/icon/background.png")

        # Create Chat Display (takes up the bottom of the screen)
        self.chat_display_frame = tk.Frame(master, bg="#2c2c2c", bd=2, relief="ridge")
        self.chat_display_frame.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.25)

        self.chat_display = tk.Text(self.chat_display_frame, wrap=tk.WORD, bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", font=("Consolas", 10))
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Scrollbar for chat display
        scroll_bar = ttk.Scrollbar(self.chat_display_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input Field
        self.input_frame = tk.Frame(master, bg="#1e1e1e")
        self.input_frame.place(relx=0.05, rely=0.95, relwidth=0.9, relheight=0.05)

        self.user_input = tk.Entry(self.input_frame, bg="#404040", fg="white", font=("Consolas", 12), relief="flat", insertbackground="white")
        self.user_input.pack(pady=5, padx=10, fill=tk.X, side=tk.LEFT, expand=True)

        # Load and resize the send icon
        try:
            send_icon_path = os.path.join("S:/Snowball/icon/send.png")
            send_icon = Image.open(send_icon_path).resize((30, 30), Image.Resampling.LANCZOS)
            self.send_icon = ImageTk.PhotoImage(send_icon)
        except FileNotFoundError:
            print("Send icon not found at S:/Snowball/icon/send.png")
            self.send_icon = None

        # Send Button with send icon
        self.send_button = tk.Button(self.input_frame, image=self.send_icon, command=self.send_input, bg="#1e1e1e", relief="flat", bd=0, state=tk.DISABLED)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Bind Enter key to send message
        self.master.bind('<Return>', lambda event: self.send_input())

        # Initial welcome message
        self.chat_display.insert(tk.END, "Welcome! Snowball AI is initializing, please wait...\n")

        # Buttons for additional functionalities (top menu like a game UI)
        self.create_functionality_buttons()

        # Start initialization in the background
        threading.Thread(target=self.initialize_background_components, daemon=True).start()

    def create_functionality_buttons(self):
        button_frame = tk.Frame(self.master, bg="#4d4d4d", bd=0, relief="flat")
        button_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.05)

        buttons = ["Games", "Minecraft", "File Monitor", "Edit Memory", "Config"]

        button_frame.grid_columnconfigure(tuple(range(len(buttons))), weight=1)

        self.buttons = []
        for index, button_name in enumerate(buttons):
            button = tk.Button(button_frame, text=button_name,
                               command=lambda name=button_name: self.open_module(name),
                               bg="#1e1e1e", fg="white", font=("Arial", 14, "bold"),
                               relief="flat", bd=0, highlightthickness=0,
                               activebackground="#3e3e3e", activeforeground="white", state=tk.DISABLED)
            button.grid(row=0, column=index, sticky="nsew", padx=10, pady=(2, 2))
            self.buttons.append(button)

    def open_module(self, module_name):
        self.chat_display.insert(tk.END, f"Opening {module_name} module...\n")

    def send_input(self):
        if not self.send_button['state'] == tk.NORMAL:
            return

        user_message = self.user_input.get()
        if not user_message.strip():
            return

        self.display_message(user_message, sender='user')
        self.chat_display.insert(tk.END, "Snowball is thinking...\n")
        self.chat_display.see(tk.END)

    def display_message(self, message, sender='user'):
        tag = 'user' if sender == 'user' else 'snowball'
        self.chat_display.insert(tk.END, f"{sender.capitalize()}: {message}\n", tag)
        self.chat_display.see(tk.END)

        if sender == 'user':
            self.user_input.delete(0, tk.END)

    def initialize_background_components(self):
        # Long-running initializations here
        try:
            print("Starting initialization of Snowball components...")

            # Debugging the initialization process with detailed statements
            start_time = time.time()

            # 1. Initialize SnowballInitializer with checkpoints
            print("Initializing SnowballInitializer...")
            initializer = SnowballInitializer()
            print("SnowballInitializer initialized.")

            # 2. Set up logging
            print("Setting up logger...")
            self.logger = initializer.logger
            print("Logger setup complete.")

            # 3. Load configuration
            print("Loading configuration...")
            self.config_loader = initializer.config_loader
            print("Configuration loaded.")

            # 4. Initialize AI components
            print("Initializing AI components...")
            self.snowball_ai = initializer.snowball_ai
            print("AI components initialized.")

            # 5. Initialize System Monitor
            print("Initializing System Monitor...")
            self.system_monitor = initializer.system_monitor
            print("System Monitor initialized.")

            # 6. Initialize Game Interface
            print("Initializing Game Interface...")
            self.game_interface = GameInterface(logger=self.logger, config_loader=self.config_loader, q_learning_agent=initializer.q_learning_agent)
            print("Game Interface initialized.")

            # Log initialization time
            total_init_time = time.time() - start_time
            print(f"Total initialization time: {total_init_time:.2f} seconds")

            # Notify user that initialization is complete
            self.master.after(0, lambda: self.chat_display.insert(tk.END, "Snowball AI is ready to assist you!\n"))
            self.master.after(0, self.enable_buttons)

        except Exception as e:
            print(f"Error initializing components: {e}")
            self.master.after(0, lambda: self.chat_display.insert(tk.END, f"Error initializing components: {e}\n"))

    def enable_buttons(self):
        # Enable all buttons and input field after initialization
        for button in self.buttons:
            button.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = SnowballGUI(master)
    master.mainloop()
