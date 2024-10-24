# memory.py (S:/Snowball/core)
 
import sqlite3
import sys
import logging
import os
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager
from cachetools import LRUCache

from core.initializer import SnowballInitializer



class MemoryError(Exception):
    pass


class Memory:
    def __init__(self, db_path='S:/Snowball/data/memories.db'):
        initializer = SnowballInitializer()
        self.logger = initializer.logger
        self.config_loader = initializer.config_loader
        self.db_path = db_path
        self.cache = LRUCache(maxsize=1000)  # Cache for frequently accessed data
        self._db_lock = threading.Lock()  # Lock for thread safety in database operations

        # Ensure the directory exists for the database
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        try:
            # Establish a connection to the SQLite database
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.logger.log_event(f"Connected to SQLite database: {self.db_path}")
            self.create_tables()
        except sqlite3.Error as e:
            self.logger.log_error(f"Error connecting to SQLite database: {e}")
            raise MemoryError(f"Error connecting to SQLite database: {e}")

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
                self.logger.log_error(f"Database error: {e}")
                raise MemoryError(f"Database operation failed: {e}")
            finally:
                cursor.close()

    def create_tables(self):
        """Create the necessary tables and indexes."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY,
                        user_input TEXT,
                        ai_response TEXT,
                        sentiment TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY,
                        result TEXT,
                        analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY,
                        interaction_id INTEGER,
                        rating INTEGER,
                        comments TEXT,
                        feedback_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (interaction_id) REFERENCES interactions (id)
                    )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)")
                self.logger.log_event("Created/checked tables: 'interactions', 'analysis_results', 'feedback'.")
        except MemoryError as e:
            self.logger.log_error(f"Error creating tables: {e}")

    def store_interaction(self, user_input, ai_response, sentiment=None):
        """Store a user interaction in the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO interactions (user_input, ai_response, sentiment) VALUES (?, ?, ?)",
                    (user_input, ai_response, sentiment)
                )
            self.logger.log_event(f"Stored interaction: User: '{user_input}', AI: '{ai_response}', Sentiment: '{sentiment}'")
        except MemoryError as e:
            self.logger.log_error(f"Error storing interaction: {e}")

    def store_feedback(self, interaction_id, rating, comments):
        """Store user feedback for a specific interaction."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO feedback (interaction_id, rating, comments) VALUES (?, ?, ?)",
                    (interaction_id, rating, comments)
                )
            self.logger.log_event(f"Stored feedback: Interaction ID: {interaction_id}, Rating: {rating}, Comments: '{comments}'")
        except MemoryError as e:
            self.logger.log_error(f"Error storing feedback: {e}")

    def get_feedback_by_interaction(self, interaction_id):
        """Retrieve feedback related to a specific interaction."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM feedback WHERE interaction_id = ?", (interaction_id,))
                feedback = cursor.fetchall()
            self.logger.log_event(f"Retrieved feedback for interaction ID: {interaction_id}")
            return feedback
        except MemoryError as e:
            self.logger.log_error(f"Error retrieving feedback: {e}")

    def analyze_feedback(self):
        """Analyze feedback to identify trends and areas for improvement."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT AVG(rating) as average_rating FROM feedback")
                average_rating = cursor.fetchone()[0]

                cursor.execute("SELECT comments FROM feedback")
                comments = cursor.fetchall()
                comments_text = [comment[0] for comment in comments]

            self.logger.log_event(f"Analyzed feedback: Average Rating: {average_rating}, Comments: {comments_text}")
            return average_rating, comments_text
        except MemoryError as e:
            self.logger.log_error(f"Error analyzing feedback: {e}")

    def store_analysis_result(self, result):
        """Store an analysis result in the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO analysis_results (result) VALUES (?)",
                    (result,)
                )
            self.logger.log_event(f"Stored analysis result: '{result}'")
        except MemoryError as e:
            self.logger.log_error(f"Error storing analysis result: {e}")

    def get_analysis_results(self):
        """Retrieve all analysis results from the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM analysis_results ORDER BY analysis_date DESC")
                results = cursor.fetchall()
            self.logger.log_event("Retrieved analysis results.")
            return results
        except MemoryError as e:
            self.logger.log_error(f"Error retrieving analysis results: {e}")

    def clean_old_interactions(self, days=30):
        """Clean old interactions from the database."""
        try:
            with self._get_cursor() as cursor:
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute("DELETE FROM interactions WHERE timestamp < ?", (cutoff_date,))
            self.logger.log_event(f"Cleaned interactions older than {days} days.")
        except MemoryError as e:
            self.logger.log_error(f"Error cleaning old interactions: {e}")

    def get_last_interaction(self):
        """Retrieve the last interaction."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT 1")
                interaction = cursor.fetchone()
            if interaction:
                self.logger.log_event(f"Retrieved last interaction: {interaction}")
            return interaction
        except MemoryError as e:
            self.logger.log_error(f"Error retrieving last interaction: {e}")

    def get_interactions_by_keyword(self, keyword):
        """Retrieve interactions containing a specific keyword."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM interactions WHERE user_input LIKE ?", ('%' + keyword + '%',))
                interactions = cursor.fetchall()
            self.logger.log_event(f"Retrieved interactions with keyword: '{keyword}'")
            return interactions
        except MemoryError as e:
            self.logger.log_error(f"Error retrieving interactions by keyword: {e}")

    def clear_interactions(self):
        """Delete all interactions from the database."""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("DELETE FROM interactions")
            self.logger.log_event("Cleared all interactions from the database.")
        except MemoryError as e:
            self.logger.log_error(f"Error clearing interactions: {e}")

    def backup_database(self):
        """Create a backup of the database for recovery."""
        try:
            backup_file = f'S:/Snowball/data/memories_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            with self._db_lock:
                with sqlite3.connect(backup_file) as backup_conn:
                    self.conn.backup(backup_conn)
            self.logger.log_event(f"Database backup created: {backup_file}")
        except sqlite3.Error as e:
            self.logger.log_error(f"Error creating backup: {e}")

    def close(self):
        """Close the database connection properly."""
        self.conn.close()
        self.logger.log_event("Closed database connection.")


# Example usage
if __name__ == "__main__":
    memory = Memory()
    try:
        # Example interactions and feedback
        memory.store_interaction("How is the weather?", "It's sunny.", "Positive")
        last_interaction = memory.get_last_interaction()
        if last_interaction:
            memory.store_feedback(last_interaction[0], 5, "Great response!")

        # Analyze feedback
        avg_rating, comments = memory.analyze_feedback()
        memory.store_analysis_result(f"Average Rating: {avg_rating}, Comments: {comments}")

        # Retrieve analysis results
        results = memory.get_analysis_results()
        print(f"Analysis Results: {results}")
    finally:
        memory.close()
