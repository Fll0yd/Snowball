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

# Initialize the main application components using SnowballInitializer
initializer = SnowballInitializer()
logger = initializer.logger
config_loader = initializer.config_loader
snowball_ai = initializer.snowball_ai
game_interface = GameInterface(logger=logger, config_loader=config_loader, q_learning_agent=initializer.q_learning_agent)

# Initialize the Tkinter master window
master = tk.Tk()

class SnowballGUI:
    def __init__(self, master, initializer):
        self.master = master
        self.logger = initializer.logger
        self.config_loader = initializer.config_loader
        self.snowball_ai = initializer.snowball_ai
        self.system_monitor = initializer.system_monitor

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
            self.logger.error("Background image not found at S:/Snowball/icon/background.png")

        # Set the AI avatar in a prominent position (initially hidden)
        try:
            self.snowball_avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/avatar_placeholder.png"))  # Placeholder for the animated avatar
            self.monitoring_avatar_image = ImageTk.PhotoImage(file=os.path.join("S:/Snowball/icon/monitoring_placeholder.png"))
            self.avatar_label = tk.Label(master, image=self.snowball_avatar_image, bd=0)
        except FileNotFoundError:
            self.logger.error("Avatar image not found at S:/Snowball/icon/avatar_placeholder.png or monitoring_placeholder.png")

        # Set the duck icon
        try:
            image = Image.open("S:/Snowball/icon/trayicon.png")
            icon_image = ImageTk.PhotoImage(image)
            master.iconphoto(False, icon_image)
        except Exception as e:
            self.logger.error(f"Failed to load image for icon: {e}")

        # Initialize Snowball AI using the provided instance
        self.snowball = snowball_ai

        # Initialize GameInterface instance
        self.game_interface = game_interface

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
            self.logger.error("Send icon not found at S:/Snowball/icon/send.png")
            self.send_icon = None

        # Send Button with send icon
        self.send_button = tk.Button(self.input_frame, image=self.send_icon, command=self.send_input, bg="#1e1e1e", relief="flat", bd=0)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Bind Enter key to send message
        self.master.bind('<Return>', lambda event: self.send_input())

        # Initial welcome message
        self.chat_display.insert(tk.END, "Welcome! How can Snowball assist you today?\n")

        # Buttons for additional functionalities (top menu like a game UI)
        self.create_functionality_buttons()

        # Play footsteps and move avatar into frame
        self.start_avatar_entry()
        
    def create_functionality_buttons(self):
        # Create the button frame with reduced height to fit buttons precisely
        button_frame = tk.Frame(self.master, bg="#4d4d4d", bd=0, relief="flat")
        button_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.05)  # Adjusted height for less padding

        buttons = ["Games", "Minecraft", "File Monitor", "Edit Memory", "Config"]

        # Configure columns for even spacing using grid
        button_frame.grid_columnconfigure(tuple(range(len(buttons))), weight=1)

        for index, button_name in enumerate(buttons):
            button = tk.Button(button_frame, text=button_name,
                               command=lambda name=button_name: self.open_module(name),
                               bg="#1e1e1e", fg="white", font=("Arial", 14, "bold"),
                               relief="flat", bd=0, highlightthickness=0,
                               activebackground="#3e3e3e", activeforeground="white")
            button.grid(row=0, column=index, sticky="nsew", padx=10, pady=(2, 2))  # Even padding above and below buttons

        # Configure style for the futuristic switch and position it directly under the buttons
        self.system_monitor_var = tk.BooleanVar()
        self.system_monitor_switch = ttk.Checkbutton(self.master, text="System Monitor", variable=self.system_monitor_var,
                                                     command=self.toggle_system_monitor, style="Switch.TCheckbutton")
        self.system_monitor_switch.place(relx=0.85, rely=0.07)  # Move it up slightly for a tighter fit

        # Adjust the style for a futuristic look
        style = ttk.Style()
        style.configure("Switch.TCheckbutton", font=("Arial", 12))
        style.map("Switch.TCheckbutton",
                  background=[("selected", "#4caf50"), ("!selected", "#4d4d4d")],
                  foreground=[("selected", "white"), ("!selected", "white")])

    def open_module(self, module_name):
        if module_name == "Config":
            # Open the ConfigInterface when "Config" button is pressed
            config_window = tk.Toplevel(self.master)
            config_window.title("Configuration")
            # Pass the required parameters (ai_instance and config_loader)
            ConfigInterface(config_window, self.snowball, self.config_loader)  # Create an instance of the ConfigInterface window
        elif module_name == "Games":
            self.open_game_interface()
        else:
            self.chat_display.insert(tk.END, f"Opening {module_name} module...\n")

    def open_game_interface(self):
        # Create a new window for the game interface
        game_window = tk.Toplevel(self.master)
        game_window.title("Game Interface")
        game_window.geometry("800x600")
        game_window.configure(bg="#2c2c2c")

        # Create a listbox to display available games
        game_listbox = tk.Listbox(game_window, bg="#404040", fg="white", font=("Arial", 12), selectbackground="#3e3e3e")
        game_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Populate the listbox with games from GameInterface
        for game in self.game_interface.list_available_games():
            game_listbox.insert(tk.END, game)

        # Create a button to launch the selected game
        launch_button = tk.Button(game_window, text="Launch Game", command=lambda: self.launch_selected_game(game_listbox),
                                bg="#1e1e1e", fg="white", font=("Arial", 14), relief="flat", activebackground="#3e3e3e")
        launch_button.pack(pady=10)

    def launch_selected_game(self, game_listbox):
        selected_game = game_listbox.get(tk.ACTIVE)
        if selected_game:
            self.game_interface.launch_game(selected_game)

    def send_input(self):
        user_message = self.user_input.get()
        if not user_message.strip():
            return

        self.display_message(user_message, sender='user')
        self.chat_display.insert(tk.END, "Snowball is thinking...\n")
        self.chat_display.see(tk.END)

        # Process the input through Snowball
        self.master.after(100, lambda: threading.Thread(target=self.process_input, args=(user_message,)).start())

    def process_input(self, user_message):
        try:
            snowball_response = self.snowball.process_input(user_message)
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            snowball_response = "Oops! Something went wrong. Please try again later."

        self.display_message(snowball_response, sender='snowball')

    def display_message(self, message, sender='user'):
        tag = 'user' if sender == 'user' else 'snowball'
        self.chat_display.insert(tk.END, f"{sender.capitalize()}: {message}\n", tag)
        self.chat_display.see(tk.END)

        # Clear the input field if it's from the user
        if sender == 'user':
            self.user_input.delete(0, tk.END)

    def start_avatar_entry(self):
        try:
            # Play footsteps audio
            pygame.mixer.init()
            footsteps_path = os.path.join("S:/Snowball/storage/audio/footsteps.mp3")
            if os.path.exists(footsteps_path):
                pygame.mixer.music.load(footsteps_path)
                pygame.mixer.music.play()
            else:
                self.logger.error(f"Footsteps audio file not found at {footsteps_path}")
        except pygame.error as e:
            self.logger.error(f"Pygame Mixer Initialization Error: {e}")

        # Start moving the avatar from the right
        self.avatar_label.place(relx=1.0, rely=0.2)  # Start off-screen to the right
        self.master.after(100, lambda: self.move_avatar_slowly(target_relx=0.35))

    def move_avatar_slowly(self, target_relx, step=0.01):
        current_relx = self.avatar_label.winfo_x() / self.master.winfo_width()
        if current_relx > target_relx:
            new_relx = max(current_relx - step, target_relx)  # Ensure it doesn't move beyond target
            self.avatar_label.place(relx=new_relx, rely=0.2)
            self.master.after(50, lambda: self.move_avatar_slowly(target_relx))
        else:
            # Play greeting after avatar reaches target position
            self.greet_user()

    def greet_user(self):
        try:
            # Use the voice interface to generate and speak the greeting
            greeting = self.snowball.voice.generate_greeting()
            self.snowball.voice.speak(greeting)
        except Exception as e:
            self.logger.error(f"Error greeting user: {e}")

    def toggle_system_monitor(self):
        if self.system_monitor_var.get():
            self.chat_display.insert(tk.END, "System Monitor activated.\n")
            # Change avatar to monitoring placeholder
            self.avatar_label.configure(image=self.monitoring_avatar_image)
            self.avatar_label.place(relx=0.35, rely=0.2)

            if not hasattr(self, 'system_monitor_active') or not self.system_monitor_active:
                # Initialize and start the SystemMonitor here
                self.system_monitor_active = True
                self.start_system_monitor()
                self.logger.info("System Monitor started.")
        else:
            self.chat_display.insert(tk.END, "System Monitor deactivated.\n")
            # Change avatar back to default placeholder
            self.avatar_label.configure(image=self.snowball_avatar_image)
            self.avatar_label.place(relx=0.35, rely=0.2)

            if hasattr(self, 'system_monitor_active') and self.system_monitor_active:
                # Stop the SystemMonitor if it's active
                self.system_monitor_active = False
                self.stop_system_monitor()
                self.logger.info("System Monitor stopped.")

    def start_system_monitor(self):
        # Initialize SystemMonitor and start monitoring only when needed
        if not hasattr(self, 'system_monitor'):
            self.system_monitor = self.system_monitor
        self.system_monitor.monitor_system()

    def stop_system_monitor(self):
        if hasattr(self, 'system_monitor'):
            self.system_monitor.stop()
    
    def enable_buttons(self):
        # Enable any buttons or features that were disabled during initialization
        # Example: you could set `state=tk.NORMAL` to buttons if you had disabled them initially
        pass
    
if __name__ == "__main__":
    app = SnowballGUI(master, initializer)
    master.mainloop()
