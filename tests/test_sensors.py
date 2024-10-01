import unittest
import sys
import os

# Ensure the core directory is accessible for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
from sensors import Sensors  # Adjusted import based on the correct file structure

class TestSensors(unittest.TestCase):

    def setUp(self):
        """Set up the Sensors instance before each test."""
        self.sensors = Sensors()

    def test_initialization(self):
        """Test if the Sensors instance initializes correctly."""
        self.assertIsInstance(self.sensors, Sensors)
        self.assertEqual(self.sensors.sensor_data, {})  # Check that sensor_data starts as empty

    def test_read_sensor_data(self):
        """Test reading sensor data."""
        self.sensors.read_sensor_data("temp_sensor")  # Simulate reading a temperature sensor
        self.assertIn("temp_sensor", self.sensors.sensor_data)  # Check that the sensor data is stored
        self.assertEqual(self.sensors.sensor_data["temp_sensor"], 50.0)  # Check the dummy value

    def test_get_sensor_data(self):
        """Test getting sensor data."""
        self.sensors.read_sensor_data("humidity_sensor")  # Read another sensor
        data = self.sensors.get_sensor_data("humidity_sensor")
        self.assertEqual(data, 50.0)  # Ensure it returns the correct dummy value
        
        # Test getting data from a sensor that hasn't been read
        non_existent_data = self.sensors.get_sensor_data("non_existent_sensor")
        self.assertIsNone(non_existent_data)  # Should return None for non-existent sensor

if __name__ == "__main__":
    unittest.main()
