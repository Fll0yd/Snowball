import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from core.logger import SnowballLogger
from core.config_loader import ConfigLoader

class SnowballInitializer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SnowballInitializer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = self._initialize_logger()
            self.config_loader = ConfigLoader()

            # Extract API keys from the loaded `account_integrations.json`
            self.account_integrations = self.config_loader.load_config('S:/Snowball/config/account_integrations.json')
            self.openai_api_key = self.account_integrations['api_keys'].get('openai_api_key', 'YOUR_API_KEY_HERE')

            # Initialize frequently used components concurrently
            self.initialize_core_components()

            # Set initialized flag
            self.initialized = True

    def _initialize_logger(self):
        logger = SnowballLogger()
        logger.log_event("Logger initialized successfully.")
        return logger

    def initialize_core_components(self):
        """Initialize core components concurrently with detailed logging."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'voice_interface': executor.submit(self.initialize_voice_interface),
                'file_monitor': executor.submit(self.initialize_file_monitor, 'S:/Snowball/config/plex_config.json'),
                'snowball_ai': executor.submit(self.initialize_ai_agent),
                'q_learning_agent': executor.submit(self.initialize_q_learning_agent, 10, 4)  # Example state/action sizes
            }

            self._components = {}

            for name, future in futures.items():
                try:
                    self.logger.log_event(f"Attempting to initialize {name}...")
                    self._components[name] = future.result(timeout=10)  # Timeout after 10 seconds
                    self.logger.log_event(f"{name} initialized successfully.")
                except Exception as e:
                    self.logger.log_error(f"Failed to initialize {name}: {e}")
                    # Add stack trace to understand where it failed
                    import traceback
                    self.logger.log_error(traceback.format_exc())

        # Start Core Services after initializing all components
        self.start_core_services()

    def start_core_services(self):
        """Start all registered core services."""
        try:
            if self._components.get('file_monitor') and self._components.get('snowball_ai'):
                self.logger.log_event("Starting File Monitor Thread.")
                threading.Thread(target=self._components['file_monitor'].start_monitoring, daemon=True).start()

                self.logger.log_event("Starting Snowball AI Interaction Loop.")
                threading.Thread(target=self._components['snowball_ai'].interact, daemon=True).start()

                self.logger.log_event("Initialization complete. Snowball AI is now running.")
            else:
                self.logger.log_error("Core services could not be started due to missing components.")
        except Exception as e:
            self.logger.log_error(f"Error starting core services: {e}")

    def shutdown(self):
        """Gracefully shutdown all core services and components."""
        self.logger.log_event("Shutting down SnowballInitializer and all components.")
        # Implement logic for stopping threads and releasing resources here.
        # e.g., stopping file monitor, saving state, etc.

    # Initialization functions for individual components with additional debug logging
    def initialize_voice_interface(self):
        from core.ai.voice import VoiceInterface  # Deferred import to avoid circular dependencies
        self.logger.log_event("Initializing Voice Interface...")
        voice_interface = VoiceInterface(api_key=self.openai_api_key)
        self.logger.log_event("Voice Interface initialized successfully.")
        return voice_interface

    def initialize_file_monitor(self, config_file):
        from core.ai.file_manager import FileMonitor  # Deferred import to avoid circular dependencies
        self.logger.log_event(f"Initializing File Monitor with config file: {config_file}...")
        file_monitor = FileMonitor(config_file)
        self.logger.log_event("File Monitor initialized successfully.")
        return file_monitor

    def initialize_mobile_integration(self):
        from core.mobile_integration import MobileIntegration  # Deferred import to avoid circular dependencies
        self.logger.log_event("Initializing Mobile Integration...")
        mobile_integration = MobileIntegration()
        self.logger.log_event("Mobile Integration initialized successfully.")
        return mobile_integration

    def initialize_decision_maker(self):
        from core.ai.decision_maker import DecisionMaker  # Deferred import to avoid circular dependencies
        self.logger.log_event("Initializing Decision Maker...")
        decision_maker = DecisionMaker()
        self.logger.log_event("Decision Maker initialized successfully.")
        return decision_maker

    def initialize_ai_agent(self):
        from core.ai.agent import SnowballAI  # Deferred import to avoid circular dependencies
        self.logger.log_event("Initializing Snowball AI Agent...")
        ai_agent = SnowballAI(api_key=self.openai_api_key)
        self.logger.log_event("Snowball AI Agent initialized successfully.")
        return ai_agent

    def initialize_q_learning_agent(self, state_size, action_size):
        from core.ai.reinforcement import QLearningAgent  # Deferred import to avoid circular dependencies
        self.logger.log_event(f"Initializing Q-Learning Agent with state size: {state_size}, action size: {action_size}...")
        q_learning_agent = QLearningAgent(state_size, action_size)
        self.logger.log_event("Reinforcement Learning Agent initialized successfully.")
        return q_learning_agent

if __name__ == "__main__":
    initializer = SnowballInitializer()
    # Example of how to initialize the config UI separately
    # config_interface = initializer.initialize_config_interface()
