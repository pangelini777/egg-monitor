from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import time
import random
import asyncio
import threading
import math

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
    responses={404: {"description": "Not found"}},
)

# Dictionary to store active mock data threads
mock_data_threads = {}

def generate_mock_data(sensor_id: int, data_rate: float):
    """Background task to generate realistic EGG mock data"""
    db = next(get_db())
    try:
        # Get the sensor
        sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
        if not sensor:
            return
        
        # Set sensor as active
        sensor.is_active = True
        db.commit()
        
        # Calculate sleep time based on data rate
        sleep_time = 1.0 / data_rate
        
        # Variables for generating realistic EGG data
        previous_value = 0.0
        base_frequency = 0.05  # 3 cycles per minute = 0.05Hz
        base_amplitude = 0.5
        
        # Generate data until stopped
        while sensor_id in mock_data_threads and mock_data_threads[sensor_id].is_active:
            # Create a new data point with realistic EGG pattern
            timestamp = time.time()
            
            # Base sine wave (3 cycles per minute)
            base_sine = base_amplitude * math.sin(2 * math.pi * base_frequency * timestamp)
            
            # Add small random variations (10% of amplitude)
            noise = (random.random() * 0.2) - 0.1
            
            # Add occasional artifacts (5% chance)
            artifact = 0.0
            if random.random() > 0.95:
                artifact = (random.random() * 0.4) - 0.2
            
            # Ensure smooth transitions from previous value
            smoothing_factor = 0.7
            value = (smoothing_factor * previous_value) + ((1 - smoothing_factor) * (base_sine + noise + artifact))
            
            # Ensure value stays within -1 to 1 range
            value = max(-1.0, min(1.0, value))
            
            # Update previous value for next iteration
            previous_value = value
            
            data_point = models.SensorData(
                sensor_id=sensor_id,
                timestamp=timestamp,
                value=value
            )
            
            db.add(data_point)
            db.commit()
            
            # Sleep according to data rate
            time.sleep(sleep_time)
        
        # Set sensor as inactive when stopped
        sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
        if sensor:
            sensor.is_active = False
            db.commit()
    finally:
        db.close()

@router.post("/", response_model=schemas.SensorInDB, status_code=status.HTTP_201_CREATED)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    """Create a new sensor"""
    # Check if sensor with the same name already exists
    db_sensor = db.query(models.Sensor).filter(models.Sensor.sensor_name == sensor.sensor_name).first()
    if db_sensor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sensor with name '{sensor.sensor_name}' already exists"
        )
    
    # Create new sensor
    db_sensor = models.Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@router.get("/", response_model=List[schemas.SensorWithUsers])
def read_sensors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sensors with their users"""
    sensors = db.query(models.Sensor).offset(skip).limit(limit).all()
    return sensors

@router.get("/{sensor_id}", response_model=schemas.SensorWithUsers)
def read_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Get a specific sensor by ID"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    return db_sensor

@router.put("/{sensor_id}", response_model=schemas.SensorInDB)
def update_sensor(sensor_id: int, sensor: schemas.SensorUpdate, db: Session = Depends(get_db)):
    """Update a sensor's information"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Update sensor fields if provided
    update_data = sensor.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sensor, key, value)
    
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Delete a sensor"""
    # Stop mock data generation if active
    if sensor_id in mock_data_threads and mock_data_threads[sensor_id].is_active:
        mock_data_threads[sensor_id].is_active = False
        del mock_data_threads[sensor_id]
    
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    db.delete(db_sensor)
    db.commit()
    return None

@router.post("/{sensor_id}/mock/start", response_model=schemas.SensorInDB)
def start_mock_data(sensor_id: int, db: Session = Depends(get_db)):
    """Start generating mock data for a sensor"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Check if mock data is already being generated
    if sensor_id in mock_data_threads and mock_data_threads[sensor_id].is_active:
        return db_sensor
    
    # Create and start a new thread for mock data generation
    class MockDataThread(threading.Thread):
        def __init__(self, sensor_id, data_rate):
            threading.Thread.__init__(self, daemon=True)
            self.sensor_id = sensor_id
            self.data_rate = data_rate
            self.is_active = True
        
        def run(self):
            generate_mock_data(self.sensor_id, self.data_rate)
    
    thread = MockDataThread(sensor_id, db_sensor.sensor_data_rate)
    mock_data_threads[sensor_id] = thread
    thread.start()
    
    # Update sensor status (the thread will also do this, but this ensures immediate UI feedback)
    db_sensor.is_active = True
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor

@router.post("/{sensor_id}/mock/stop", response_model=schemas.SensorInDB)
def stop_mock_data(sensor_id: int, db: Session = Depends(get_db)):
    """Stop generating mock data for a sensor"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Stop the mock data thread if it exists
    if sensor_id in mock_data_threads:
        mock_data_threads[sensor_id].is_active = False
        del mock_data_threads[sensor_id]
    
    # Update sensor status
    db_sensor.is_active = False
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor

@router.get("/{sensor_id}/data", response_model=List[schemas.SensorDataInDB])
def get_sensor_data(
    sensor_id: int, 
    limit: int = 100, 
    start_time: float = None, 
    end_time: float = None,
    db: Session = Depends(get_db)
):
    """Get data for a specific sensor with optional time range filtering"""
    # Check if sensor exists
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Build query
    query = db.query(models.SensorData).filter(models.SensorData.sensor_id == sensor_id)
    
    # Apply time range filters if provided
    if start_time is not None:
        query = query.filter(models.SensorData.timestamp >= start_time)
    if end_time is not None:
        query = query.filter(models.SensorData.timestamp <= end_time)
    
    # Order by timestamp (newest first) and limit results
    data = query.order_by(models.SensorData.timestamp.desc()).limit(limit).all()
    
    return data
