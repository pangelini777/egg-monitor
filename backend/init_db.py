"""
Database initialization script for EGG Monitor.
This script creates the database tables and populates them with sample data.
"""

import os
import sys
import time
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import Base, engine
from app.models import User, Sensor, SensorData, user_sensor_association

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def init_db():
    """Initialize the database with sample data"""
    try:
        # Check if we already have data
        existing_users = db.query(User).count()
        existing_sensors = db.query(Sensor).count()
        
        if existing_users > 0 or existing_sensors > 0:
            print("Database already contains data. Skipping initialization.")
            return
        
        print("Initializing database with sample data...")
        
        # Create sample users
        users = [
            User(user_name="John Doe", user_age=35),
            User(user_name="Jane Smith", user_age=28),
            User(user_name="Bob Johnson", user_age=42)
        ]
        
        # Add users to the database
        for user in users:
            db.add(user)
        
        db.commit()
        print(f"Created {len(users)} sample users")
        
        # Create sample sensors
        sensors = [
            Sensor(sensor_name="EGG Sensor 1", sensor_data_rate=100.0),
            Sensor(sensor_name="EGG Sensor 2", sensor_data_rate=200.0),
            Sensor(sensor_name="EGG Sensor 3", sensor_data_rate=50.0),
            Sensor(sensor_name="EGG Sensor 4", sensor_data_rate=150.0)
        ]
        
        # Add sensors to the database
        for sensor in sensors:
            db.add(sensor)
        
        db.commit()
        print(f"Created {len(sensors)} sample sensors")
        
        # Assign sensors to users
        # John has sensors 1 and 2
        users[0].sensors.append(sensors[0])
        users[0].sensors.append(sensors[1])
        
        # Jane has sensor 3
        users[1].sensors.append(sensors[2])
        
        # Bob has sensors 2 and 4
        users[2].sensors.append(sensors[1])
        users[2].sensors.append(sensors[3])
        
        db.commit()
        print("Assigned sensors to users")
        
        # Generate sample sensor data
        now = time.time()
        data_points = []
        
        for sensor in sensors:
            # Generate 100 data points for each sensor
            for i in range(100):
                # Data points from the last 5 minutes
                timestamp = now - (300 * random.random())
                value = random.uniform(-1.0, 1.0)  # Random value between -1 and 1
                
                data_point = SensorData(
                    sensor_id=sensor.id,
                    timestamp=timestamp,
                    value=value
                )
                data_points.append(data_point)
        
        # Add data points to the database
        for data_point in data_points:
            db.add(data_point)
        
        db.commit()
        print(f"Generated {len(data_points)} sample data points")
        
        print("Database initialization complete!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
