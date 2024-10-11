import tkinter as tk
from tkinter import messagebox, Scrollbar
import os

# Define the path to the log files directory
logs_directory = 'S:/Snowball/storage/logs'

class LogsConfig:
    def __init__(self, master):
        self.master = master
        self.master.configure(bg="#2c2c2c")

        # Main container for log buttons and log viewer
        self.log_buttons_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.log_buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.log_view_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.log_view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create buttons for each log folder
        self.create_log_buttons()

    def create_log_buttons(self):
        """
        Create buttons for each log folder in the logs directory.
        """
        if not os.path.exists(logs_directory):
            messagebox.showerror("Error", f"Logs path '{logs_directory}' not found.")
            return

        log_dirs = [d for d in os.listdir(logs_directory) if os.path.isdir(os.path.join(logs_directory, d))]

        for i, log_dir in enumerate(log_dirs):
            button = tk.Button(self.log_buttons_frame, text=log_dir.replace('_', ' ').title(),
                               command=lambda d=log_dir: self.display_log_files(d),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20)
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)

    def display_log_files(self, log_dir):
        """
        Display the log files from the selected directory.
        """
        # Clear the current log view
        for widget in self.log_view_frame.winfo_children():
            widget.destroy()

        # Get the path to the selected log directory
        log_dir_path = os.path.join(logs_directory, log_dir)
        log_files = [f for f in os.listdir(log_dir_path) if os.path.isfile(os.path.join(log_dir_path, f))]

        if not log_files:
            messagebox.showinfo("No Logs", f"No log files found in '{log_dir}'.")
            return

        # Create a scrollable text widget to display the content of the selected log file
        self.log_text = tk.Text(self.log_view_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#3e3e3e", fg="white", relief="flat")
        self.scrollbar = Scrollbar(self.log_view_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display the most recent log file by default
        log_files.sort(reverse=True)  # Sort by file name (assuming timestamped names)
        self.load_log_content(os.path.join(log_dir_path, log_files[0]))

    def load_log_content(self, file_path):
        """
        Load the content of the selected log file into the text widget.
        """
        try:
            with open(file_path, 'r') as log_file:
                log_content = log_file.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read log file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogsConfig(root)
    root.mainloop()