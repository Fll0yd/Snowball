# test_agent.py

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import threading

# Add the project root to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '../../../'))  # Adjust to point to the project root
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the SnowballAI class after modifying sys.path
from Snowball.decom.OLDagent import SnowballAI

class TestSnowballAI(unittest.TestCase):
    def setUp(self):
        """Set up the SnowballAI instance before each test."""
        with patch('core.logger.SnowballLogger') as MockLogger:
            self.mock_logger = MockLogger.return_value
            self.snowball_ai = SnowballAI()

    def test_initialization(self):
        """Test that the SnowballAI initializes all components correctly."""
        self.assertIsNotNone(self.snowball_ai.logger)
        self.assertIsNotNone(self.snowball_ai.name)
        self.mock_logger.log_event.assert_any_call("Logger initialized successfully.")
        self.mock_logger.log_event.assert_any_call("SnowballAI initialized with provided API key.")

    @patch('core.ai.sentiment_analysis.SentimentAnalysis')
    def test_sentiment_analysis(self, MockSentimentAnalysis):
        """Test the sentiment analysis module functionality."""
        mock_sentiment_instance = MockSentimentAnalysis.return_value
        mock_sentiment_instance.analyze.return_value = "positive"

        sentiment = self.snowball_ai.sentiment_analysis_module.analyze("I love this!")
        self.assertEqual(sentiment, "positive")
        mock_sentiment_instance.analyze.assert_called_with("I love this!")

    @patch('core.ai.voice.VoiceInterface')
    def test_voice_module(self, MockVoiceInterface):
        """Test the voice module functionality."""
        mock_voice_instance = MockVoiceInterface.return_value
        self.snowball_ai.voice_module = mock_voice_instance
        
        # Test speak functionality
        self.snowball_ai.voice_module.speak("Hello!")
        mock_voice_instance.speak.assert_called_with("Hello!")

    @patch('core.ai.vision.VisionModule')
    def test_vision_module(self, MockVisionModule):
        """Test the vision module functionality."""
        mock_vision_instance = MockVisionModule.return_value
        mock_vision_instance.get_current_emotion.return_value = "happy"
        
        facial_emotion = self.snowball_ai.vision_module.get_current_emotion()
        self.assertEqual(facial_emotion, "happy")
        mock_vision_instance.get_current_emotion.assert_called_once()

    @patch('core.ai.reinforcement.QLearningAgent')
    def test_reinforcement_learning(self, MockQLearningAgent):
        """Test the reinforcement learning module functionality."""
        mock_rl_instance = MockQLearningAgent.return_value
        self.snowball_ai.reinforcement_module = mock_rl_instance
        
        # Test training functionality
        self.snowball_ai.run_reinforcement_learning()
        mock_rl_instance.train.assert_called_once()
        
    @patch('core.ai.conversation.ConversationModule')
    def test_conversation_module(self, MockConversationModule):
        """Test the conversation module functionality."""
        mock_conversation_instance = MockConversationModule.return_value
        mock_conversation_instance.process_input.return_value = "Hello, how can I assist you?"
        
        response = self.snowball_ai.get_best_response("Hi there!", "neutral", "happy")
        self.assertIn("Hello, how can I assist you?", response)
        mock_conversation_instance.process_input.assert_called_with("Hi there!")

    @patch('core.system_monitor.SystemMonitor')
    def test_system_monitor(self, MockSystemMonitor):
        """Test the system monitoring module."""
        mock_system_monitor = MockSystemMonitor.return_value
        mock_system_monitor.get_system_health.return_value = {"alert": True, "message": "High CPU usage"}
        
        self.snowball_ai.system_monitor = mock_system_monitor
        
        # Run the system monitor loop once
        with patch.object(self.snowball_ai, 'running_event', threading.Event()):
            self.snowball_ai.running_event.set()  # Stop the loop after one run
            self.snowball_ai.system_monitor_loop()
        
        mock_system_monitor.get_system_health.assert_called_once()
        self.mock_logger.log_event.assert_any_call("System alert: High CPU usage")

    @patch('core.ai.file_manager.FileMonitor')
    def test_file_monitor(self, MockFileMonitor):
        """Test the file monitoring module."""
        mock_file_monitor = MockFileMonitor.return_value
        self.snowball_ai.file_monitor = mock_file_monitor
        
        # Test start monitoring functionality
        self.snowball_ai.file_monitor.start_monitoring()
        mock_file_monitor.start_monitoring.assert_called_once()

    def test_generate_name(self):
        """Test the AI's name generation method."""
        with patch("builtins.open", unittest.mock.mock_open(read_data="Snowy\nFlurry\nChill")):
            generated_name = self.snowball_ai.generate_name()
            self.assertIn(generated_name, ["Snowy", "Flurry", "Chill"])

    def test_toggle_module(self):
        """Test enabling and disabling AI modules."""
        mock_voice_module = MagicMock()
        self.snowball_ai.voice_module = mock_voice_module
        
        self.snowball_ai.toggle_module("voice", enable=True)
        mock_voice_module.start.assert_called_once()
        
        self.snowball_ai.toggle_module("voice", enable=False)
        mock_voice_module.stop.assert_called_once()

    def test_interact(self):
        """Test the interaction method of SnowballAI."""
        mock_sentiment = MagicMock()
        mock_sentiment.analyze.return_value = "positive"
        self.snowball_ai.sentiment_analysis_module = mock_sentiment
        
        mock_vision = MagicMock()
        mock_vision.get_current_emotion.return_value = "happy"
        self.snowball_ai.vision_module = mock_vision
        
        mock_conversation = MagicMock()
        mock_conversation.process_input.return_value = "Glad to hear that!"
        self.snowball_ai.conversation_module = mock_conversation
        
        mock_voice = MagicMock()
        self.snowball_ai.voice_module = mock_voice
        
        self.snowball_ai.interact("I am feeling great!")
        mock_sentiment.analyze.assert_called_with("I am feeling great!")
        mock_vision.get_current_emotion.assert_called_once()
        mock_conversation.process_input.assert_called_with("I am feeling great!")
        mock_voice.speak.assert_called_with("Glad to hear that!")

if __name__ == "__main__":
    unittest.main()
