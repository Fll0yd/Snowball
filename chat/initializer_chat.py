from chat.agent_chat import SnowballAI
from core.logger import SnowballLogger

class SnowballInitializer:
    """Minimal initializer to set up SnowballAI and logging."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SnowballInitializer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = SnowballLogger()
            self.logger.log_event("Logger initialized successfully.")
            self.snowball_ai = SnowballAI()
            self.initialized = True
