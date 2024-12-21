import sqlite3
import os
import threading
from datetime import datetime, timedelta
from cachetools import LRUCache
from contextlib import contextmanager
from Snowball.core.ai.file_manager import FileManager

class MemoryError(Exception):
    pass

class Memory:
    def __init__(self, db_path='S:/Snowball/storage/data/memories.db', logger=None):
        self.logger = logger
        self.db_path = db_path
        self.cache = LRUCache(maxsize=1000)
        self.metadata_cache = LRUCache(maxsize=500)
        self._db_lock = threading.Lock()
        self.scan_dir = 'S:/'

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            if self.logger:
                self.logger.log_event(f"Connected to SQLite database: {self.db_path}")
            self.create_tables()
        except sqlite3.Error as e:
            if self.logger:
                self.logger.log_error(f"Error connecting to SQLite database: {e}")
            raise MemoryError(f"Error connecting to SQLite database: {e}")

        # Initialize FileManager
        self.file_manager = FileManager(logger=self.logger, memory=self, scan_dir=self.scan_dir)
        self.file_manager.start_monitoring()

    @contextmanager
    def _get_cursor(self):
        """Context manager to handle database connection and ensure thread safety."""
        with self._db_lock:
            cursor = self.conn.cursor()
            try:
                yield cursor
                self.conn.commit()
            except sqlite3.Error as e:
                self.conn.rollback()
                if self.logger:
                    self.logger.log_error(f"Database error: {e}")
                raise MemoryError(f"Database operation failed: {e}")
            finally:
                cursor.close()

    def create_tables(self):
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS interactions (
                                    id INTEGER PRIMARY KEY,
                                    user_input TEXT,
                                    ai_response TEXT,
                                    query_type TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                                )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS file_metadata (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    path TEXT UNIQUE,
                                    last_modified DATETIME,
                                    analysis_result TEXT
                                )''')
                if self.logger:
                    self.logger.log_event("Created/checked tables: 'interactions', 'file_metadata'.")
        except MemoryError as e:
            if self.logger:
                self.logger.log_error(f"Error creating tables: {e}")

    def store_interaction(self, user_input, ai_response, query_type="General"):
        """Store a user interaction in the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO interactions (user_input, ai_response, query_type) VALUES (?, ?, ?)",
                    (user_input, ai_response, query_type)
                )
            if self.logger:
                self.logger.log_event(f"Stored interaction: User: '{user_input}', AI: '{ai_response}', Type: '{query_type}'")
        except MemoryError as e:
            if self.logger:
                self.logger.log_error(f"Error storing interaction: {e}")

    def store_file_metadata(self, file_name, file_path, last_modified, analysis_result=None):
        """Store or update file metadata in the database with logging."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO file_metadata (name, path, last_modified, analysis_result)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        last_modified = excluded.last_modified,
                        analysis_result = excluded.analysis_result
                    """,
                    (file_name, file_path, last_modified, analysis_result)
                )
            self.logger.log_event(f"Indexed or updated file: {file_name} at {file_path} (Last Modified: {last_modified})")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error storing or updating file metadata: {e}")

    def search_files(self, keyword):
        """Search indexed files by keyword."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM file_metadata WHERE name LIKE ? OR path LIKE ?",
                    (f"%{keyword}%", f"%{keyword}%")
                )
                results = cursor.fetchall()
            self.logger.log_event(f"Retrieved {len(results)} files matching keyword: '{keyword}'")
            return results
        except sqlite3.Error as e:
            self.logger.log_error(f"Error searching files by keyword '{keyword}': {e}")
            return []

    def get_last_interaction(self):
        """Retrieve the last interaction."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT 1")
                interaction = cursor.fetchone()
            if interaction and self.logger:
                self.logger.log_event(f"Retrieved last interaction: {interaction}")
            return interaction
        except MemoryError as e:
            if self.logger:
                self.logger.log_error(f"Error retrieving last interaction: {e}")

    def clean_old_interactions(self, days=30):
        """Clean old interactions from the database."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            with self._get_cursor() as cursor:
                cursor.execute("DELETE FROM interactions WHERE timestamp < ?", (cutoff_date,))
                rows_deleted = cursor.rowcount
            self.logger.log_event(f"Cleaned {rows_deleted} interactions older than {days} days.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error cleaning old interactions: {e}")

    def close(self):
        """Close the database connection properly."""
        self.conn.close()
        if self.logger:
            self.logger.log_event("Closed database connection.")
