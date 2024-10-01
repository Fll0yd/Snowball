import unittest
import numpy as np
import sys
import os

# Add the core directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

from game_ai import GameAI

class TestGameAI(unittest.TestCase):

    def setUp(self):
        """Set up the environment and initialize the AI before each test."""
        self.ai = GameAI()
        self.state = np.random.rand(self.ai.state_size)  # Random initial state
        self.next_state = np.random.rand(self.ai.state_size)  # Random next state

    def test_initialization(self):
        """Test if the AI initializes correctly with the right parameters."""
        self.assertEqual(self.ai.state_size, 11)
        self.assertEqual(self.ai.action_size, 3)
        self.assertEqual(len(self.ai.memory), 0)
        self.assertEqual(self.ai.epsilon, 1.0)
        self.assertTrue(self.ai.model)  # Model should be initialized

    def test_build_model(self):
        """Test if the model builds correctly."""
        model = self.ai.build_model()
        self.assertEqual(model.input_shape[1], self.ai.state_size)
        self.assertEqual(model.output_shape[1], self.ai.action_size)

    def test_remember(self):
        """Test if the AI remembers experiences."""
        action = 1
        reward = 10
        done = False
        self.ai.remember(self.state, action, reward, self.next_state, done)
        self.assertEqual(len(self.ai.memory), 1)  # Memory should now have 1 item
        experience = self.ai.memory[-1]
        self.assertEqual(experience[0].all(), self.state.all())
        self.assertEqual(experience[1], action)
        self.assertEqual(experience[2], reward)
        self.assertEqual(experience[3].all(), self.next_state.all())
        self.assertEqual(experience[4], done)

    def test_choose_action_explore(self):
        """Test if the AI chooses a random action (explore mode) when epsilon is high."""
        self.ai.epsilon = 1.0  # Set epsilon high to force exploration
        action = self.ai.choose_action(self.state)
        self.assertIn(action, range(self.ai.action_size))  # Action should be valid

    def test_choose_action_exploit(self):
        """Test if the AI chooses the best action (exploit mode) when epsilon is low."""
        self.ai.epsilon = 0.0  # Set epsilon low to force exploitation
        action = self.ai.choose_action(self.state)
        self.assertIn(action, range(self.ai.action_size))  # Action should be valid

    def test_replay(self):
        """Test if the replay function trains the model."""
        # Add some experiences to memory
        for _ in range(32):
            self.ai.remember(self.state, 1, 10, self.next_state, False)
        
        # Before replaying, ensure memory is filled
        self.assertEqual(len(self.ai.memory), 32)
        
        # Test replay function to ensure it processes without crashing
        self.ai.replay(batch_size=32)
        # Cannot assert learning but can ensure function completes without error

    def test_save_model(self):
        """Test if the model saves correctly."""
        file_name = "test_model.h5"
        self.ai.save_model(file_name)
        self.assertTrue(os.path.exists(file_name))  # Check if file exists
        os.remove(file_name)  # Clean up after test

    def test_load_model(self):
        """Test if the model loads correctly."""
        file_name = "test_model.h5"
        self.ai.save_model(file_name)
        self.ai.load_model(file_name)
        self.assertTrue(self.ai.model)  # Model should still exist after loading
        os.remove(file_name)  # Clean up after test

    def test_adjust_learning_parameters(self):
        """Test if the AI can adjust learning parameters."""
        new_epsilon = 0.5
        self.ai.adjust_learning_parameters('exploration_rate', new_epsilon)
        self.assertEqual(self.ai.epsilon, new_epsilon)

        new_learning_rate = 0.0005
        self.ai.adjust_learning_parameters('learning_rate', new_learning_rate)
        self.assertAlmostEqual(float(self.ai.model.optimizer.learning_rate.numpy()), new_learning_rate, places=7)

    def test_get_last_game_performance(self):
        """Test if the AI can return a performance metric."""
        performance = self.ai.get_last_game_performance()
        self.assertTrue(isinstance(performance, int))  # Should return an integer (e.g., score)

if __name__ == "__main__":
    unittest.main()
