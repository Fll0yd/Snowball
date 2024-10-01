import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import sys
sys.path.append('S:/core/')
from nlp_engine import NLPEngine

class SnowballGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snowball AI - Chat Interface")
        
        # Set the duck icon
        duck_icon = ImageTk.PhotoImage(file="S:/icon/trayicon.png")
        self.root.iconphoto(True, duck_icon)

        # Initialize NLP engine
        self.snowball = NLPEngine(config_path="S:/config/api_keys.json")

        # Set window background to dark grey
        self.root.configure(bg="#1e1e1e")
        
        # Create a Frame to contain the text area and scrollbar
        text_frame = tk.Frame(self.root, bg="#1e1e1e")
        text_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Create Chat Display with a darker background and white text
        self.chat_display = tk.Text(text_frame, width=80, height=20, wrap=tk.WORD, bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", font=("Arial", 14))
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.insert(tk.END, "Welcome! How can Snowball assist you today?\n")
        self.chat_display.tag_configure('user', foreground='lightblue')
        self.chat_display.tag_configure('snowball', foreground='lightgreen')
        
        # Configure row/column to ensure the text box resizes properly
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Create a custom scrollbar for the chat display
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScrollbar", gripcount=0,
                        background="#333333", darkcolor="#1e1e1e", lightcolor="#4a4a4a",
                        troughcolor="#1e1e1e", bordercolor="#4a4a4a", arrowcolor="white")
        
        # Add the scrollbar
        scroll_bar = ttk.Scrollbar(text_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scroll_bar.set)
        scroll_bar.grid(row=0, column=1, sticky="ns")

        # Create Input Field with lighter gray background
        self.user_input = tk.Entry(root, bg="#404040", fg="white", font=("Arial", 14), relief="flat", insertbackground="white")
        self.user_input.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Load and resize the send icon (up arrow)
        send_icon = Image.open("S:/icon/send.png")
        send_icon = send_icon.resize((40, 40), Image.Resampling.LANCZOS)
        send_icon = ImageTk.PhotoImage(send_icon)

        # Send Button with up arrow icon
        self.send_button = tk.Button(root, image=send_icon, command=self.send_input, bg="#1e1e1e", relief="flat", bd=0)
        self.send_button.grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.send_button.image = send_icon  # Keep reference to avoid garbage collection

        # Load and resize the attach icon (paperclip)
        attach_icon = Image.open("S:/icon/attach.png")
        attach_icon = attach_icon.resize((40, 40), Image.Resampling.LANCZOS)
        attach_icon = ImageTk.PhotoImage(attach_icon)

        # Attach Button for file attachment (left of the input field)
        self.attach_button = tk.Button(root, image=attach_icon, bg="#1e1e1e", relief="flat", bd=0)
        self.attach_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.attach_button.image = attach_icon  # Keep reference to avoid garbage collection

        # Load and resize the save icon
        save_icon = Image.open("S:/icon/save.png")
        save_icon = save_icon.resize((40, 40), Image.Resampling.LANCZOS)
        save_icon = ImageTk.PhotoImage(save_icon)

        # Save Button for saving chat (next to the send button)
        self.save_button = tk.Button(root, image=save_icon, command=self.save_chat, bg="#1e1e1e", relief="flat", bd=0)
        self.save_button.grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.save_button.image = save_icon  # Keep reference to avoid garbage collection

        # Bind Enter key to send message
        self.root.bind('<Return>', lambda event: self.send_input())

        # Grid weight to ensure proper resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def send_input(self):
        # Get the user's input
        user_message = self.user_input.get()
        if not user_message.strip():
            return  # Don't process empty inputs

        # Display the user's message in the chat
        self.display_message(user_message, sender='user')

        # Show "thinking" message while processing
        self.chat_display.insert(tk.END, "Snowball is thinking...\n")
        self.chat_display.see(tk.END)

        # Process the input through Snowball
        self.root.after(100, lambda: self.process_input(user_message))

    def process_input(self, user_message):
        try:
            snowball_response = self.snowball.process_input(user_message)
        except Exception as e:
            snowball_response = "Oops! Something went wrong."

        # Display Snowball's response
        self.display_message(snowball_response, sender='snowball')

    def display_message(self, message, sender='user'):
        tag = 'user' if sender == 'user' else 'snowball'
        self.chat_display.insert(tk.END, f"{sender.capitalize()}: {message}\n", tag)
        self.chat_display.see(tk.END)
        
        # Clear the input field if it's from the user
        if sender == 'user':
            self.user_input.delete(0, tk.END)

    def save_chat(self):
        """Save the chat history to a file."""
        with open("chat_history.txt", "w") as file:
            file.write(self.chat_display.get("1.0", tk.END))

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    gui = SnowballGUI(root)
    root.geometry("1250x950")
    root.mainloop()
