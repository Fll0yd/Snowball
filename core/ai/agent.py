import os
import sys
import threading
import time
import json
import random

# Lazy import core components to prevent circular imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SnowballAI:
    def __init__(self):
        # Lazy initialization of core components to avoid circular imports
        self.initializer = None
        self.logger = None
        self.memory = None
        self.config_loader = None
        self.conversation_module = None
        self.sentiment_analysis_module = None
        self.vision_module = None
        self.decision_maker = None
        self.file_monitor = None
        self.reinforcement_module = None
        self.system_monitor = None
        self.voice_module = None
        self.running_event = threading.Event()
        
        # Initialize components when needed
        self._initialize_core_components()
        
        self.name = self.generate_name()
        self.logger.log_event("SnowballAI initialized with provided API key.")

    def _initialize_core_components(self):
        from core.initializer import SnowballInitializer
        
        self.initializer = SnowballInitializer()
        self.logger = self.initializer.logger
        self.memory = self.initializer.memory
        self.config_loader = self.initializer.config_loader
        self.conversation_module = self.initializer.snowball_ai.conversation
        self.sentiment_analysis_module = self.initializer.sentiment_analysis
        self.vision_module = self.initializer.vision
        self.decision_maker = self.initializer.decision_maker
        self.file_monitor = self.initializer.file_monitor
        self.reinforcement_module = self.initializer.q_learning_agent
        self.system_monitor = self.initializer.system_monitor
        self.voice_module = self.initializer.voice_interface

    def load_api_key(self):
        try:
            with open('S:/Snowball/config/account_integrations.json', 'r') as f:
                config = json.load(f)
                return config['api_keys'].get('openai_api_key')
        except FileNotFoundError as e:
            print(f"Error loading OpenAI API key: {e}")
            sys.exit(1)

    def generate_name(self):
        """Generate a name for the AI instance by considering suggestions from a .txt file."""
        names_file_path = 'S:/Snowball/docs/names.txt'
        suggested_names = []
        try:
            if os.path.exists(names_file_path):
                with open(names_file_path, 'r', encoding='utf-8') as file:
                    suggested_names = [line.strip() for line in file if line.strip()]
                self.logger.log_event(f"Loaded {len(suggested_names)} suggested names from {names_file_path}")
            else:
                self.logger.log_event(f"Names file not found at {names_file_path}")
        except Exception as e:
            self.logger.log_event(f"Error reading names file: {e}")

        if suggested_names and random.random() < 0.7:
            return random.choice(suggested_names)
        else:
            return self.conversation_module.generate_name(suggested_names)

    def start(self):
        """Main loop to start interaction, system monitoring, and multitasking."""
        self.logger.log_event(f"{self.name} started.")

        # Start threads for each module's main functionality
        threading.Thread(target=self.voice_module.listen_and_respond, args=(self.conversation_module,), daemon=True).start()
        threading.Thread(target=self.reinforcement_module.train, daemon=True).start()
        threading.Thread(target=self.push_notifications_loop, daemon=True).start()
        threading.Thread(target=self.vision_module.start_facial_recognition, daemon=True).start()
        threading.Thread(target=self.system_monitor_loop, daemon=True).start()
        threading.Thread(target=self.file_monitor.start_monitoring, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def push_notifications_loop(self):
        """Push notifications to the user on mobile."""
        while not self.running_event.is_set():
            self.logger.log_event("Initiating push notification cycle.")
            time.sleep(60)
            self.logger.log_event("Pushing notifications to the user...")

    def system_monitor_loop(self):
        """Monitor system health and send alerts when thresholds are crossed."""
        while not self.running_event.is_set():
            try:
                system_status = self.system_monitor.get_system_health()
                if system_status['alert']:
                    self.logger.log_event("System alert: " + system_status['message'])
                    self.voice_module.speak(system_status['message'])
            except Exception as e:
                self.logger.log_event(f"Error in system monitor loop: {e}")
            time.sleep(10)

    def heartbeat_loop(self):
        """Continuously monitor and log the status of all modules."""
        while not self.running_event.is_set():
            try:
                self.logger.log_event("Heartbeat check: All modules are being monitored...")
                # Example checks for modules
                if not self.voice_module.is_active():
                    self.logger.log_event("Warning: Voice Module is not active.")
                if not self.vision_module.is_active():
                    self.logger.log_event("Warning: Vision Module is not active.")
            except Exception as e:
                self.logger.log_event(f"Error in heartbeat loop: {e}")
            time.sleep(60)  # Perform status checks every 60 seconds

    def interact(self, user_input):
        """Process user input and generate a response."""
        try:
            sentiment = self.sentiment_analysis_module.analyze(user_input)
            facial_emotion = self.vision_module.get_current_emotion()
            self.logger.log_event(f"User sentiment: {sentiment}, Facial emotion: {facial_emotion}")

            response = self.get_best_response(user_input, sentiment, facial_emotion)
            self.logger.log_event(f"Generated response: {response}")
            self.voice_module.speak(response)
        except Exception as e:
            self.logger.log_event(f"Error during interaction: {e}")
            self.voice_module.speak("I'm sorry, something went wrong while processing your request.")

    def get_best_response(self, user_input, sentiment, facial_emotion):
        """Dynamically select the best response from multiple NLP models."""
        responses = [
            ("OpenAI", self.conversation_module.process_input(user_input)),
            ("GPT-J", self.conversation_module.process_input_with_gptj(user_input)),
            ("BERT", self.conversation_module.process_input_with_bert(user_input))
        ]
        # Rank responses based on sentiment analysis or other criteria
        responses_ranked = sorted(responses, key=lambda r: self.sentiment_analysis_module.analyze_response_quality(r[1]), reverse=True)
        best_response = responses_ranked[0]
        self.logger.log_event(f"Selected best response from {best_response[0]}: {best_response[1]}")
        return best_response[1]

    def run_reinforcement_learning(self):
        """Run the reinforcement learning module to train the AI in games."""
        self.logger.log_event("Starting reinforcement learning for games.")
        try:
            self.reinforcement_module.train()
        except Exception as e:
            self.logger.log_event(f"Error in reinforcement learning module: {e}")

    def toggle_module(self, module_name, enable=True):
        """Enable or disable individual AI modules."""
        modules = {
            'voice': self.voice_module,
            'vision': self.vision_module,
            'reinforcement': self.reinforcement_module
        }
        if module_name in modules:
            if enable:
                modules[module_name].start()
                self.logger.log_event(f"{module_name} module enabled.")
            else:
                modules[module_name].stop()
                self.logger.log_event(f"{module_name} module disabled.")
        else:
            self.logger.log_event(f"Module '{module_name}' not found.")

    def stop(self):
        """Gracefully stop all AI processes and threads."""
        self.logger.log_event("Shutting down SnowballAI...")
        self.running_event.set()  # Stop the main loop
        self.logger.log_event("SnowballAI has been shut down.")

if __name__ == "__main__":
    ai = SnowballAI()
    try:
        ai.start()
    except KeyboardInterrupt:
        ai.stop()
