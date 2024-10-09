import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import sys
import logging
import time
import threading
import pygame
import json
import os

# Import the new config interface module
from config_interface import ConfigInterface  

# Load API keys from JSON file
try:
    with open('S:/Snowball/config/account_integrations.json', 'r') as file:
        api_keys = json.load(file)

    # Check if the OpenAI API key is available
    if not api_keys.get('api_keys', {}).get('openai_api_key'):
        raise ValueError("OpenAI API key not found in S:/Snowball/config/account_integrations.json")

    # Set environment variable for OpenAI key
    os.environ['OPENAI_API_KEY'] = api_keys['api_keys']['openai_api_key']

except FileNotFoundError:
    raise FileNotFoundError("The API keys file was not found at S:/Snowball/config/account_integrations.json")
except json.JSONDecodeError:
    raise ValueError("The API keys file is not in a valid JSON format")
except Exception as e:
    raise RuntimeError(f"An unexpected error occurred: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add the Snowball directory to the system path
sys.path.append('S:/Snowball')

# Debugging output to confirm path
logging.info(f"Current Python Path: {sys.path}")

try:
    logging.info("Attempting to import SnowballAI...")
    from core.ai_agent import SnowballAI
except ImportError as e:
    logging.error(f"ImportError: {e}")
    sys.exit(1)

class SnowballGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snowball AI - Main Menu")
        self.root.geometry("1250x950")
        self.root.configure(bg="#e6e6e6")

        # Load the background image for a futuristic feel
        self.bg_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/background.png"))
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        # Set the AI avatar in a prominent position (initially hidden)
        self.snowball_avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/avatar_placeholder.png"))  # Placeholder for the animated avatar
        self.monitoring_avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/monitoring_placeholder.png"))
        self.avatar_label = tk.Label(root, image=self.snowball_avatar_image, bd=0)

        # Set the duck icon
        duck_icon_path = os.path.join("S:/Snowball/icon/trayicon.png")
        self.duck_icon = ImageTk.PhotoImage(file=duck_icon_path)
        self.root.iconphoto(True, self.duck_icon)

        # Initialize Snowball AI
        self.snowball = SnowballAI()

        # Create Chat Display (takes up the bottom of the screen)
        self.chat_display_frame = tk.Frame(root, bg="#2c2c2c", bd=2, relief="ridge")
        self.chat_display_frame.place(relx=0.05, rely=0.7, relwidth=0.9, relheight=0.25)

        self.chat_display = tk.Text(self.chat_display_frame, wrap=tk.WORD, bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", font=("Consolas", 10))
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Scrollbar for chat display
        scroll_bar = ttk.Scrollbar(self.chat_display_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input Field
        self.input_frame = tk.Frame(root, bg="#1e1e1e")
        self.input_frame.place(relx=0.05, rely=0.95, relwidth=0.9, relheight=0.05)

        self.user_input = tk.Entry(self.input_frame, bg="#404040", fg="white", font=("Consolas", 12), relief="flat", insertbackground="white")
        self.user_input.pack(pady=5, padx=10, fill=tk.X, side=tk.LEFT, expand=True)

        # Load and resize the send icon
        send_icon_path = os.path.join("S:/Snowball/icon/send.png")
        send_icon = Image.open(send_icon_path).resize((30, 30), Image.Resampling.LANCZOS)
        self.send_icon = ImageTk.PhotoImage(send_icon)

        # Send Button with send icon
        self.send_button = tk.Button(self.input_frame, image=self.send_icon, command=self.send_input, bg="#1e1e1e", relief="flat", bd=0)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Bind Enter key to send message
        self.root.bind('<Return>', lambda event: self.send_input())

        # Initial welcome message
        self.chat_display.insert(tk.END, "Welcome! How can Snowball assist you today?\n")

        # Buttons for additional functionalities (top menu like a game UI)
        self.create_functionality_buttons()

        # Play footsteps and move avatar into frame
        self.start_avatar_entry()

    def create_functionality_buttons(self):
        button_frame = tk.Frame(self.root, bg="#e6e6e6", bd=0, relief="flat")
        button_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.08)

        buttons = ["Games", "Minecraft", "File Monitor", "Edit Memory", "Config"]
        for button_name in buttons:
            button = tk.Button(button_frame, text=button_name, command=lambda name=button_name: self.open_module(name),
                              bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", padx=20, pady=10)
            button.pack(side=tk.LEFT, padx=10)

        # Create System Monitor switch
        self.system_monitor_var = tk.BooleanVar()
        self.system_monitor_switch = ttk.Checkbutton(button_frame, text="System Monitor", variable=self.system_monitor_var,
                                                     command=self.toggle_system_monitor, style="Switch.TCheckbutton")
        self.system_monitor_switch.pack(side=tk.RIGHT, padx=10)

        # Style for the switch
        style = ttk.Style()
        style.configure("Switch.TCheckbutton", font=("Arial", 12))
        style.map("Switch.TCheckbutton",
                  background=[("selected", "#4caf50"), ("!selected", "#4d4d4d")],
                  foreground=[("selected", "white"), ("!selected", "white")])

    def open_module(self, module_name):
        if module_name == "Config":
            # Open the ConfigInterface when "Config" button is pressed
            config_window = tk.Toplevel(self.root)
            config_window.title("Configuration")
            ConfigInterface(config_window)  # This creates an instance of the ConfigInterface window

        elif module_name == "System Monitor":
            if not hasattr(self, 'system_monitor_active') or not self.system_monitor_active:
                self.system_monitor_active = True
                self.chat_display.insert(tk.END, "System Monitor activated.\n")
            else:
                self.system_monitor_active = False
                self.chat_display.insert(tk.END, "System Monitor deactivated.\n")
        else:
            self.chat_display.insert(tk.END, f"Opening {module_name} module...\n")

    def send_input(self):
        user_message = self.user_input.get()
        if not user_message.strip():
            return  # Don't process empty inputs

        self.display_message(user_message, sender='user')
        self.chat_display.insert(tk.END, "Snowball is thinking...\n")
        self.chat_display.see(tk.END)

        # Process the input through Snowball
        self.root.after(100, lambda: self.process_input(user_message))

    def process_input(self, user_message):
        try:
            snowball_response = self.snowball.process_input(user_message)
        except Exception as e:
            snowball_response = "Oops! Something went wrong. " + str(e)

        self.display_message(snowball_response, sender='snowball')

    def display_message(self, message, sender='user'):
        tag = 'user' if sender == 'user' else 'snowball'
        self.chat_display.insert(tk.END, f"{sender.capitalize()}: {message}\n", tag)
        self.chat_display.see(tk.END)

        # Clear the input field if it's from the user
        if sender == 'user':
            self.user_input.delete(0, tk.END)

    def start_avatar_entry(self):
        # Play footsteps audio
        pygame.mixer.init()
        footsteps_path = os.path.join("S:/Snowball/audio/footsteps.mp3")
        pygame.mixer.music.load(footsteps_path)
        pygame.mixer.music.play()

        # Start moving the avatar from the right
        self.avatar_label.place(relx=1.0, rely=0.2)  # Start off-screen to the right
        self.root.after(100, lambda: self.move_avatar_slowly(target_relx=0.35))

    def move_avatar_slowly(self, target_relx, step=0.01):
        current_relx = self.avatar_label.winfo_x() / self.root.winfo_width()
        if current_relx > target_relx:
            new_relx = current_relx - step
            self.avatar_label.place(relx=new_relx, rely=0.2)
            self.root.after(50, lambda: self.move_avatar_slowly(target_relx))
        else:
            # Play greeting after avatar reaches target position
            self.greet_user()

    def greet_user(self):
        try:
            # Use the voice interface to generate and speak the greeting
            greeting = self.snowball.voice.generate_greeting()
            self.snowball.voice.speak(greeting)
        except Exception as e:
            self.snowball.logger.logger.error(f"Error greeting user: {e}")

    def toggle_system_monitor(self):
        if self.system_monitor_var.get():
            self.chat_display.insert(tk.END, "System Monitor activated.\n")
            # Change avatar to monitoring placeholder
            self.avatar_label.configure(image=self.monitoring_avatar_image)
            self.avatar_label.place(relx=0.35, rely=0.2)
        else:
            self.chat_display.insert(tk.END, "System Monitor deactivated.\n")
            # Change avatar back to default placeholder
            self.avatar_label.configure(image=self.snowball_avatar_image)
            self.avatar_label.place(relx=0.35, rely=0.2)

if __name__ == "__main__":
    root = tk.Tk()
    app = SnowballGUI(root)
    root.mainloop()