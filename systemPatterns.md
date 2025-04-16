# EGG Monitor - System Patterns

## Architecture Overview
- **Frontend**: NextJS14 application with two main views:
  - Administration panel (CRUD operations)
  - Presentation screen (data visualization)
- **Backend**: FastAPI service handling:
  - User/sensor management
  - WebSocket data streaming
  - Database operations
- **Database**: SQLite for persistent storage of sensor data

## Key Components
1. **Admin Panel**:
   - User management (create/read/update/delete)
   - Sensor management (create/read/update/delete)
   - Mock data control (start/stop)

2. **Presentation Screen**:
   - d3.js charts for data visualization
   - Time range slider (1 minute default)
   - WebSocket data subscription

3. **Data Flow**:
   - Sensors → Database (SQLite)
   - Database → Backend (FastAPI)
   - Backend → Frontend (WebSockets)
   - Frontend → d3.js visualization

## Design Patterns
- **Observer Pattern**: WebSocket pub/sub for real-time updates
- **Repository Pattern**: Database access layer
- **Component-Based Architecture**: Frontend organization
