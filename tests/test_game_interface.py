import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append('S:/games')

from game_interface import GameInterface

class TestGameInterface(unittest.TestCase):

    @patch('game_interface.logging.getLogger')
    def setUp(self, mock_logger):
        """Set up the GameInterface instance for each test."""
        self.game_interface = GameInterface()
        self.logger = mock_logger.return_value

    @patch('game_interface.GameInterface.launch_snake')
    def test_launch_valid_game(self, mock_launch_snake):
        """Test launching a valid game (snake)."""
        game_interface = GameInterface()
        game_interface.launch_game('snake')
        mock_launch_snake.assert_called_once()

    @patch('game_interface.GameInterface.launch_snake')
    def test_start_valid_game(self, mock_launch_snake):
        """Test starting a valid game (snake)."""
        game_interface = GameInterface()
        game_interface.start_game('snake')
        self.assertEqual(game_interface.get_active_game(), 'snake')
        mock_launch_snake.assert_called_once()

    def test_launch_invalid_game(self):
        """Test launching an invalid game."""
        self.game_interface.launch_game('invalid_game')
        self.logger.warning.assert_called_with("Game 'invalid_game' is not available.")

    def test_start_invalid_game(self):
        """Test starting an invalid game."""
        self.game_interface.start_game('invalid_game')
        self.assertEqual(self.game_interface.get_active_game(), "No active game.")
        self.logger.warning.assert_called_with("Game 'invalid_game' not found.")

    def test_stop_game_with_no_active_game(self):
        """Test stopping a game when no game is active."""
        self.game_interface.stop_game()
        self.logger.info.assert_called_with("No active game to stop.")
        self.assertIsNone(self.game_interface.active_game)

    @patch.object(GameInterface, 'launch_snake')
    def test_stop_active_game(self, mock_launch_snake):
        """Test stopping an active game."""
        self.game_interface.start_game('snake')
        self.game_interface.stop_game()
        self.assertIsNone(self.game_interface.active_game)
        self.logger.info.assert_called_with("Stopping snake game.")

if __name__ == "__main__":
    unittest.main()
