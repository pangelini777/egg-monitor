# EGG Monitor

A tool for monitoring EGG (electrogastrogram) data with an administration panel and presentation screen.

## Project Overview

The EGG Monitor provides real-time visualization of electrogastrogram data through:

1. An administration panel for managing users and sensors
2. A presentation screen for data visualization

### Key Features

#### Administration Panel
- Create/edit/delete users (user_name + user_age)
- Create/edit/delete sensors (sensor_name + sensor_data_rate)
- Start/stop mock data production for any sensor (default 100Hz)

#### Presentation Screen
- Beautiful visualization of sensor data per user
- Interactive time range selection (default 1 minute)
- Real-time data updates via WebSockets

## Tech Stack

### Frontend
- NextJS 14 (App Router)
- d3.js for data visualization
- Tailwind CSS for styling

### Backend
- Python 3.11
- FastAPI
- WebSockets for real-time communication

### Database
- SQLite for sensor data storage

### DevOps
- Docker and Docker Compose for containerization

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (compatible with NextJS 14)
- Python 3.11

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/egg-monitor.git
cd egg-monitor
```

2. Start the application using Docker Compose
```bash
docker-compose up -d
```

3. Access the application
- Administration Panel: http://localhost:3000/admin
- Presentation Screen: http://localhost:3000

## Project Structure

```
├── frontend/            # NextJS 14 application
├── backend/             # FastAPI application
├── database/            # SQLite database setup
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # Project documentation
```

## Development

### Running in Development Mode

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing

### Backend
```bash
cd backend
python -m pytest
```

### Frontend
```bash
cd frontend
npm test
