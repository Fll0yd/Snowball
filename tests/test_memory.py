import sys
import os
import unittest
import threading
from unittest.mock import patch, mock_open
from time import sleep

# Ensure the core directory is accessible for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

from memory import Memory  # Import Memory class from core

class TestMemory(unittest.TestCase):
    
    def setUp(self):
        """Set up the Memory instance before each test."""
        self.memory = Memory()
        
    def tearDown(self):
        """Clean up after each test."""
        self.memory.clear_interactions()  # Ensure a clean state for each test
        self.memory.close_connection()

    def test_store_interaction(self):
        """Test storing a single user interaction."""
        self.memory.store_interaction("Hello, Snowball!", "Hi! How can I assist?")
        interactions = self.memory.get_interactions()
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0][1], "Hello, Snowball!")  # Check the user input

    def test_store_batch_interactions(self):
        """Test storing a batch of user interactions."""
        interactions = [
            ("Test input 1", "Test response 1"),
            ("Test input 2", "Test response 2"),
        ]
        self.memory.store_batch_interactions(interactions)

        all_interactions = self.memory.get_interactions()
        self.assertGreaterEqual(len(all_interactions), 2)

    def test_get_interactions(self):
        """Test retrieving all stored interactions."""
        self.memory.store_interaction("Hello!", "Hi there!")
        self.memory.store_interaction("How are you?", "I'm just a program.")
        all_interactions = self.memory.get_interactions()
        self.assertEqual(len(all_interactions), 2)

    def test_get_last_interaction(self):
        """Test retrieving the last stored interaction."""
        self.memory.store_interaction("First input", "First response")
        self.memory.store_interaction("Second input", "Second response")
        last_interaction = self.memory.get_last_interaction()
        self.assertIsNotNone(last_interaction)
        self.assertEqual(last_interaction[1], "Second input")  # Check the last user input
        self.assertEqual(last_interaction[2], "Second response")  # Check the last AI response

    def test_get_interactions_by_keyword(self):
        """Test retrieving interactions by a specific keyword."""
        self.memory.store_interaction("What's the weather?", "It's sunny today!")
        self.memory.store_interaction("Tell me about the weather tomorrow.", "It will be cloudy.")
        
        keyword_interactions = self.memory.get_interactions_by_keyword("weather")
        self.assertEqual(len(keyword_interactions), 2)

    @patch('plyer.notification.notify')
    def test_log_error_handling(self, mock_notify):
        """Test error logging on database failure (simulated)."""
        # Simulate a database error by providing an invalid path
        self.memory.db_path = 'invalid/path/memories.db'
        with self.assertRaises(Exception):
            Memory(self.memory.db_path)

    def test_clear_interactions(self):
        """Test clearing all stored interactions."""
        self.memory.store_interaction("Interaction 1", "Response 1")
        self.memory.store_interaction("Interaction 2", "Response 2")
        self.memory.clear_interactions()
        all_interactions = self.memory.get_interactions()
        self.assertEqual(len(all_interactions), 0)

    def test_backup_database(self):
        """Test database backup functionality."""
        self.memory.store_interaction("Backup test", "This should be backed up.")
        self.memory.backup_database()
        backup_file_exists = any('memories_backup' in f for f in os.listdir('data'))
        self.assertTrue(backup_file_exists)

    def test_cache_mechanism(self):
        """Test that cache works for interactions and keywords."""
        self.memory.store_interaction("Cached input", "Cached response")
        
        # First call should populate the cache
        all_interactions = self.memory.get_interactions()  # Should populate cache
        
        # Cache test for all interactions
        with patch.object(self.memory, 'conn', autospec=True) as mock_conn:
            all_interactions_cached = self.memory.get_interactions()  # Cache hit
            mock_conn.execute.assert_not_called()  # Database should not be queried on cache hit
            self.assertEqual(len(all_interactions_cached), 1)

        # First keyword search should populate cache
        keyword_interactions = self.memory.get_interactions_by_keyword("Cached")
        
        # Cache test for keyword search
        with patch.object(self.memory, 'conn', autospec=True) as mock_conn:
            keyword_interactions_cached = self.memory.get_interactions_by_keyword("Cached")  # Cache hit
            mock_conn.execute.assert_not_called()  # Database should not be queried on cache hit
            self.assertEqual(len(keyword_interactions_cached), 1)

    def test_thread_safety(self):
        """Test thread safety for storing and retrieving interactions."""
        def store_interactions_in_thread(memory_instance, interactions):
            for interaction in interactions:
                memory_instance.store_interaction(*interaction)
                sleep(0.1)  # Simulate a delay between operations

        interactions = [("Thread input 1", "Thread response 1"), ("Thread input 2", "Thread response 2")]
        thread1 = threading.Thread(target=store_interactions_in_thread, args=(self.memory, interactions))
        thread2 = threading.Thread(target=store_interactions_in_thread, args=(self.memory, interactions))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        all_interactions = self.memory.get_interactions()
        self.assertGreaterEqual(len(all_interactions), 4)  # Should have at least 4 interactions

    def test_backup_error_handling(self):
        """Test that errors during backup are handled."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Unable to create backup file")
            with self.assertLogs(self.memory.logger.logger, level='ERROR') as log:
                self.memory.backup_database()
                self.assertIn("Error backing up the database", log.output[0])

if __name__ == "__main__":
    unittest.main()
