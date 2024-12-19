import os
import sys
import threading
import tkinter as tk
from tkinter import ttk
import warnings
import time
import json

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Add project root to system path
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '../..'))  # Adjusted for `interface/main_menu.py`
if project_root not in sys.path:
    sys.path.insert(0, project_root)  # Prepend to ensure priority

# Import SnowballInitializer
from Snowball.core.initializer import SnowballInitializer

class SnowballGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Snowball AI - Chat Interface")
        self.master.geometry("800x600")
        self.master.configure(bg="#e6e6e6")
        
        # Initialize components
        self.chat_initialized = False
        self.create_chat_display()
        self.create_input_field()

        # Start initialization
        threading.Thread(target=self.initialize_ai, daemon=True).start()
        self.display_message("Welcome! Initializing Snowball AI, please wait...", sender="System")

    def initialize_ai(self):
        """Initialize Snowball AI."""
        try:
            initializer = SnowballInitializer()
            self.snowball = initializer.snowball_ai
            self.chat_initialized = True
            self.display_message("Snowball AI is ready! How can I assist you?", sender="System")
        except Exception as e:
            self.display_message(f"Failed to initialize AI: {e}", sender="System")

    def create_chat_display(self):
        """Create chat display area."""
        self.chat_display = tk.Text(self.master, wrap=tk.WORD, bg="#2c2c2c", fg="white", font=("Consolas", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

    def create_input_field(self):
        """Create input field and send button."""
        input_frame = tk.Frame(self.master, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        self.user_input = tk.Entry(input_frame, bg="#404040", fg="white", font=("Consolas", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        self.user_input.bind("<Return>", lambda event: self.send_input())

        self.send_button = tk.Button(input_frame, text="Send", command=self.send_input, bg="#1e1e1e", fg="white")
        self.send_button.pack(side=tk.RIGHT, padx=(5, 10))

    def send_input(self):
        """Send user input to Snowball AI."""
        user_message = self.user_input.get().strip()
        if not user_message or not self.chat_initialized:
            return

        self.display_message(user_message, sender="You")
        self.user_input.delete(0, tk.END)
        self.display_message("Snowball is thinking...", sender="System")

        threading.Thread(target=self.process_input, args=(user_message,), daemon=True).start()

    def process_input(self, user_message):
        """Process user input with Snowball AI."""
        try:
            response = self.snowball.get_combined_response(user_message)
            self.display_message(response, sender="Snowball")
        except Exception as e:
            self.display_message(f"Error: {e}", sender="System")

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
