import math
import random
from typing import Dict, List, Optional

class MockDataGenerator:
    """
    Class to generate realistic mock EGG (Electrogastrogram) data for sensors.
    
    This class maintains state for each sensor to ensure continuous, coherent waveforms
    that simulate realistic EGG patterns with appropriate variations and artifacts.
    """
    
    def __init__(self):
        # Keep track of the phase and last value for each sensor to generate continuous, coherent waves
        self.sensor_phases: Dict[int, float] = {}
        self.sensor_last_values: Dict[int, float] = {}
        
        # Keep track of sensor data rates
        self.sensor_data_rates: Dict[int, float] = {}
    
    def update_sensor_data_rate(self, sensor_id: int, data_rate: float) -> None:
        """
        Update the data rate for a sensor
        
        Args:
            sensor_id: The ID of the sensor
            data_rate: The data rate in Hz
        """
        self.sensor_data_rates[sensor_id] = data_rate
    
    def remove_sensor(self, sensor_id: int) -> None:
        """
        Remove a sensor from tracking
        
        Args:
            sensor_id: The ID of the sensor to remove
        """
        if sensor_id in self.sensor_data_rates:
            del self.sensor_data_rates[sensor_id]
        if sensor_id in self.sensor_phases:
            del self.sensor_phases[sensor_id]
        if sensor_id in self.sensor_last_values:
            del self.sensor_last_values[sensor_id]
    
    def generate_data_points(self, sensor_id: int, current_time: float, broadcast_interval: float) -> List[Dict[str, float]]:
        """
        Generate data points for a sensor based on its data rate
        
        Args:
            sensor_id: The ID of the sensor
            current_time: The current timestamp
            broadcast_interval: The time interval between broadcasts in seconds
            
        Returns:
            A list of data points, each with a timestamp and value
        """
        if sensor_id not in self.sensor_data_rates:
            return []
        
        data_rate = self.sensor_data_rates[sensor_id]
        
        # Calculate number of points to generate based on data_rate and broadcast interval
        # For example, if data_rate is 10Hz and broadcast_interval is 1 second, generate 10 points
        num_points = max(1, int(data_rate * broadcast_interval))
        
        # Time step between points in seconds
        time_step = broadcast_interval / num_points
        
        # Initialize phase if not exists
        if sensor_id not in self.sensor_phases:
            self.sensor_phases[sensor_id] = random.uniform(0, 2 * math.pi)
            self.sensor_last_values[sensor_id] = 0.0
        
        # Generate data points
        data_points = []
        
        # Base frequency - 3 cycles per minute (0.05Hz) with variation based on sensor_id
        base_frequency = 0.05 * (1 + (sensor_id % 5) * 0.2)
        
        for i in range(num_points):
            # Calculate timestamp for this point with full precision
            point_time = current_time - broadcast_interval + (i + 1) * time_step
            
            # Generate the data point
            value = self._generate_single_data_point(sensor_id, base_frequency, time_step)
            
            # Create data point with precise formatting for both timestamp and value
            data_points.append({
                "timestamp": point_time,
                "value": float(f"{value:.6f}")  # Ensure 6 decimal places
            })
        
        return data_points
    
    def _generate_single_data_point(self, sensor_id: int, base_frequency: float, time_step: float) -> float:
        """
        Generate a single data point for a sensor
        
        Args:
            sensor_id: The ID of the sensor
            base_frequency: The base frequency for the sine wave
            time_step: The time step between points in seconds
            
        Returns:
            A float value representing the data point
        """
        # Update phase gradually
        phase_increment = 2 * math.pi * base_frequency * time_step
        self.sensor_phases[sensor_id] += phase_increment
        
        # Get last value
        last_value = self.sensor_last_values[sensor_id]
        
        # Generate new base value from sine wave
        base_value = math.sin(self.sensor_phases[sensor_id])
        
        # Add small random variation (max 10% change from previous value)
        max_change = 0.1
        noise = random.uniform(-max_change, max_change)
        
        # Ensure coherent transition from last value (limit rate of change)
        target_value = base_value + noise
        max_step = 0.2 * time_step  # Max change per time step
        
        # Limit change to ensure coherence
        if target_value > last_value + max_step:
            value = last_value + max_step
        elif target_value < last_value - max_step:
            value = last_value - max_step
        else:
            value = target_value
        
        # Occasionally add a small artifact (5% chance)
        if random.random() < 0.05 * time_step:  # Scale chance with time step
            artifact = random.uniform(0.1, 0.3) * (1 if random.random() > 0.5 else -1)
            value += artifact
        
        # Clamp value between -1 and 1
        value = max(-1.0, min(1.0, value))
        
        # Ensure the value has sufficient decimal precision (at least 6 decimal places)
        # We do this by formatting the value with 6 decimal places and then converting back to float
        value = float(f"{value:.6f}")
        
        # Store as last value for next iteration
        self.sensor_last_values[sensor_id] = value
        
        return value