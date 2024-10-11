    def display_log_buttons(self):
        """
        Display buttons for each log file available, arranged in rows of three.
        """
        logs_path = 'S:/Snowball/storage/logs'
        if hasattr(self, 'log_buttons_frame'):
            self.log_buttons_frame.pack_forget()  # Remove any existing log buttons frame

        self.log_buttons_frame = tk.Frame(self.main_frame, bg="#2c2c2c")
        self.log_buttons_frame.pack(pady=10)

        log_file_mapping = {
            "Decision Log": "decision_logs/decision_log.txt",
            "Error Log": "error_logs/error_log.txt",
            "Event Log": "event_logs/event_log.txt",
            "File Log": "file_io_logs/file_io_log.txt",
            "Interaction Log": "interaction_logs/interaction_log.txt",
            "CPU Log": "system_health_logs/cpu_log.txt",
            "Memory Log": "system_health_logs/memory_log.txt",
            "Config Log": "config_logs/config_log.txt",
            "Security Log": "security_logs/security_log.txt",
            "Task Log": "task_logs/task_log.txt",
            "Warning Log": "warning_logs/warning_log.txt"
        }

        # Rearrange buttons into rows of three
        row = 0
        col = 0
        for log_name, log_file in log_file_mapping.items():
            button = tk.Button(self.log_buttons_frame, text=log_name, command=lambda lf=log_file: self.load_log_file(lf),
                               bg="#4d4d4d", fg="white", font=("Arial", 12), relief="flat", width=20, pady=5)
            button.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 2:  # Create a new row after every three buttons
                col = 0
                row += 1

    def load_log_file(self, log_file):
        """
        Load the contents of the selected log file into the text box.
        """
        logs_path = 'S:/Snowball/storage/logs'
        full_path = os.path.join(logs_path, log_file)

        if not os.access(full_path, os.R_OK):
            messagebox.showerror("Error", f"Cannot read log file: '{full_path}'. Check file permissions.")
            return

        try:
            with open(full_path, 'r') as f:
                log_content = f.read()
                for widget in self.config_widgets_frame.winfo_children():
                    widget.destroy()
                self.config_widgets_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
                text_box = tk.Text(self.config_widgets_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#3e3e3e", fg="white", relief="flat")
                text_box.insert(tk.END, log_content)
                text_box.pack(fill=tk.BOTH, expand=True)
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: '{full_path}'")
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: '{full_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")