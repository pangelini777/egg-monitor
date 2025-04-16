from pydantic import BaseModel, Field
from typing import List, Optional, Union

# User schemas
class UserBase(BaseModel):
    user_name: str
    user_age: int = Field(ge=0)  # Age must be non-negative

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    user_name: Optional[str] = None
    user_age: Optional[int] = None

class UserInDB(UserBase):
    id: int
    
    class Config:
        orm_mode = True

# Sensor schemas
class SensorBase(BaseModel):
    sensor_name: str
    sensor_data_rate: float = Field(ge=1.0, default=100.0)  # Data rate must be at least 1Hz

class SensorCreate(SensorBase):
    pass

class SensorUpdate(SensorBase):
    sensor_name: Optional[str] = None
    sensor_data_rate: Optional[float] = None

class SensorInDB(SensorBase):
    id: int
    is_active: bool = False
    
    class Config:
        orm_mode = True

# Sensor data schemas
class SensorDataBase(BaseModel):
    timestamp: float
    value: float

class SensorDataCreate(SensorDataBase):
    sensor_id: int

class SensorDataInDB(SensorDataBase):
    id: int
    sensor_id: int
    
    class Config:
        orm_mode = True

# Response schemas with relationships
class SensorWithData(SensorInDB):
    data: List[SensorDataInDB] = []

class UserWithSensors(UserInDB):
    sensors: List[SensorInDB] = []

class SensorWithUsers(SensorInDB):
    users: List[UserInDB] = []
