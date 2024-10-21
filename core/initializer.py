# initializer.py (S:/Snowball/core)

import os
import threading
import tkinter as tk
import time
from core.ai.agent import SnowballAI
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

            # Registry of initialized components
            self._components = {}

            # Initialize frequently used components
            self.initialize_core_components()
            self._snowball_ai = None
            self._memory = None
            self._system_monitor = None
            self._q_learning_agent = None
            self.voice_interface = self.initialize_voice_interface()
            self.file_monitor = self.initialize_file_monitor('S:/Snowball/config/plex_config.json')
            self.mobile_integration = self.initialize_mobile_integration()
            self.decision_maker = self.initialize_decision_maker()

            # Initialize AI Agent
            self.snowball_ai = self.initialize_ai_agent()

            # Initialize Reinforcement Learning Agent
            self.q_learning_agent = self.initialize_q_learning_agent(state_size=10, action_size=4)  # Placeholder values

            # Start Core Services
            self.start_core_services()

            # Set initialized flag
            self.initialized = True

    def _initialize_logger(self):
        logger = SnowballLogger()
        logger.log_event("Logger initialized successfully.")
        return logger

    def initialize_core_components(self):
        """Initialize core components and register them in the registry."""
        self._components['voice_interface'] = self.initialize_component('voice_interface', self.initialize_voice_interface)
        self._components['file_monitor'] = self.initialize_component('file_monitor', lambda: self.initialize_file_monitor('S:/Snowball/config/plex_config.json'))
        self._components['snowball_ai'] = self.initialize_component('snowball_ai', self.initialize_ai_agent)
        self._components['q_learning_agent'] = self.initialize_component('q_learning_agent', lambda: self.initialize_q_learning_agent(10, 4))  # Example state/action sizes

        # Start Core Services
        self.start_core_services()

    def initialize_component(self, name, initializer_fn):
        """Initialize and register a component, retrying if necessary."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                component = initializer_fn()
                self.logger.log_event(f"{name} initialized successfully.")
                return component
            except Exception as e:
                self.logger.log_error(f"Failed to initialize {name} (attempt {attempt + 1}): {e}")
                time.sleep(2)  # Delay before retrying
        self.logger.log_error(f"{name} could not be initialized after {max_retries} attempts.")
        return None

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

    def initialize_voice_interface(self):
        from core.ai.voice import VoiceInterface
        voice_interface = VoiceInterface(api_key=self.openai_api_key)
        self.logger.log_event("Voice Interface initialized successfully.")
        return voice_interface

    def initialize_file_monitor(self, config_file):
        from core.ai.file_manager import FileMonitor
        file_monitor = FileMonitor(config_file)
        self.logger.log_event("File Monitor initialized successfully.")
        return file_monitor

    def initialize_mobile_integration(self):
        from core.mobile_integration import MobileIntegration
        mobile_integration = MobileIntegration()
        self.logger.log_event("Mobile Integration initialized successfully.")
        return mobile_integration

    def initialize_decision_maker(self):
        from core.ai.decision_maker import DecisionMaker
        decision_maker = DecisionMaker()
        self.logger.log_event("Decision Maker initialized successfully.")
        return decision_maker

    def initialize_ai_agent(self):
        ai_agent = SnowballAI(api_key=self.openai_api_key)
        self.logger.log_event("Snowball AI Agent initialized successfully.")
        return ai_agent

    def initialize_q_learning_agent(self, state_size, action_size):
        from core.ai.reinforcement import QLearningAgent
        q_learning_agent = QLearningAgent(state_size, action_size)
        self.logger.log_event("Reinforcement Learning Agent initialized successfully.")
        return q_learning_agent

    def start_core_services(self):
        if self.file_monitor and self.snowball_ai:
            self.logger.log_event("Starting File Monitor Thread.")
            threading.Thread(target=self.file_monitor.start_monitoring, daemon=True).start()

            self.logger.log_event("Starting Snowball AI Interaction Loop.")
            threading.Thread(target=self.snowball_ai.interact, daemon=True).start()

            self.logger.log_event("Initialization complete. Snowball AI is now running.")
        else:
            self.logger.log_event("Core services could not be started due to missing components.", level="ERROR")

    def initialize_config_interface(self):
        master = tk.Tk()
        from interface.config_interface import ConfigInterface
        config_interface = ConfigInterface(master, self.snowball_ai, self.config_loader)
        return config_interface


if __name__ == "__main__":
    initializer = SnowballInitializer()
    # Example of how to initialize the config UI separately
    # config_interface = initializer.initialize_config_interface()
