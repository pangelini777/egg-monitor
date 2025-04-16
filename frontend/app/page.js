"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import EggChart from '../components/EggChart';
import useWebSocket from '../hooks/useWebSocket';

export default function PresentationScreen() {
  const [users, setUsers] = useState([]);
  const [timeRange, setTimeRange] = useState(60); // Default 60 seconds (1 minute)
  const [sensorData, setSensorData] = useState({});
  const [connectionStatus, setConnectionStatus] = useState({});
  
  // Fetch users and their sensors
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users`);
        if (!response.ok) throw new Error('Failed to fetch users');
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    fetchUsers();
    // Set up polling to refresh data
    const interval = setInterval(fetchUsers, 10000); // Refresh every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for all sensors
  const { lastMessage, connectionStatus: wsConnectionStatus, sendMessage, reconnect } = useWebSocket('/api/ws/all', timeRange);
  
  // Ref to store active sensor IDs
  const activeSensorIds = useRef(new Set());
  
  // Process incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        // lastMessage should already be parsed by the useWebSocket hook
        const data = lastMessage;
        
        // Handle different message types
        if (data.event === 'connected') {
          console.log('Connected to WebSocket server');
          
          // Subscribe to all available sensors
          const allSensorIds = [];
          users.forEach(user => {
            if (user.sensors && user.sensors.length > 0) {
              user.sensors.forEach(sensor => {
                allSensorIds.push(sensor.id);
                
                // Update connection status
                setConnectionStatus(prev => ({
                  ...prev,
                  [sensor.id]: true
                }));
              });
            }
          });
          
          // Store active sensor IDs
          activeSensorIds.current = new Set(allSensorIds);
          
          // Send subscription message
          if (allSensorIds.length > 0) {
            const subscriptionMessage = {
              type: 'subscribe',
              sensor_ids: allSensorIds,
              time_range: timeRange
            };
            
            // Send subscription message
            if (wsConnectionStatus === 'OPEN') {
              console.log('Subscribing to sensors:', allSensorIds);
              sendMessage(JSON.stringify(subscriptionMessage));
            }
          }
        }
        // Handle incoming data
        else if (data.event === 'data' && data.sensor_id) {
          const now = Math.floor(Date.now() / 1000);
          
          // Update sensor data
          setSensorData(prevData => {
            // Initialize sensor data array if it doesn't exist
            const sensorDataArray = prevData[data.sensor_id] || [];
            
            // Add new data point
            // Ensure timestamp and value are numbers
            const timestamp = typeof data.timestamp === 'number' ? data.timestamp : parseFloat(data.timestamp);
            const value = typeof data.value === 'number' ? data.value : parseFloat(data.value);
            
            
            // Add new data point
            const newData = [
              ...sensorDataArray,
              {
                timestamp: timestamp || now,
                value: value
              }
            ];
            
            
            // Remove data older than 5 minutes
            const maxAge = 300; // 5 minutes in seconds
            const filteredData = newData.filter(d => {
              const pointTimestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
              return pointTimestamp >= now - maxAge;
            });
            
            // Log how many points were removed
            const removedCount = newData.length - filteredData.length;
            
            
            return {
              ...prevData,
              [data.sensor_id]: filteredData
            };
          });
          
          // Update connection status
          setConnectionStatus(prev => ({
            ...prev,
            [data.sensor_id]: true
          }));
        }
        // Handle batch data for multiple sensors
        else if (data.event === 'batch_data' && data.data) {
          const now = Math.floor(Date.now() / 1000);
          
          // Update sensor data for all sensors in the batch
          setSensorData(prevData => {
            const updatedData = { ...prevData };
            
            // Process each sensor's data
            Object.entries(data.data).forEach(([sensorId, dataPoints]) => {
              // Convert sensorId to number if needed
              const numericSensorId = parseInt(sensorId);
              
              // Initialize sensor data array if it doesn't exist
              const sensorDataArray = updatedData[numericSensorId] || [];
              
              // Add all new data points
              const newDataPoints = dataPoints.map(point => {
                // Ensure timestamp and value are numbers
                const timestamp = typeof point.timestamp === 'number' ? point.timestamp : parseFloat(point.timestamp);
                const value = typeof point.value === 'number' ? point.value : parseFloat(point.value);
                
                return {
                  timestamp: timestamp || now,
                  value: value
                };
              });
              
              // Combine existing and new data
              const combinedData = [...sensorDataArray, ...newDataPoints];
              
              // Remove data older than 5 minutes
              const now = Math.floor(Date.now() / 1000);
              const maxAge = 300; // 5 minutes in seconds
              
              const filteredData = combinedData.filter(d => {
                const timestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
                return timestamp >= now - maxAge;
              });
              
              // Log how many points were removed
              const removedCount = combinedData.length - filteredData.length;
              
              
              // Update data for this sensor
              updatedData[numericSensorId] = filteredData;
              
              // Update connection status for this sensor
              setConnectionStatus(prev => ({
                ...prev,
                [numericSensorId]: true
              }));
            });
            
            return updatedData;
          });
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    }
  }, [lastMessage, users, timeRange, wsConnectionStatus, sendMessage]);
  
  // Re-subscribe when timeRange changes
  useEffect(() => {
    if (wsConnectionStatus === 'OPEN' && users.length > 0) {
      const allSensorIds = [];
      users.forEach(user => {
        if (user.sensors && user.sensors.length > 0) {
          user.sensors.forEach(sensor => {
            allSensorIds.push(sensor.id);
          });
        }
      });
      
      if (allSensorIds.length > 0) {
        const subscriptionMessage = {
          type: 'subscribe',
          sensor_ids: allSensorIds,
          time_range: timeRange
        };
        
        console.log('Updating subscription with new time range:', timeRange);
        sendMessage(JSON.stringify(subscriptionMessage));
      }
    }
    
    // Log current data for debugging
    console.log(`Time range changed to ${timeRange} seconds`);
    Object.entries(sensorData).forEach(([sensorId, data]) => {
      if (data && data.length > 0) {
        
        // Convert timestamps to numbers for consistent comparison
        const timestamps = data.map(d => typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp));
        
        // Calculate time span
        const minTime = Math.min(...timestamps);
        const maxTime = Math.max(...timestamps);
        
        // Calculate how many points should be visible with current time range
        const now = Math.floor(Date.now() / 1000);
        const cutoffTime = now - timeRange;
        const visiblePoints = timestamps.filter(t => t >= cutoffTime).length;
      }
    });
  }, [timeRange, wsConnectionStatus, users, sendMessage]);
  
  // Clean up old data periodically
  useEffect(() => {
    // Function to clean up old data
    const cleanupOldData = () => {
      const now = Math.floor(Date.now() / 1000);
      const maxAge = 300; // 5 minutes in seconds
      
      setSensorData(prevData => {
        const updatedData = {};
        
        // For each sensor, remove data older than 5 minutes
        Object.keys(prevData).forEach(sensorId => {
          // Filter out data older than 5 minutes
          const filteredData = prevData[sensorId].filter(d => {
            const timestamp = typeof d.timestamp === 'number' ? d.timestamp : parseFloat(d.timestamp);
            return timestamp >= now - maxAge;
          });
          
          updatedData[sensorId] = filteredData;
          
          // Log how many points were removed
          const removedCount = prevData[sensorId].length - filteredData.length;

        });
        
        return updatedData;
      });
    };
    
    // Run cleanup every 5 seconds
    const cleanupInterval = setInterval(cleanupOldData, 5000);
    
    // Clean up interval on unmount
    return () => clearInterval(cleanupInterval);
  }, [timeRange]);

  return (
    <main className="container mx-auto px-4 py-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-primary-700">EGG Monitor</h1>
        <Link href="/admin" className="btn-primary">
          Admin Panel
        </Link>
      </header>

      <div className="mb-6">
        <label htmlFor="timeRange" className="block text-sm font-medium text-gray-700 mb-1">
          Time Range: {timeRange} seconds
        </label>
        <input
          type="range"
          id="timeRange"
          min="10"
          max="300"
          step="10"
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      {users.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600">No users found. Add users in the admin panel.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {users.map((user) => (
            <div key={user.id} className="card">
              <h2 className="text-xl font-semibold mb-4">{user.user_name} ({user.user_age} years)</h2>
              
              {user.sensors && user.sensors.length > 0 ? (
                <div>
                  {user.sensors.map((sensor) => (
                    <div key={sensor.id} className="mb-4">
                      <h3 className="text-lg font-medium text-gray-700 mb-2">
                        {sensor.sensor_name} ({sensor.sensor_data_rate}Hz)
                        <span className={`ml-2 text-xs ${connectionStatus[sensor.id] ? 'text-green-500' : 'text-red-500'}`}>
                          {connectionStatus[sensor.id] ? '● Connected' : '● Disconnected'}
                        </span>
                      </h3>
                      <div className="bg-gray-100 p-4 rounded-md">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Data points: {(sensorData[sensor.id] || []).length}</span>
                          <span>Sensor ID: {sensor.id}</span>
                        </div>
                        {(sensorData[sensor.id] || []).length > 0 ? (
                          <>
                            <EggChart
                              data={sensorData[sensor.id] || []}
                              width={350}
                              height={180}
                              timeRange={timeRange}
                            />
                            <div className="text-xs text-gray-500 mt-1">
                              Latest value: {
                                sensorData[sensor.id] && sensorData[sensor.id].length > 0
                                  ? (() => {
                                      // Sort data by timestamp to find the latest
                                      const sortedData = [...sensorData[sensor.id]].sort((a, b) => {
                                        const aTime = typeof a.timestamp === 'number' ? a.timestamp : parseFloat(a.timestamp);
                                        const bTime = typeof b.timestamp === 'number' ? b.timestamp : parseFloat(b.timestamp);
                                        return bTime - aTime; // Descending order
                                      });
                                      return sortedData[0].value.toFixed(4);
                                    })()
                                  : 'N/A'
                              }
                            </div>
                          </>
                        ) : (
                          <div className="flex items-center justify-center" style={{ height: 180 }}>
                            <p className="text-gray-500">Waiting for data...</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No sensors assigned to this user</p>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
