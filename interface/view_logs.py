import tkinter as tk
from tkinter import messagebox, scrolledtext
import os

# Define the path to the log files directory
logs_directory = 'S:/Snowball/storage/logs'

class LogsViewer:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1200x800")
        self.master.title("Snowball AI - Logs Viewer")
        self.master.configure(bg="#2c2c2c")

        # Sidebar setup for log file buttons
        self.sidebar_frame = tk.Frame(self.master, bg="#1e1e1e", width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights to stretch the sidebar evenly
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=4)
        self.master.grid_rowconfigure(0, weight=1)

        # Create a frame for displaying the log contents
        self.main_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Label for main content
        self.header_label = tk.Label(self.main_frame, text="Log Viewer", font=("Arial", 16), fg="white", bg="#2c2c2c")
        self.header_label.pack(anchor="nw", pady=10)

        # Text area for displaying the log content
        self.log_text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, font=("Consolas", 12), bg="#3e3e3e", fg="white", relief="flat")
        self.log_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create buttons for each log file dynamically
        self.load_log_buttons()

    def load_log_buttons(self):
        """
        Load buttons for each log file in the logs directory.
        """
        try:
            for i, subdir in enumerate(os.listdir(logs_directory)):
                subdir_path = os.path.join(logs_directory, subdir)
                if os.path.isdir(subdir_path):
                    # Create buttons for each subdirectory (log type)
                    button = tk.Button(self.sidebar_frame, text=subdir.replace('_', ' ').title(),
                                       command=lambda p=subdir_path: self.load_log_file(p),
                                       bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=18)
                    button.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
                    self.sidebar_frame.grid_rowconfigure(i, weight=1)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Logs directory not found at {logs_directory}. Please check the path.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading logs: {e}")

    def load_log_file(self, log_directory):
        """
        Load the contents of the selected log file and display it in the text area.
        """
        # Find the most recent log file in the selected directory
        try:
            log_files = [f for f in os.listdir(log_directory) if os.path.isfile(os.path.join(log_directory, f))]
            if not log_files:
                self.log_text_area.delete(1.0, tk.END)
                self.log_text_area.insert(tk.END, "No log files found in this directory.")
                return

            # Sort log files by modification date (most recent first)
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
            latest_log_file = os.path.join(log_directory, log_files[0])

            # Read and display the contents of the most recent log file
            with open(latest_log_file, 'r') as f:
                log_content = f.read()
                self.log_text_area.delete(1.0, tk.END)
                self.log_text_area.insert(tk.END, log_content)
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: Unable to read files in '{log_directory}'")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Log directory '{log_directory}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the log file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogsViewer(root)
    root.mainloop()