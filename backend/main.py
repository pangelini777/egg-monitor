from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os

from app import models
from app.database import engine
from app.routers import users, sensors, websockets

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="EGG Monitor API",
    description="API for monitoring EGG (electrogastrogram) data",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(sensors.router)
app.include_router(websockets.router)

# Background task for WebSocket broadcasting
@app.on_event("startup")
async def startup_event():
    # Start the background task for broadcasting sensor data
    asyncio.create_task(websockets.broadcast_sensor_data())

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the EGG Monitor API",
        "docs": "/docs",
        "version": "0.1.0",
    }

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
