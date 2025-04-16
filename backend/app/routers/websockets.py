from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Set
import json
import asyncio
import time

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["websockets"])

# Store active connections
class ConnectionManager:
    def __init__(self):
        # Maps sensor_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, sensor_id: int):
        await websocket.accept()
        if sensor_id not in self.active_connections:
            self.active_connections[sensor_id] = set()
        self.active_connections[sensor_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, sensor_id: int):
        if sensor_id in self.active_connections:
            self.active_connections[sensor_id].discard(websocket)
            if not self.active_connections[sensor_id]:
                del self.active_connections[sensor_id]
    
    async def broadcast_to_sensor(self, sensor_id: int, data: dict):
        if sensor_id in self.active_connections:
            disconnected_websockets = set()
            for websocket in self.active_connections[sensor_id]:
                try:
                    await websocket.send_json(data)
                except Exception:
                    disconnected_websockets.add(websocket)
            
            # Clean up any disconnected websockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, sensor_id)

manager = ConnectionManager()

@router.websocket("/ws/sensors/{sensor_id}")
async def websocket_sensor_endpoint(websocket: WebSocket, sensor_id: int):
    """WebSocket endpoint for real-time sensor data"""
    # Connect to the WebSocket
    await manager.connect(websocket, sensor_id)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Check if sensor exists
        sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
        if not sensor:
            await websocket.close(code=1000)
            return
        
        # Send initial message
        await websocket.send_json({
            "event": "connected",
            "sensor_id": sensor_id,
            "sensor_name": sensor.sensor_name,
            "data_rate": sensor.sensor_data_rate
        })
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "subscribe":
                # Client can update subscription parameters
                time_range = message.get("time_range", 60)  # Default 60 seconds
                await websocket.send_json({
                    "type": "subscription_updated",
                    "time_range": time_range
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, sensor_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, sensor_id)
    finally:
        db.close()

# Background task to broadcast sensor data to connected clients
async def broadcast_sensor_data():
    """Periodically check for new sensor data and broadcast to connected clients"""
    while True:
        try:
            # Only process if there are active connections
            if manager.active_connections:
                db = next(get_db())
                try:
                    # For each sensor with active connections
                    for sensor_id in list(manager.active_connections.keys()):
                        # Get the latest data point
                        latest_data = db.query(models.SensorData)\
                            .filter(models.SensorData.sensor_id == sensor_id)\
                            .order_by(models.SensorData.timestamp.desc())\
                            .first()
                        
                        if latest_data:
                            # Broadcast to all connections for this sensor
                            await manager.broadcast_to_sensor(sensor_id, {
                                "event": "data",
                                "sensor_id": sensor_id,
                                "timestamp": latest_data.timestamp,
                                "value": latest_data.value
                            })
                finally:
                    db.close()
            
            # Sleep before checking again
            await asyncio.sleep(0.1)  # Check every 100ms
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(1)  # Wait a bit longer on error
