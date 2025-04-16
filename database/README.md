# EGG Monitor Database

This directory contains the SQLite database files for the EGG Monitor application.

## Files

- `egg_monitor.db`: The main SQLite database file that stores all application data
  - Created automatically when the application starts
  - Contains tables for users, sensors, and sensor data

## Notes

- This directory is mounted as a volume in the Docker container
- The database file is excluded from version control via .gitignore
- For development and testing purposes, sample data is automatically generated when the application starts for the first time

## Database Schema

The database schema includes the following tables:

1. `users`: Stores information about users being monitored
   - `id`: Primary key
   - `user_name`: User's name (unique)
   - `user_age`: User's age

2. `sensors`: Stores information about EGG sensors
   - `id`: Primary key
   - `sensor_name`: Sensor name (unique)
   - `sensor_data_rate`: Data rate in Hz
   - `is_active`: Whether mock data is being produced

3. `sensor_data`: Stores the actual EGG data points
   - `id`: Primary key
   - `sensor_id`: Foreign key to sensors table
   - `timestamp`: Unix timestamp when the data was recorded
   - `value`: The EGG data value

4. `user_sensor_association`: Junction table for many-to-many relationship between users and sensors
   - `user_id`: Foreign key to users table
   - `sensor_id`: Foreign key to sensors table
