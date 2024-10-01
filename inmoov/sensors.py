class Sensors:
    def __init__(self):
        self.sensor_data = {}

    def read_sensor_data(self, sensor_id):
        """
        Reads data from a sensor, like temperature, humidity, etc.
        This would likely be implemented with specific hardware libraries.
        """
        # Placeholder: This would interface with actual hardware
        self.sensor_data[sensor_id] = 50.0  # Dummy data

    def get_sensor_data(self, sensor_id):
        """
        Returns the last read value for a sensor.
        """
        return self.sensor_data.get(sensor_id, None)
