import sqlite3
import sys
import logging
import os
import threading
from datetime import datetime
from contextlib import closing
from cachetools import LRUCache

# Ensure the core directory is in the system path for logger import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logger import SnowballLogger

class MemoryError(Exception):
    """Custom exception for Memory class errors."""
    pass

class Memory:
    def __init__(self, db_path='data/memories.db'):
        self.logger = SnowballLogger()  # Initialize logger
        self.db_path = db_path
        self.cache = LRUCache(maxsize=1000)  # Limited cache for frequently accessed data
        self._db_lock = threading.Lock()  # Lock for database operations
        
        # Ensure the directory exists for the database
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        try:
            # Establish connection to the SQLite database
            self.conn = closing(sqlite3.connect(self.db_path, check_same_thread=False))  # Enable multi-threaded access
            self.logger.logger.info(f"Connected to SQLite database: {self.db_path}")
            self.create_table()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error connecting to SQLite database: {e}")
            raise MemoryError(f"Error connecting to SQLite database: {e}")

    def create_table(self):
        """Creates the interactions table if it doesn't exist, and adds indexes."""
        try:
            with self._db_lock:
                with self.conn:
                    self.conn.execute(''' 
                        CREATE TABLE IF NOT EXISTS interactions (
                            id INTEGER PRIMARY KEY,
                            user_input TEXT,
                            ai_response TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    # Create index on timestamp for faster queries
                    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)")
                self.logger.logger.info("Checked/created 'interactions' table and index.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error creating table: {e}")
            raise MemoryError(f"Error creating table: {e}")

    def store_interaction(self, user_input, ai_response):
        """Stores a user interaction in the database, with error handling."""
        try:
            with self._db_lock:
                with self.conn:
                    self.conn.execute(
                        "INSERT INTO interactions (user_input, ai_response) VALUES (?, ?)",
                        (user_input, ai_response)
                    )
                self.cache[user_input] = ai_response  # Cache interaction
                self.logger.logger.info(f"{self.__class__.__name__} - Stored interaction: User: '{user_input}', AI: '{ai_response}'")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error storing interaction: {e}")
            raise MemoryError(f"Error storing interaction: {e}")

    def store_batch_interactions(self, interactions):
        """Stores a batch of user interactions."""
        try:
            with self._db_lock:
                with self.conn:
                    self.conn.execute("BEGIN TRANSACTION")
                    self.conn.executemany(
                        "INSERT INTO interactions (user_input, ai_response) VALUES (?, ?)",
                        interactions
                    )
                    self.conn.execute("COMMIT")
                self.logger.logger.info(f"Stored batch of {len(interactions)} interactions.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error storing batch interactions: {e}")
            raise MemoryError(f"Error storing batch interactions: {e}")

    def get_interactions(self):
        """Retrieve all interactions from the database."""
        try:
            if 'all_interactions' in self.cache:
                return self.cache['all_interactions']  # Return from cache

            with self._db_lock:
                with self.conn:
                    cursor = self.conn.execute("SELECT * FROM interactions ORDER BY timestamp DESC")
                    interactions = cursor.fetchall()
                self.cache['all_interactions'] = interactions  # Cache result
                self.logger.logger.info(f"{self.__class__.__name__} - Retrieved all interactions.")
                return interactions
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving interactions: {e}")
            raise MemoryError(f"Error retrieving interactions: {e}")

    def get_last_interaction(self):
        """Retrieve the last interaction."""
        try:
            with self._db_lock:
                with self.conn:
                    cursor = self.conn.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT 1")
                    interaction = cursor.fetchone()
            if interaction:
                self.logger.logger.info(f"{self.__class__.__name__} - Retrieved last interaction: {interaction}")
            return interaction
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving last interaction: {e}")
            raise MemoryError(f"Error retrieving last interaction: {e}")

    def get_interactions_by_keyword(self, keyword):
        """Retrieve interactions containing a specific keyword."""
        try:
            if keyword in self.cache:
                return self.cache[keyword]  # Return cached result

            with self._db_lock:
                with self.conn:
                    cursor = self.conn.execute("SELECT * FROM interactions WHERE user_input LIKE ?", ('%' + keyword + '%',))
                    interactions = cursor.fetchall()
                self.cache[keyword] = interactions  # Cache result
                self.logger.logger.info(f"{self.__class__.__name__} - Retrieved interactions with keyword: '{keyword}'")
                return interactions
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving interactions by keyword: {e}")
            raise MemoryError(f"Error retrieving interactions by keyword: {e}")

    def clear_interactions(self):
        """Delete all interactions from the database."""
        try:
            with self._db_lock:
                with self.conn:
                    self.conn.execute("DELETE FROM interactions")
                self.logger.logger.info(f"{self.__class__.__name__} - Cleared all interactions from the database.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error clearing interactions: {e}")
            raise MemoryError(f"Error clearing interactions: {e}")

    def backup_database(self):
        """Create a backup of the database for recovery."""
        try:
            backup_file = f'data/memories_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            with open(self.db_path, 'rb') as original_db:
                with open(backup_file, 'wb') as backup_db:
                    backup_db.write(original_db.read())
            self.logger.logger.info(f"Database backup created at {backup_file}")
        except Exception as e:
            self.logger.log_error(f"Error backing up the database: {e}")
            raise MemoryError(f"Error backing up the database: {e}")

    def close_connection(self):
        """Closes the SQLite connection."""
        try:
            with self._db_lock:
                if self.conn:
                    self.conn.close()
                    self.logger.logger.info(f"{self.__class__.__name__} - Closed SQLite database connection.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error closing SQLite connection: {e}")
            raise MemoryError(f"Error closing SQLite connection: {e}")
