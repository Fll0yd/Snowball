import sys
import os
import unittest
from unittest.mock import patch

# Ensure the core directory is accessible for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from other.nlp_engine import NLPEngine  # Import NLPEngine from core

# Define the path to the config file
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/api_keys.json'))

class TestNLPEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up the NLPEngine instance before each test."""
        self.nlp_engine = NLPEngine(config_path=config_path)

    @patch('openai.ChatCompletion.create')
    def test_openai_api_integration(self, mock_create):
        """Test OpenAI API integration."""
        mock_create.return_value = {
            'choices': [{'message': {'content': 'Sure! I can help with Python.'}}]
        }
        response = self.nlp_engine.process_input("Can you help me with Python?")
        self.assertEqual(response, 'Sure! I can help with Python.')

    def test_memory_interaction(self):
        """Test memory recall."""
        self.nlp_engine.memory.store_interaction("Hello, Snowball!", "Hi there!")
        response = self.nlp_engine.process_input("Hello, Snowball!")
        self.assertIn("Here's what I found related to 'hello, snowball!'", response)

    @patch('core.decision_maker.DecisionMaker.handle_request')
    def test_decision_making(self, mock_handle_request):
        """Test decision-making for reminders."""
        mock_handle_request.return_value = "Reminder set!"
        response = self.nlp_engine.process_input("remind me to take a break in 5 minutes")
        self.assertEqual(response, "Reminder set!")

    @patch('core.game_ai.GameAI.adjust_learning_parameters')
    def test_process_snake_commands(self, mock_adjust):
        """Test Snake AI command processing."""
        response = self.nlp_engine.process_input("help snake with learning")
        mock_adjust.assert_called_once_with("exploration_rate", 0.05)
        self.assertEqual(response, "I've helped the Snake AI with a learning boost!")

    def test_api_key_loading(self):
        """Test loading API keys from config."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with self.assertRaises(Exception):
                NLPEngine(config_path='invalid/path/api_keys.json')

if __name__ == "__main__":
    unittest.main()
