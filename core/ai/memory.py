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
                self.logger.log_memory(f"Connected to SQLite database: {self.db_path}")
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
                                    file_size INTEGER,
                                    tags TEXT,
                                    file_type TEXT,
                                    checksum TEXT,
                                    analysis_result TEXT
                                )''')
                cursor.execute('''CREATE INDEX IF NOT EXISTS idx_file_metadata_name ON file_metadata (name)''')
                cursor.execute('''CREATE INDEX IF NOT EXISTS idx_file_metadata_size ON file_metadata (file_size)''')
                cursor.execute('''CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions (timestamp)''')
                if self.logger:
                    self.logger.log_memory("Created/checked tables and indexes.")
        except sqlite3.Error as e:
            if self.logger:
                self.logger.log_error(f"Error creating tables: {e}")

    def search_files_by_tags(self, tags):
        """Search files by tags."""
        try:
            tag_query = " OR ".join(["tags LIKE ?"] * len(tags))
            params = [f"%{tag}%" for tag in tags]
            with self._get_cursor() as cursor:
                cursor.execute(f"SELECT * FROM file_metadata WHERE {tag_query}", params)
                results = cursor.fetchall()
            self.logger.log_memory(f"Retrieved {len(results)} files matching tags: {tags}")
            return results
        except sqlite3.Error as e:
            self.logger.log_error(f"Error searching files by tags '{tags}': {e}")
            return []

    def store_interaction(self, user_input, ai_response, query_type="General"):
        """Store a user interaction in the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO interactions (user_input, ai_response, query_type) VALUES (?, ?, ?)",
                    (user_input, ai_response, query_type)
                )
            if self.logger:
                self.logger.log_memory(f"Stored interaction: User: '{user_input}', AI: '{ai_response}', Type: '{query_type}'")
        except MemoryError as e:
            if self.logger:
                self.logger.log_error(f"Error storing interaction: {e}")
    
    def get_interactions(self, query_type=None, start_time=None, end_time=None, limit=100, offset=0):
        """Retrieve interactions with optional filters."""
        try:
            query = "SELECT * FROM interactions WHERE 1=1"
            params = []
            if query_type:
                query += " AND query_type = ?"
                params.append(query_type)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            with self._get_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()

            if self.logger:
                self.logger.log_memory(f"Retrieved {len(results)} interactions matching filters.")
            return results
        except sqlite3.Error as e:
            self.logger.log_error(f"Error retrieving interactions: {e}")
            return []
    
    def store_file_metadata(self, file_name, file_path, last_modified, file_size=None, tags=None, analysis_result=None):
        """Store or update file metadata in the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO file_metadata (name, path, last_modified, file_size, tags, analysis_result)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        last_modified = excluded.last_modified,
                        file_size = excluded.file_size,
                        tags = excluded.tags,
                        analysis_result = excluded.analysis_result
                    """,
                    (file_name, file_path, last_modified, file_size, tags, analysis_result)
                )
            if self.logger:
                self.logger.log_memory(
                    f"Stored metadata for file: {file_name}, Size: {file_size}, Tags: {tags}"
                )
        except sqlite3.Error as e:
            self.logger.log_error(f"Error storing or updating file metadata: {e}")

    def search_files(self, keyword):
        """Search indexed files by keyword with caching."""
        if keyword in self.metadata_cache:
            self.logger.log_memory(f"Cache hit for file search: '{keyword}'")
            return self.metadata_cache[keyword]

        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM file_metadata WHERE name LIKE ? OR path LIKE ?",
                    (f"%{keyword}%", f"%{keyword}%")
                )
                results = cursor.fetchall()
            self.metadata_cache[keyword] = results
            self.logger.log_memory(f"Retrieved {len(results)} files matching keyword: '{keyword}'")
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
                self.logger.log_memory(f"Retrieved last interaction: {interaction}")
            return interaction
        except MemoryError as e:
            if self.logger:
                self.logger.log_error(f"Error retrieving last interaction: {e}")

    def archive_old_interactions(self, days=30, archive_table="archived_interactions"):
        """Archive old interactions instead of deleting them."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            with self._get_cursor() as cursor:
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {archive_table} AS SELECT * FROM interactions WHERE 1=0
                ''')
                cursor.execute(f'''
                    INSERT INTO {archive_table} SELECT * FROM interactions WHERE timestamp < ?
                ''', (cutoff_date,))
                cursor.execute("DELETE FROM interactions WHERE timestamp < ?", (cutoff_date,))
                rows_archived = cursor.rowcount
            if self.logger:
                self.logger.log_memory(f"Archived {rows_archived} interactions older than {days} days.")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error archiving old interactions: {e}")

    def close(self):
        """Close the database connection properly."""
        self.conn.close()
        if self.logger:
            self.logger.log_memory("Closed database connection.")
