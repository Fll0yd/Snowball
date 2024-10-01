# tests/test_ai_agent.py

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ai_agent import SnowballAI
import logging

class MobileIntegration:
    def listen_for_requests(self):
        # Simulate listening for mobile requests
        return "Check my schedule"
    
    def respond(self, response):
        # Placeholder for responding to mobile requests
        pass

class SystemMonitor:
    def start_system_monitoring(self):
        # Simulate system monitoring logic
        pass

class SnowballLogger:
    def __init__(self):
        self.logger = logging.getLogger("SnowballLogger")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

class TestSnowballAI(unittest.TestCase):

    def setUp(self):
        """Set up reusable objects for testing."""
        self.snowball_ai = SnowballAI()

    def tearDown(self):
        """Clean up after each test."""
        self.snowball_ai.stop()

    @patch('core.memory.Memory.store_interaction')
    @patch('core.nlp_engine.NLPEngine.process_input', return_value="Hello, how can I assist you?")
    @patch('core.voice_interface.VoiceInterface.listen', return_value="Hello Snowball")
    @patch('core.voice_interface.VoiceInterface.speak', return_value=None)  # Mocking speak function to prevent actual audio processing
    @patch('builtins.open', new_callable=MagicMock)  # Mock file opening
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_interact(self, mock_play_audio, mock_open, mock_speak, mock_listen, mock_process_input, mock_store_interaction):
        """Test basic voice interaction flow without speech synthesis."""
        self.snowball_ai.is_running = True
        with patch.object(self.snowball_ai, 'is_running', side_effect=[True, False]):
            self.snowball_ai.interact()

        # Assertions
        mock_listen.assert_called_once()
        mock_process_input.assert_called_once_with("Hello Snowball")
        mock_speak.assert_called_once_with("Hello, how can I assist you?")
        mock_store_interaction.assert_called_once_with("Hello Snowball", "Hello, how can I assist you?")

    @patch('core.mobile_integration.MobileIntegration.listen_for_requests', return_value="Check my schedule")
    @patch('core.mobile_integration.MobileIntegration.respond')
    @patch('core.nlp_engine.NLPEngine.process_input', return_value="Your next meeting is at 3 PM.")
    @patch('core.memory.Memory.store_interaction')
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_handle_mobile_requests(self, mock_play_audio, mock_store_interaction, mock_process_input, mock_respond, mock_listen_for_requests):
        """Test mobile request handling."""
        # Make sure is_running is set to True so the loop runs at least once
        self.snowball_ai.is_running = True
        with patch.object(self.snowball_ai, 'is_running', side_effect=[True, False]):
            self.snowball_ai.handle_mobile_requests()

        # Assertions
        mock_listen_for_requests.assert_called_once()
        mock_process_input.assert_called_once_with("Check my schedule")
        mock_respond.assert_called_once_with("Your next meeting is at 3 PM.")
        mock_store_interaction.assert_called_once_with("Check my schedule", "Your next meeting is at 3 PM.")

    @patch('core.logger.SnowballLogger.logger.info')
    @patch('core.system_monitor.SystemMonitor.start_system_monitoring')
    @patch('threading.Thread.start')
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_start(self, mock_play_audio, mock_thread_start, mock_system_monitoring, mock_logger_info):
        """Test the Snowball AI start method."""
        self.snowball_ai.is_running = False  # Prevent infinite interaction loop
        self.snowball_ai.start()

        # Assertions
        mock_logger_info.assert_called_with(f"Snowball AI ({self.snowball_ai.name}) started.")
        mock_thread_start.assert_called()
        mock_system_monitoring.assert_called_once()

    @patch('core.logger.SnowballLogger.__init__', return_value=None)
    @patch('core.logger.SnowballLogger.logger', new_callable=MagicMock)
    @patch('core.voice_interface.VoiceInterface.speak', return_value=None)
    @patch('builtins.open', new_callable=MagicMock)  # Mock file opening
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_stop(self, mock_play_audio, mock_open, mock_speak, mock_logger, mock_logger_init):
        """Test stopping Snowball AI."""
        self.snowball_ai.stop()

        # Assertions
        self.assertFalse(self.snowball_ai.is_running)
        mock_logger.logger.info.assert_called_with("Snowball AI shutting down.")
        mock_speak.assert_called_with("Goodbye!")

    def test_generate_name(self):
        """Test the random name generation for Snowball AI."""
        name = self.snowball_ai.generate_name()
        self.assertIn(name, ["Nova", "Aris", "Zephyr", "Echo", "Snowball"])

    @patch('core.nlp_engine.NLPEngine.process_input', return_value="Your next meeting is at 3 PM.")
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_process_input_schedule(self, mock_play_audio, mock_process_input):
        """Test decision making for schedule queries."""
        response = self.snowball_ai.process_input("What's my schedule?")
        self.assertEqual(response, "Your next meeting is at 3 PM.")

    @patch('core.decision_maker.DecisionMaker.handle_game_request', return_value="Starting Snake game")
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_process_input_game(self, mock_play_audio, mock_game_request):
        """Test decision making for game-related queries."""
        response = self.snowball_ai.process_input("Let's play a game.")
        self.assertEqual(response, "Starting Snake game")

    @patch('core.nlp_engine.NLPEngine.process_input', return_value="I don't understand.")
    @patch('core.voice_interface.VoiceInterface.play_audio', return_value=None)  # Mock play_audio to avoid playback issues
    def test_process_input_default(self, mock_play_audio, mock_process_input):
        """Test default NLP engine processing for non-specific queries."""
        response = self.snowball_ai.process_input("Tell me a joke.")
        self.assertEqual(response, "I don't understand.")

if __name__ == "__main__":
    unittest.main()
