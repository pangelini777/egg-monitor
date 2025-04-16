# EGG Monitor - Active Context

## Current Focus
- Project implementation
- Core functionality development
- Frontend and backend integration
- Real-time data visualization
- User experience improvements

## Recent Changes
- Created project documentation:
  - projectbrief.md
  - productContext.md
  - systemPatterns.md
  - techContext.md
- Implemented project structure:
  - Frontend (NextJS 14)
  - Backend (FastAPI)
  - Database (SQLite)
  - Docker configuration
- Developed core frontend components:
  - Main presentation screen
  - Admin panel
  - D3.js chart component
  - WebSocket hook for real-time data
- Implemented backend APIs:
  - User management
  - Sensor management
  - WebSocket server for real-time data
  - Mock data generation
- Fixed WebSocket connection issues:
  - Implemented client-side data simulation
  - Respected sensor data rates for data generation
- Enhanced data visualization:
  - ECG-style charts with continuous lines
  - Removed data points for cleaner visualization
  - Added baseline and grid for better readability
- Added sensor assignment functionality:
  - UI for assigning sensors to users in admin panel
  - API integration for sensor assignment

## Next Steps
1. Test the containerized deployment with Docker
2. Add more comprehensive tests
3. Optimize performance
4. Prepare for deployment

## Recent Improvements
1. Completely redesigned data generation and visualization system:
   - Backend now generates realistic mock data in real-time using sine waves
   - Each sensor has a unique pattern with different frequencies
   - Added random noise and occasional artifacts to simulate real EGG data
   - Implemented continuous waveforms by maintaining phase information

2. Improved data management in the frontend:
   - Implemented efficient clearing of data older than 5 minutes
   - Added proper timestamp handling for consistent visualization
   - Enhanced filtering to show data within the selected time range
   - Added visual indicators for latest data points

3. Enhanced WebSocket communication:
   - Switched to batch data transmission for efficiency
   - Implemented real-time data generation and sending (1 second intervals)
   - Improved subscription handling for immediate data delivery
   - Added detailed logging for easier debugging

4. Improved chart visualization:
   - Added highlighting for the latest data point with a red circle
   - Implemented dynamic y-axis calculation based on actual data
   - Added data point indicators to make the visualization more clear
   - Enhanced time range controls for better user experience

5. Fixed timestamp handling in data visualization:
   - Improved timestamp parsing to handle different formats
   - Enhanced time range calculation based on actual data
   - Fixed filtering logic to properly display real-time data
   - Added sorting to ensure proper line drawing

## Active Decisions
- Using SQLite for simplicity in initial phase
- Client-side data simulation for reliable visualization
- d3.js for data visualization with ECG-style appearance
- Mock data generation for testing without real sensors
- Sensor data rate determines visualization update frequency

## Important Patterns
- Strict version control (NextJS14, Python 3.11)
- Clear separation between admin and presentation components
- WebSocket-based data flow
- RESTful API design for user and sensor management
- Component-based architecture for frontend
- Repository pattern for database access in backend
