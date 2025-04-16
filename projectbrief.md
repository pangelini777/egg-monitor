# EGG Monitor

## Project description

The EGG monitor is a tool that allows a user to monitor the EGG. The interface is beautifully designed and is composed of 2 main components:

1. An administration panel
1. A presentation screen

### Components description

The administration panel allows the user to do the following:

- create/edit/delete users (user_name + user_age)
- create/edit/delete sensors (sensor_name + sensor_data_rate)
- delete sensors (by sensor_name)
- delete users (by user_name)
- start/stop mock data production for any sensor (default sensor_data_rate is 100Hz)

In the administration panel there is no limit to the users and sensors to create.

The presentation screen is a beautiful page where the user and sensor data is presented. 
For each user, a chart will display the associated sensors data. A slider will allow to set the timerange for the data to show (default 1 minute)

## Tech stack

### Frontend
- NextJS14 (NO NextJS15!!!)
- d3.js for the charts
- Tailwind for the CSS

### Backend
- Python 3.11
- FastAPI
- WebSockets for communication

### Database
- SQLite to record sensors data

### DevOps
- Dockerfile for every service
- docker compose file to startup the project
- GitHub to maintain the repository (you can create a new repo at the beginning of the project using the MCP server)

## Tech mandatory rules

You need to mandatory follow these rules:

- Code must be clean and understandable
- Section of codes must be commented (in a short and understandable manner)
- The backend need unit tests
- The frontend requires integration tests
- Always provide the full code, DON'T BE LAZY!