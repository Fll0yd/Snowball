import json
import os
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigLoader:
    _cache = {}
    DEFAULT_CONFIG_DIR = os.environ.get("CONFIG_DIR", "S:/Snowball/config")

    @classmethod
    def load_config(cls, file_name: str, force_reload: bool = False, config_dir: Optional[str] = None) -> dict:
        """
        Loads the JSON configuration file and returns the data as a dictionary.
        Caches the file data to prevent reloading it multiple times, unless forced.

        :param file_name: The name of the JSON file (with extension).
        :param force_reload: Boolean flag to force reload from disk, bypassing the cache.
        :param config_dir: Optionally specify a custom config directory, otherwise uses default.
        :return: Dictionary of the loaded configuration.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        if file_name in cls._cache and not force_reload:
            logger.info(f"Loading configuration from cache: {file_name}")
            return cls._cache[file_name]

        # Use custom directory if provided, otherwise use default
        config_dir = config_dir or cls.DEFAULT_CONFIG_DIR
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
        except IOError as e:
            logger.error(f"IOError while opening file {file_name}: {e}")
            raise

    @classmethod
    def clear_cache(cls):
        """
        Clears the configuration cache for all files, forcing a reload on the next load.
        """
        cls._cache.clear()
        logger.info("Configuration cache cleared.")

    @classmethod
    def remove_from_cache(cls, file_name: str):
        """
        Removes a specific configuration file from the cache.
        
        :param file_name: The name of the configuration file to remove from the cache.
        """
        if file_name in cls._cache:
            del cls._cache[file_name]
            logger.info(f"Configuration for {file_name} removed from cache.")
        else:
            logger.info(f"No cached configuration found for {file_name}.")

    @classmethod
    def cache_status(cls) -> list:
        """
        Returns the current status of the cache (which files are cached).

        :return: List of cached files.
        """
        logger.info(f"Current cache status: {cls._cache.keys()}")
        return list(cls._cache.keys())

    @classmethod
    def save_config(cls, file_name: str, config_data: dict, config_dir: Optional[str] = None):
        """
        Saves the configuration data to the specified JSON file.

        :param file_name: The name of the JSON file (with extension).
        :param config_data: The dictionary data to save as JSON.
        :param config_dir: Optionally specify a custom config directory, otherwise uses default.
        :raises IOError: If the file cannot be written.
        """
        config_dir = config_dir or cls.DEFAULT_CONFIG_DIR
        file_path = os.path.join(config_dir, file_name)

        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
                logger.info(f"Configuration saved to {file_path}")
        except IOError as e:
            logger.error(f"Failed to write configuration to {file_path}: {e}")
            raise

    @classmethod
    def refresh_config(cls, file_name: str, config_dir: Optional[str] = None) -> dict:
        """
        Forces a cache refresh by reloading the configuration file from disk.

        :param file_name: The name of the JSON file (with extension).
        :param config_dir: Optionally specify a custom config directory, otherwise uses default.
        :return: Dictionary of the reloaded configuration.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        logger.info(f"Refreshing configuration for {file_name}")
        return cls.load_config(file_name, force_reload=True, config_dir=config_dir)

# Example usage:
if __name__ == "__main__":
    try:
        # Load the config file, forcing a reload from disk
        config = ConfigLoader.load_config("user_customizations.json", force_reload=True)
        print(config)

        # Check the current cache status
        print("Cached files:", ConfigLoader.cache_status())

        # Load the config file without forcing reload (should come from cache)
        config_cached = ConfigLoader.load_config("user_customizations.json")
        print(config_cached)

        # Clear the entire cache
        ConfigLoader.clear_cache()

        # Check the cache status after clearing
        print("Cached files after clearing:", ConfigLoader.cache_status())

        # Save new configuration data to a file
        new_config_data = {"new_setting": "example_value"}
        ConfigLoader.save_config("new_config.json", new_config_data)

        # Force refresh and load new configuration
        new_config = ConfigLoader.refresh_config("new_config.json")
        print(new_config)

    except Exception as e:
        logger.error(f"Error: {e}")
