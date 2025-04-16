from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Association table for many-to-many relationship between users and sensors
user_sensor_association = Table(
    'user_sensor_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('sensor_id', Integer, ForeignKey('sensors.id'), primary_key=True)
)

class User(Base):
    """User model representing a person being monitored"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    user_age = Column(Integer)
    
    # Relationship with sensors (many-to-many)
    sensors = relationship(
        "Sensor",
        secondary=user_sensor_association,
        back_populates="users"
    )

class Sensor(Base):
    """Sensor model representing a device collecting EGG data"""
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True)
    sensor_data_rate = Column(Float, default=100.0)  # Default 100Hz
    is_active = Column(Boolean, default=False)  # Whether mock data is being produced
    
    # Relationship with users (many-to-many)
    users = relationship(
        "User",
        secondary=user_sensor_association,
        back_populates="sensors"
    )
    
    # Relationship with sensor data (one-to-many)
    data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")

class SensorData(Base):
    """Model for storing sensor data points"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    timestamp = Column(Float, index=True)  # Unix timestamp
    value = Column(Float)  # EGG data value
    
    # Relationship with sensor (many-to-one)
    sensor = relationship("Sensor", back_populates="data")
