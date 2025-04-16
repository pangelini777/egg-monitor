"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function PresentationScreen() {
  const [users, setUsers] = useState([]);
  const [timeRange, setTimeRange] = useState(60); // Default 60 seconds (1 minute)

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

  // This would be replaced with actual WebSocket connection in a real implementation
  useEffect(() => {
    // Placeholder for WebSocket connection
    console.log('Would connect to WebSocket here with time range:', timeRange);
    
    // Cleanup function
    return () => {
      console.log('Would disconnect from WebSocket here');
    };
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
                      </h3>
                      <div className="bg-gray-100 p-4 rounded-md h-48 flex items-center justify-center">
                        <p className="text-gray-500">Chart visualization will appear here</p>
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
