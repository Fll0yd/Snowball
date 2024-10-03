import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import importlib.util
import sys
import os

# Ensure the root directory is in the sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
sys.path.append(os.path.join(root_dir, '..'))  # Add the parent directory

from core import ai_agent, decision_maker  # Import from core now

# Print the current working directory for debugging purposes
print("Current working directory:", os.getcwd())
print("Current sys.path:", sys.path)

# Define the full path to your ai_agent module
module_path = 'ai_agent.py'  # File name since we're in the core directory

# Load the module from the specified path
try:
    module_full_path = os.path.join(root_dir, module_path)
    print(f"Loading module from: {module_full_path}")  # Debug statement
    spec = importlib.util.spec_from_file_location("SnowballAI", module_full_path)
    SnowballAI = importlib.util.module_from_spec(spec)
    sys.modules["SnowballAI"] = SnowballAI
    spec.loader.exec_module(SnowballAI)
except Exception as e:
    print("Error loading module:", e)

class SnowballGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snowball AI - Main Menu")
        
        # Set the main window's dimensions and background color
        self.root.geometry("1250x950")
        self.root.configure(bg="#1e1e1e")  # Dark background

        # Load background image
        try:
            self.background_image = Image.open("S:/Snowball/icon/background.png")  # Path to background image
            self.background_image = self.background_image.resize((1250, 950), Image.Resampling.LANCZOS)
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = tk.Label(self.root, image=self.background_photo)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover the entire window
        except Exception as e:
            print("Error loading background image:", e)

        # Load the AI character image
        try:
            self.character_image = Image.open("S:/Snowball/icon/character_placeholder.png")  # Path to AI character image
            self.character_image = self.character_image.resize((300, 500), Image.Resampling.LANCZOS)
            self.character_photo = ImageTk.PhotoImage(self.character_image)

            self.character_label = tk.Label(self.root, image=self.character_photo, bg="#1e1e1e")
            self.character_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)  # Center character in the window
        except Exception as e:
            print("Error loading character image:", e)

        # Create a Frame for buttons
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(side=tk.BOTTOM, pady=50)  # Position at the bottom

        # Create buttons for "Games," "System Monitor," and "Chat"
        self.games_button = tk.Button(button_frame, text="Games", command=self.open_games,
                                       bg="#4a4a4a", fg="white", font=("Arial", 16), width=15)
        self.system_monitor_button = tk.Button(button_frame, text="System Monitor", command=self.open_system_monitor,
                                               bg="#4a4a4a", fg="white", font=("Arial", 16), width=15)
        self.chat_button = tk.Button(button_frame, text="Chat", command=self.open_chat,
                                     bg="#4a4a4a", fg="white", font=("Arial", 16), width=15)

        # Place buttons in the button frame
        self.games_button.pack(side=tk.LEFT, padx=20)
        self.system_monitor_button.pack(side=tk.LEFT, padx=20)
        self.chat_button.pack(side=tk.LEFT, padx=20)

    def open_games(self):
        print("Opening Games interface...")  # Placeholder functionality

    def open_system_monitor(self):
        print("Opening System Monitor interface...")  # Placeholder functionality

    def open_chat(self):
        print("Opening Chat interface...")  # Placeholder functionality

if __name__ == "__main__":
    root = tk.Tk()
    gui = SnowballGUI(root)
    root.mainloop()
