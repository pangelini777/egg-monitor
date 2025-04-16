from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user with the same name already exists
    db_user = db.query(models.User).filter(models.User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with name '{user.user_name}' already exists"
        )
    
    # Create new user
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.UserWithSensors])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with their sensors"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.UserWithSensors)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return db_user

@router.put("/{user_id}", response_model=schemas.UserInDB)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update a user's information"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update user fields if provided
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    db.delete(db_user)
    db.commit()
    return None

@router.post("/{user_id}/sensors/{sensor_id}", response_model=schemas.UserWithSensors)
def assign_sensor_to_user(user_id: int, sensor_id: int, db: Session = Depends(get_db)):
    """Assign a sensor to a user"""
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if sensor exists
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Add sensor to user if not already assigned
    if db_sensor not in db_user.sensors:
        db_user.sensors.append(db_sensor)
        db.commit()
        db.refresh(db_user)
    
    return db_user

@router.delete("/{user_id}/sensors/{sensor_id}", response_model=schemas.UserWithSensors)
def remove_sensor_from_user(user_id: int, sensor_id: int, db: Session = Depends(get_db)):
    """Remove a sensor from a user"""
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if sensor exists
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if db_sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID {sensor_id} not found"
        )
    
    # Remove sensor from user if assigned
    if db_sensor in db_user.sensors:
        db_user.sensors.remove(db_sensor)
        db.commit()
        db.refresh(db_user)
    
    return db_user
