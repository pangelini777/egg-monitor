# EGG Monitor - Project Summary

## Project Overview

The EGG Monitor is a web-based tool for monitoring electrogastrogram (EGG) data with:
1. An administration panel for managing users and sensors
2. A presentation screen for real-time data visualization

## Implementation Details

### Frontend (NextJS 14)
- Modern React application with App Router
- Responsive UI with Tailwind CSS
- Real-time data visualization with d3.js
- WebSocket integration for live updates
- Admin panel for user and sensor management

### Backend (FastAPI)
- RESTful API for user and sensor management
- WebSocket server for real-time data streaming
- SQLite database with SQLAlchemy ORM
- Mock data generation for testing
- Comprehensive API documentation with Swagger UI

### DevOps
- Docker containerization for both frontend and backend
- Docker Compose for orchestration
- Development scripts for easy setup

## Project Structure

```
egg-monitor/
├── frontend/                # NextJS 14 application
│   ├── app/                 # Next.js App Router
│   │   ├── admin/           # Admin panel
│   │   ├── globals.css      # Global styles
│   │   ├── layout.js        # Root layout
│   │   └── page.js          # Presentation screen
│   ├── components/          # Reusable components
│   │   └── EggChart.js      # D3.js chart component
│   ├── hooks/               # Custom React hooks
│   │   └── useWebSocket.js  # WebSocket hook
│   ├── Dockerfile           # Frontend container
│   ├── next.config.js       # Next.js configuration
│   ├── package.json         # Dependencies
│   ├── postcss.config.js    # PostCSS configuration
│   ├── run.dev.js           # Development script
│   └── tailwind.config.js   # Tailwind CSS configuration
│
├── backend/                 # FastAPI application
│   ├── app/                 # Application package
│   │   ├── routers/         # API routes
│   │   │   ├── sensors.py   # Sensor endpoints
│   │   │   ├── users.py     # User endpoints
│   │   │   └── websockets.py # WebSocket endpoints
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── tests/               # Unit tests
│   │   └── test_api.py      # API tests
│   ├── Dockerfile           # Backend container
│   ├── init_db.py           # Database initialization
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Run script
│
├── database/                # SQLite database
│   └── README.md            # Database documentation
│
├── docker-compose.yml       # Docker Compose configuration
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
└── run_dev.sh               # Development script
```

## How to Run

### Development Mode

1. Run both frontend and backend:
   ```bash
   ./run_dev.sh
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Admin Panel: http://localhost:3000/admin
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Features

### Administration Panel
- Create/edit/delete users (user_name + user_age)
- Create/edit/delete sensors (sensor_name + sensor_data_rate)
- Start/stop mock data production for any sensor
- Assign sensors to users

### Presentation Screen
- Real-time visualization of EGG data
- Time range selection slider
- User and sensor organization
- Automatic updates via WebSockets

## Next Steps

1. Integration testing between frontend and backend
2. Performance optimization for large datasets
3. Enhanced data visualization options
4. User authentication and authorization
5. Deployment to production environment
