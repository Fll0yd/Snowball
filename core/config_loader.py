import json
import os
import logging
from typing import Optional
from core.logger import SnowballLogger  # Use the SnowballLogger for enhanced logging

class ConfigLoader:
    _cache = {}
    DEFAULT_CONFIG_DIR = os.environ.get("CONFIG_DIR", "S:/Snowball/config")

    def __init__(self):
        self.logger = SnowballLogger()

    @staticmethod
    def load_config(file_name: str, force_reload: bool = False, config_dir: Optional[str] = None) -> dict:
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
        config_dir = config_dir or ConfigLoader.DEFAULT_CONFIG_DIR
        file_path = os.path.join(config_dir, file_name)

        if not os.path.exists(file_path):
            SnowballLogger().log_error(f"Configuration file {file_name} not found in {config_dir}")
            raise FileNotFoundError(f"Configuration file {file_name} not found in {config_dir}")

        if file_name in ConfigLoader._cache and not force_reload:
            SnowballLogger().logger.info(f"Loading configuration from cache: {file_name}")
            return ConfigLoader._cache[file_name]

        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
                ConfigLoader._cache[file_name] = config_data  # Cache the loaded config
                SnowballLogger().logger.info(f"Successfully loaded configuration: {file_name}")
                return config_data
        except json.JSONDecodeError as e:
            SnowballLogger().log_error(f"Error decoding JSON from file {file_name}: {e}")
            raise
        except IOError as e:
            SnowballLogger().log_error(f"IOError while opening file {file_name}: {e}")
            raise

    def clear_cache(self):
        """
        Clears the configuration cache for all files, forcing a reload on the next load.
        """
        ConfigLoader._cache.clear()
        self.logger.logger.info("Configuration cache cleared.")

    def remove_from_cache(self, file_name: str):
        """
        Removes a specific configuration file from the cache.

        :param file_name: The name of the configuration file to remove from the cache.
        """
        if file_name in ConfigLoader._cache:
            del ConfigLoader._cache[file_name]
            self.logger.logger.info(f"Configuration for {file_name} removed from cache.")
        else:
            self.logger.logger.info(f"No cached configuration found for {file_name}.")

    def cache_status(self) -> list:
        """
        Returns the current status of the cache (which files are cached).

        :return: List of cached files.
        """
        self.logger.logger.info(f"Current cache status: {ConfigLoader._cache.keys()}")
        return list(ConfigLoader._cache.keys())

    def save_config(self, file_name: str, config_data: dict, config_dir: Optional[str] = None):
        """
        Saves the configuration data to the specified JSON file.

        :param file_name: The name of the JSON file (with extension).
        :param config_data: The dictionary data to save as JSON.
        :param config_dir: Optionally specify a custom config directory, otherwise uses default.
        :raises IOError: If the file cannot be written.
        """
        config_dir = config_dir or ConfigLoader.DEFAULT_CONFIG_DIR
        file_path = os.path.join(config_dir, file_name)

        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
                ConfigLoader._cache[file_name] = config_data  # Update the cache
                self.logger.logger.info(f"Configuration saved to {file_path}")
        except IOError as e:
            self.logger.log_error(f"Failed to write configuration to {file_path}: {e}")
            raise

    def refresh_config(self, file_name: str, config_dir: Optional[str] = None) -> dict:
        """
        Forces a cache refresh by reloading the configuration file from disk.

        :param file_name: The name of the JSON file (with extension).
        :param config_dir: Optionally specify a custom config directory, otherwise uses default.
        :return: Dictionary of the reloaded configuration.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        self.logger.logger.info(f"Refreshing configuration for {file_name}")
        return self.load_config(file_name, force_reload=True, config_dir=config_dir)

# Example usage:
if __name__ == "__main__":
    config_loader = ConfigLoader()
    try:
        # Load the config file, forcing a reload from disk
        config = config_loader.load_config("user_customizations.json", force_reload=True)
        print(config)

        # Check the current cache status
        print("Cached files:", config_loader.cache_status())

        # Load the config file without forcing reload (should come from cache)
        config_cached = config_loader.load_config("user_customizations.json")
        print(config_cached)

        # Clear the entire cache
        config_loader.clear_cache()

        # Check the cache status after clearing
        print("Cached files after clearing:", config_loader.cache_status())

        # Save new configuration data to a file
        new_config_data = {"new_setting": "example_value"}
        config_loader.save_config("new_config.json", new_config_data)

        # Force refresh and load new configuration
        new_config = config_loader.refresh_config("new_config.json")
        print(new_config)

    except Exception as e:
        config_loader.logger.log_error(f"Error: {e}")