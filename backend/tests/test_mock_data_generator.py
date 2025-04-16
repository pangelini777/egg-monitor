import unittest
import math
import time
from app.utils.mock_data_generator import MockDataGenerator

class TestMockDataGenerator(unittest.TestCase):
    """Tests for the MockDataGenerator class"""
    
    def setUp(self):
        """Set up a new MockDataGenerator instance for each test"""
        self.generator = MockDataGenerator()
        
    def test_update_sensor_data_rate(self):
        """Test updating a sensor's data rate"""
        # Arrange
        sensor_id = 1
        data_rate = 10.5
        
        # Act
        self.generator.update_sensor_data_rate(sensor_id, data_rate)
        
        # Assert
        self.assertEqual(self.generator.sensor_data_rates[sensor_id], data_rate)
        self.assertIsInstance(self.generator.sensor_data_rates[sensor_id], float)
        
    def test_remove_sensor(self):
        """Test removing a sensor"""
        # Arrange
        sensor_id = 1
        self.generator.update_sensor_data_rate(sensor_id, 10.0)
        self.generator.sensor_phases[sensor_id] = 0.5
        self.generator.sensor_last_values[sensor_id] = 0.3
        
        # Act
        self.generator.remove_sensor(sensor_id)
        
        # Assert
        self.assertNotIn(sensor_id, self.generator.sensor_data_rates)
        self.assertNotIn(sensor_id, self.generator.sensor_phases)
        self.assertNotIn(sensor_id, self.generator.sensor_last_values)
        
    def test_generate_data_points_no_data_rate(self):
        """Test generating data points for a sensor with no data rate"""
        # Arrange
        sensor_id = 1
        current_time = time.time()
        broadcast_interval = 1.0
        
        # Act
        data_points = self.generator.generate_data_points(sensor_id, current_time, broadcast_interval)
        
        # Assert
        self.assertEqual(len(data_points), 0)
        
    def test_generate_data_points(self):
        """Test generating data points for a sensor"""
        # Arrange
        sensor_id = 1
        data_rate = 5.0  # 5 Hz
        current_time = time.time()
        broadcast_interval = 1.0
        self.generator.update_sensor_data_rate(sensor_id, data_rate)
        
        # Act
        data_points = self.generator.generate_data_points(sensor_id, current_time, broadcast_interval)
        
        # Assert
        self.assertEqual(len(data_points), 5)  # Should generate 5 points (5 Hz * 1 second)
        
        # Check data point structure and values
        for point in data_points:
            self.assertIn("timestamp", point)
            self.assertIn("value", point)
            self.assertIsInstance(point["timestamp"], float)
            self.assertIsInstance(point["value"], float)
            self.assertGreaterEqual(point["value"], -1.0)
            self.assertLessEqual(point["value"], 1.0)
            
        # Check timestamps are in correct order and have correct precision
        for i in range(1, len(data_points)):
            self.assertGreater(data_points[i]["timestamp"], data_points[i-1]["timestamp"])
            # Check timestamp precision (should have microsecond precision at least)
            timestamp_diff = data_points[i]["timestamp"] - data_points[i-1]["timestamp"]
            self.assertAlmostEqual(timestamp_diff, broadcast_interval / data_rate, places=6)
            
    def test_generate_single_data_point(self):
        """Test generating a single data point"""
        # Arrange
        sensor_id = 1
        base_frequency = 0.05
        time_step = 0.1
        self.generator.sensor_phases[sensor_id] = 0.0
        self.generator.sensor_last_values[sensor_id] = 0.0
        
        # Act
        value = self.generator._generate_single_data_point(sensor_id, base_frequency, time_step)
        
        # Assert
        self.assertIsInstance(value, float)
        self.assertGreaterEqual(value, -1.0)
        self.assertLessEqual(value, 1.0)
        
        # Check that phase was updated
        self.assertGreater(self.generator.sensor_phases[sensor_id], 0.0)
        
        # Check that last value was updated
        self.assertEqual(self.generator.sensor_last_values[sensor_id], value)
        
    def test_data_continuity(self):
        """Test that generated data is continuous between calls"""
        # Arrange
        sensor_id = 1
        data_rate = 10.0
        current_time = time.time()
        broadcast_interval = 1.0
        self.generator.update_sensor_data_rate(sensor_id, data_rate)
        
        # Act - Generate two batches of data
        batch1 = self.generator.generate_data_points(sensor_id, current_time, broadcast_interval)
        batch2 = self.generator.generate_data_points(sensor_id, current_time + broadcast_interval, broadcast_interval)
        
        # Assert - The last value of batch1 should be close to the first value of batch2
        # (allowing for some change due to the algorithm)
        last_value_batch1 = batch1[-1]["value"]
        first_value_batch2 = batch2[0]["value"]
        
        # The change should be limited by max_step in the algorithm
        max_allowed_change = 0.2 * (broadcast_interval / data_rate)
        self.assertLessEqual(abs(first_value_batch2 - last_value_batch1), max_allowed_change + 0.001)  # Add small epsilon for floating point comparison
        
    def test_data_precision(self):
        """Test that data has appropriate precision"""
        # Arrange
        sensor_id = 1
        data_rate = 10.0  # Use a lower data rate to avoid precision issues
        current_time = time.time()
        broadcast_interval = 1.0  # Use a standard interval
        self.generator.update_sensor_data_rate(sensor_id, data_rate)
        
        # Act
        data_points = self.generator.generate_data_points(sensor_id, current_time, broadcast_interval)
        
        # Assert
        # Check that timestamps are increasing and roughly match the expected interval
        for i in range(1, len(data_points)):
            timestamp_diff = data_points[i]["timestamp"] - data_points[i-1]["timestamp"]
            expected_diff = broadcast_interval / data_rate
            
            # The difference should be close to the expected value, but we allow for some system-level variance
            # Instead of exact equality, we check that it's within a reasonable range
            self.assertGreater(timestamp_diff, 0, "Timestamps should be increasing")
            self.assertLess(abs(timestamp_diff - expected_diff), 0.01,
                           f"Timestamp difference {timestamp_diff} should be close to expected {expected_diff}")
            
        # Check that values have appropriate precision
        for point in data_points:
            # Ensure values are within the valid range with proper precision
            self.assertGreaterEqual(point["value"], -1.0)
            self.assertLessEqual(point["value"], 1.0)
            
            # Check that the value has sufficient decimal precision
            # We convert to string and check decimal places
            value_str = str(point["value"])
            if '.' in value_str:
                decimal_places = len(value_str.split('.')[1])
                self.assertGreaterEqual(decimal_places, 6, "Value should have at least 6 decimal places")

if __name__ == "__main__":
    unittest.main()