import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigLoader:
    _cache = {}

    @classmethod
    def load_config(cls, file_name: str) -> dict:
        """
        Loads the JSON configuration file and returns the data as a dictionary.

        :param file_name: The name of the JSON file (with extension).
        :return: Dictionary of the loaded configuration.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        if file_name in cls._cache:
            logger.info(f"Loading configuration from cache: {file_name}")
            return cls._cache[file_name]

        config_dir = os.environ.get("CONFIG_DIR", "S:/config")  # Use environment variable if set
        file_path = os.path.join(config_dir, file_name)

        if not os.path.exists(file_path):
            logger.error(f"Configuration file {file_name} not found in {config_dir}")
            raise FileNotFoundError(f"Configuration file {file_name} not found in {config_dir}")

        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
                cls._cache[file_name] = config_data  # Cache the loaded config
                logger.info(f"Successfully loaded configuration: {file_name}")
                return config_data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from file {file_name}: {e}")
            raise
