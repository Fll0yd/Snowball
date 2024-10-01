import sys
import os
import unittest
import numpy as np
from unittest.mock import patch

# Ensure the core directory is accessible for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
from reinforcement import QLearningAgent  # Adjusted import based on the correct file structure

class TestQLearningAgent(unittest.TestCase):

    def setUp(self):
        """Set up the QLearningAgent instance before each test."""
        self.state_size = 5  # Example state size
        self.action_size = 3  # Example action size
        self.agent = QLearningAgent(state_size=self.state_size, action_size=self.action_size)

    def test_initialization(self):
        """Test if the agent is initialized correctly."""
        self.assertEqual(self.agent.state_size, self.state_size)
        self.assertEqual(self.agent.action_size, self.action_size)
        self.assertEqual(len(self.agent.memory), 0)  # Memory should be empty initially
        self.assertTrue(np.array_equal(self.agent.q_table, np.zeros((self.state_size, self.action_size))))

    def test_choose_action_exploitation(self):
        """Test action selection under exploitation."""
        self.agent.q_table[0] = [0.1, 0.5, 0.3]  # Set some Q-values for state 0
        self.agent.exploration_rate = 0.0  # Set exploration rate to 0 to force exploitation
        action = self.agent.choose_action(0)
        self.assertEqual(action, 1)  # Should select action with highest Q-value

    def test_choose_action_exploitation(self):
        """Test action selection under exploitation."""
        self.agent.q_table[0] = [0.1, 0.5, 0.3]  # Set some Q-values for state 0
        self.agent.exploration_rate = 0.0  # Set exploration rate to 0 to force exploitation
        action = self.agent.choose_action(0)
        print(f"Selected action: {action}, Q-values: {self.agent.q_table[0]}")  # Debugging line
        self.assertEqual(action, 1)  # Should select action with highest Q-value

    def test_remember(self):
        """Test storing experiences in memory."""
        self.agent.remember(0, 1, 1, 0, False)
        self.assertEqual(len(self.agent.memory), 1)
        self.assertEqual(self.agent.memory[0], (0, 1, 1, 0, False))  # Check if the stored experience matches

    def test_learn(self):
        """Test learning process."""
        self.agent.q_table[0] = [0.0, 0.0, 0.0]  # Reset Q-values
        self.agent.learn(current_state=0, action=1, reward=1, next_state=1, done=False)
        self.assertNotEqual(self.agent.q_table[0][1], 0.0)  # Q-value should have been updated

    def test_save_load_q_table(self):
        """Test saving and loading Q-table."""
        self.agent.q_table[0][1] = 1.0  # Modify Q-table
        self.agent.save_q_table("test_q_table.npy")
        new_agent = QLearningAgent(state_size=self.state_size, action_size=self.action_size)
        new_agent.load_q_table("test_q_table.npy")
        self.assertEqual(new_agent.q_table[0][1], 1.0)  # Check if the Q-table was loaded correctly

    def test_visualize_training(self):
        """Test if the training visualization function works without errors."""
        self.agent.update_performance(10)  # Add some performance data
        self.agent.visualize_training()  # This should run without throwing errors

    def test_reset_agent(self):
        """Test if the agent's parameters reset correctly."""
        self.agent.reset_agent()
        self.assertTrue(np.array_equal(self.agent.q_table, np.zeros((self.state_size, self.action_size))))
        self.assertEqual(self.agent.exploration_rate, 1.0)
        self.assertEqual(len(self.agent.history), 0)

    def test_save_load_model_checkpoint(self):
        """Test saving and loading model checkpoints."""
        self.agent.save_model_checkpoint("test_checkpoint.npz")
        new_agent = QLearningAgent(state_size=self.state_size, action_size=self.action_size)
        new_agent.load_model_checkpoint("test_checkpoint.npz")
        self.assertTrue(np.array_equal(new_agent.q_table, self.agent.q_table))  # Check if the Q-table matches
        self.assertEqual(new_agent.exploration_rate, self.agent.exploration_rate)  # Check exploration rate

if __name__ == "__main__":
    unittest.main()
