# EGG Monitor - Product Context

## Purpose
The EGG Monitor provides real-time visualization of EGG (electrogastrogram) data through:
1. An administration panel for managing users and sensors
2. A presentation screen for data visualization

## User Needs
### Administration Panel
- Create/manage users (name + age)
- Create/manage sensors (name + data rate)
- Control mock data production (start/stop at 100Hz default)

### Presentation Screen
- Beautiful visualization of sensor data per user
- Interactive time range selection (default 1 minute)
- Clear association between users and their sensors

## UX Goals
- **Admin Panel**: Intuitive CRUD operations with clear feedback
- **Presentation**: Visually appealing charts with smooth animations
- **Responsiveness**: Real-time updates via WebSockets
- **Accessibility**: Clear data presentation for medical professionals
