"""
Run script for the EGG Monitor backend.
This script initializes the database and starts the FastAPI server.
"""

import os
import uvicorn
from init_db import init_db

def main():
    """Initialize the database and start the server"""
    print("EGG Monitor Backend")
    print("===================")
    
    # Initialize the database with sample data
    print("Initializing database...")
    init_db()
    
    # Start the FastAPI server
    print("\nStarting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

if __name__ == "__main__":
    main()
