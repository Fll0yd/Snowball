import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image, ImageSequence
import sys
import os
import logging

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
        self.root.configure(bg="#1e1e1e")
        self.system_monitor_active = False

        # Load the Detroit: Become Human-like background image
        self.bg_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/background_detroit.png"))
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        # Set the duck icon (to keep it quirky)
        duck_icon_path = os.path.join("S:/Snowball/icon/trayicon.png")
        self.duck_icon = ImageTk.PhotoImage(file=duck_icon_path)
        self.root.iconphoto(True, self.duck_icon)

        # Initialize Snowball AI
        self.snowball = SnowballAI()

        # Create Chat Display (taking up only 1/4 of the screen)
        self.chat_frame = tk.Frame(root, bg="#2c2c2c")
        self.chat_frame.place(relwidth=0.25, relheight=0.7, x=10, y=150)

        self.chat_display = tk.Text(self.chat_frame, width=40, height=20, wrap=tk.WORD, bg="#2c2c2c", fg="white", 
                                    insertbackground="white", relief="flat", font=("Arial", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar for chat display
        scroll_bar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input Field
        self.user_input = tk.Entry(root, bg="#404040", fg="white", font=("Arial", 14), relief="flat", insertbackground="white")
        self.user_input.place(relwidth=0.25, height=40, x=10, y=870)

        # Load and resize the send icon
        send_icon_path = os.path.join("S:/Snowball/icon/send.png")
        send_icon = Image.open(send_icon_path).resize((30, 30), Image.Resampling.LANCZOS)
        self.send_icon = ImageTk.PhotoImage(send_icon)

        # Send Button
        self.send_button = tk.Button(root, image=self.send_icon, command=self.send_input, bg="#1e1e1e", relief="flat", bd=0)
        self.send_button.place(x=280, y=870)

        # Bind Enter key to send message
        self.root.bind('<Return>', lambda event: self.send_input())

        # Initial welcome message
        self.chat_display.insert(tk.END, "Welcome! How can Snowball assist you today?\n")

        # Buttons for additional functionalities
        self.create_functionality_buttons()

        # Load Snowball avatar (Detroit-style appearance)
        self.snowball_avatar = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/avatar_detroit.png"))
        self.avatar_label = tk.Label(root, image=self.snowball_avatar, bg="#1e1e1e")
        self.avatar_label.place(relwidth=0.2, relheight=0.3, x=1000, y=150)

    def create_functionality_buttons(self):
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.place(relwidth=0.5, height=80, y=800, x=350)

        # Modern, flat-style buttons
        buttons = ["Games", "Minecraft", "File Monitor", "Edit Memory", "Config"]
        for button_name in buttons:
            button = tk.Button(button_frame, text=button_name, command=lambda name=button_name: self.open_module(name), 
                               bg="#2c2c2c", fg="white", relief="flat", font=("Arial", 14))
            button.pack(side=tk.LEFT, padx=15, pady=10, ipadx=10, ipady=5)

        # System Monitor Toggle
        self.monitor_toggle = tk.BooleanVar(value=False)
        self.monitor_button = tk.Checkbutton(button_frame, text="System Monitor", variable=self.monitor_toggle, 
                                             command=self.toggle_system_monitor, bg="#2c2c2c", fg="white", 
                                             relief="flat", font=("Arial", 14))
        self.monitor_button.pack(side=tk.LEFT, padx=15, pady=10)

    def toggle_system_monitor(self):
        self.system_monitor_active = not self.system_monitor_active
        if self.system_monitor_active:
            self.chat_display.insert(tk.END, "System Monitor activated.\n")
            # Trigger AI avatar animation for system monitoring
            self.animate_avatar("monitoring")
        else:
            self.chat_display.insert(tk.END, "System Monitor deactivated.\n")
            self.animate_avatar("idle")

    def animate_avatar(self, mode="idle"):
        # Animation logic (replace this with actual animation handling)
        if mode == "monitoring":
            avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/avatar_monitoring.png"))
        else:
            avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/avatar_idle.png"))
        
        self.avatar_label.config(image=avatar_image)
        self.avatar_label.image = avatar_image

    def open_module(self, module_name):
        self.chat_display.insert(tk.END, f"Opening {module_name} module...\n")
        # Implement the functionality to open each module here

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
            snowball_response = self.snowball.nlp.process_input(user_message)
        except Exception as e:
            snowball_response
