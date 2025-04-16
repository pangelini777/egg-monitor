from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Set
import json
import asyncio
import time

from .. import models, schemas
from ..database import get_db
from ..utils.mock_data_generator import MockDataGenerator

router = APIRouter(prefix="/api", tags=["websockets"])

# Store active connections
class ConnectionManager:
    def __init__(self):
        # Maps sensor_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # All connections for the global endpoint
        self.global_connections: Set[WebSocket] = set()
        # Subscriptions for each global connection
        self.global_subscriptions: Dict[WebSocket, List[int]] = {}
    
    async def connect(self, websocket: WebSocket, sensor_id: int = None):
        await websocket.accept()
        if sensor_id is not None:
            # Single sensor connection
            if sensor_id not in self.active_connections:
                self.active_connections[sensor_id] = set()
            self.active_connections[sensor_id].add(websocket)
        else:
            # Global connection
            self.global_connections.add(websocket)
            self.global_subscriptions[websocket] = []
    
    def disconnect(self, websocket: WebSocket, sensor_id: int = None):
        if sensor_id is not None:
            # Single sensor connection
            if sensor_id in self.active_connections:
                self.active_connections[sensor_id].discard(websocket)
                if not self.active_connections[sensor_id]:
                    del self.active_connections[sensor_id]
        else:
            # Global connection
            self.global_connections.discard(websocket)
            if websocket in self.global_subscriptions:
                del self.global_subscriptions[websocket]
    
    def subscribe_global(self, websocket: WebSocket, sensor_ids: List[int]):
        """Subscribe a global connection to specific sensors"""
        if websocket in self.global_subscriptions:
            self.global_subscriptions[websocket] = sensor_ids
    
    async def broadcast_to_sensor(self, sensor_id: int, data: dict):
        # Add sensor_id to the data
        data["sensor_id"] = sensor_id
        
        # Send to specific sensor connections
        if sensor_id in self.active_connections:
            # Create a copy of the set to avoid modification during iteration
            websockets_to_process = list(self.active_connections[sensor_id])
            disconnected_websockets = set()
            
            for websocket in websockets_to_process:
                try:
                    await websocket.send_json(data)
                except Exception as e:
                    print(f"Error sending to websocket: {e}")
                    disconnected_websockets.add(websocket)
            
            # Clean up any disconnected websockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, sensor_id)
        
        # Send to global connections that are subscribed to this sensor
        global_disconnected = set()
        for websocket in self.global_connections:
            if websocket in self.global_subscriptions and sensor_id in self.global_subscriptions[websocket]:
                try:
                    await websocket.send_json(data)
                except Exception as e:
                    print(f"Error sending to global websocket: {e}")
                    global_disconnected.add(websocket)
        
        # Clean up disconnected global connections
        for websocket in global_disconnected:
            self.disconnect(websocket)

manager = ConnectionManager()

@router.websocket("/ws/sensors/{sensor_id}")
async def websocket_sensor_endpoint(websocket: WebSocket, sensor_id: int):
    """WebSocket endpoint for real-time data from a single sensor"""
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

@router.websocket("/ws/all")
async def websocket_all_sensors_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data from all sensors"""
    # Connect to the WebSocket
    await manager.connect(websocket)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Send initial message
        await websocket.send_json({
            "event": "connected",
            "message": "Connected to all sensors endpoint"
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
                sensor_ids = message.get("sensor_ids", [])  # List of sensor IDs to subscribe to
                
                # Update subscriptions
                manager.subscribe_global(websocket, sensor_ids)
                
                # No need to send initial data - the broadcast_sensor_data task will send data immediately
                
                await websocket.send_json({
                    "type": "subscription_updated",
                    "time_range": time_range,
                    "sensor_ids": sensor_ids
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()

# Create a global instance of the mock data generator
mock_data_generator = MockDataGenerator()

# Background task to broadcast sensor data to connected clients
async def broadcast_sensor_data():
    """Generate mock data for each sensor based on data_rate and broadcast to connected clients"""
    # Time between broadcasts in seconds
    broadcast_interval = 1.0
    
    while True:
        try:
            # Get all active sensors (from both specific and global connections)
            active_sensors = set()
            
            # Add sensors from specific connections
            for sensor_id in manager.active_connections.keys():
                active_sensors.add(sensor_id)
            
            # Add sensors from global subscriptions
            for subscriptions in manager.global_subscriptions.values():
                active_sensors.update(subscriptions)
            
            # Only process if there are active sensors
            if active_sensors:
                # Get current timestamp
                current_time = time.time()
                
                # Get database session
                db = next(get_db())
                
                try:
                    # Prepare batch data for all sensors
                    batch_data = {}
                    
                    # Create a list of sensors to process (to avoid modifying the set during iteration)
                    sensors_to_process = []
                    inactive_sensors = []
                    
                    # First, check which sensors are active by querying the database for all sensors
                    # This ensures we always have the latest active status
                    for sensor_id in active_sensors:
                        # Always query the database to get the latest active status
                        sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
                        if sensor and sensor.is_active:
                            # Only include active sensors
                            sensors_to_process.append(sensor_id)
                            # Update the data rate in case it changed
                            mock_data_generator.update_sensor_data_rate(sensor_id, round(sensor.sensor_data_rate / 100, 0))
                        else:
                            # Track inactive sensors to remove later
                            inactive_sensors.append(sensor_id)
                    
                    # Remove inactive sensors from the active_sensors set
                    for sensor_id in inactive_sensors:
                        active_sensors.discard(sensor_id)
                        mock_data_generator.remove_sensor(sensor_id)
                    
                    # Prepare batch data for all sensors
                    batch_data = {}
                    
                    # For each active sensor, generate data points
                    for sensor_id in sensors_to_process:
                        # Generate data points using the mock data generator
                        data_points = mock_data_generator.generate_data_points(
                            sensor_id,
                            current_time,
                            broadcast_interval
                        )
                        
                        # Add to batch data
                        batch_data[sensor_id] = data_points
                        
                        data_rate = mock_data_generator.sensor_data_rates.get(sensor_id, 0)
                        print(f"Generated {len(data_points)} points for sensor {sensor_id} (data_rate: {data_rate}Hz)")
                    
                    # Broadcast batch data to all global connections
                    if batch_data:
                        print(f"Broadcasting mock data for {len(batch_data)} sensors")
                        for websocket in manager.global_connections:
                            try:
                                # Only send data for sensors this connection is subscribed to
                                if websocket in manager.global_subscriptions:
                                    subscribed_sensors = manager.global_subscriptions[websocket]
                                    filtered_batch = {
                                        sensor_id: data
                                        for sensor_id, data in batch_data.items()
                                        if sensor_id in subscribed_sensors
                                    }
                                    
                                    if filtered_batch:
                                        await websocket.send_json({
                                            "event": "batch_data",
                                            "data": filtered_batch
                                        })
                            except Exception as e:
                                print(f"Error sending batch data to websocket: {e}")
                finally:
                    db.close()
            
            # Sleep before generating new data
            await asyncio.sleep(broadcast_interval)
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(1)  # Wait a bit longer on error
