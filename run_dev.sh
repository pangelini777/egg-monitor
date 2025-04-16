#!/bin/bash

# Development script for the EGG Monitor application
# This script starts both the frontend and backend servers

echo "EGG Monitor Development Environment"
echo "=================================="

# Create the database directory if it doesn't exist
mkdir -p database

# Function to stop all processes on exit
function cleanup {
  echo -e "\nStopping all processes..."
  kill $(jobs -p) 2>/dev/null
  exit
}

# Set up trap to call cleanup function when script exits
trap cleanup EXIT INT TERM

# Start the backend server
echo -e "\nStarting backend server..."
cd backend
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo "Failed to start backend server"
  exit 1
fi

echo "Backend server running at http://localhost:8000"

# Start the frontend server
echo -e "\nStarting frontend server..."
cd frontend
node run.dev.js &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
  echo "Failed to start frontend server"
  exit 1
fi

echo "Frontend server running at http://localhost:3000"

echo -e "\nEGG Monitor is now running!"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- Backend API Docs: http://localhost:8000/docs"
echo -e "\nPress Ctrl+C to stop all servers"

# Wait for all background processes to finish
wait
