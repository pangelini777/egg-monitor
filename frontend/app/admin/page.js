"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdminPanel() {
  // State for users and sensors
  const [users, setUsers] = useState([]);
  const [sensors, setSensors] = useState([]);
  
  // State for form inputs
  const [newUser, setNewUser] = useState({ user_name: '', user_age: '' });
  const [newSensor, setNewSensor] = useState({ sensor_name: '', sensor_data_rate: '100' });
  
  // State for editing
  const [editingUser, setEditingUser] = useState(null);
  const [editingUserData, setEditingUserData] = useState({ user_name: '', user_age: '' });
  const [editingSensor, setEditingSensor] = useState(null);
  const [editingSensorData, setEditingSensorData] = useState({ sensor_name: '', sensor_data_rate: '' });

  // Fetch users and sensors on component mount
  useEffect(() => {
    fetchUsers();
    fetchSensors();
  }, []);

  // Fetch users from API
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

  // Fetch sensors from API
  const fetchSensors = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sensors`);
      if (!response.ok) throw new Error('Failed to fetch sensors');
      const data = await response.json();
      setSensors(data);
    } catch (error) {
      console.error('Error fetching sensors:', error);
    }
  };

  // Handle user form submission
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });
      
      if (!response.ok) throw new Error('Failed to create user');
      
      // Reset form and refresh users
      setNewUser({ user_name: '', user_age: '' });
      fetchUsers();
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  // Handle sensor form submission
  const handleSensorSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sensors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSensor),
      });
      
      if (!response.ok) throw new Error('Failed to create sensor');
      
      // Reset form and refresh sensors
      setNewSensor({ sensor_name: '', sensor_data_rate: '100' });
      fetchSensors();
    } catch (error) {
      console.error('Error creating sensor:', error);
    }
  };

  // Handle user deletion
  const handleDeleteUser = async (userId) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${userId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete user');
      
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  // Handle sensor deletion
  const handleDeleteSensor = async (sensorId) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sensors/${sensorId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete sensor');
      
      fetchSensors();
    } catch (error) {
      console.error('Error deleting sensor:', error);
    }
  };

  // Start editing user
  const startEditUser = (user) => {
    setEditingUser(user.id);
    setEditingUserData({ user_name: user.user_name, user_age: user.user_age });
  };

  // Handle user update
  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${editingUser}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingUserData),
      });
      
      if (!response.ok) throw new Error('Failed to update user');
      
      setEditingUser(null);
      fetchUsers();
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  // Start editing sensor
  const startEditSensor = (sensor) => {
    setEditingSensor(sensor.id);
    setEditingSensorData({ 
      sensor_name: sensor.sensor_name, 
      sensor_data_rate: sensor.sensor_data_rate 
    });
  };

  // Handle sensor update
  const handleUpdateSensor = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sensors/${editingSensor}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingSensorData),
      });
      
      if (!response.ok) throw new Error('Failed to update sensor');
      
      setEditingSensor(null);
      fetchSensors();
    } catch (error) {
      console.error('Error updating sensor:', error);
    }
  };

  // Toggle mock data production
  const toggleMockData = async (sensorId, isActive) => {
    try {
      const action = isActive ? 'stop' : 'start';
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sensors/${sensorId}/mock/${action}`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error(`Failed to ${action} mock data`);
      
      fetchSensors();
    } catch (error) {
      console.error(`Error toggling mock data: ${error}`);
    }
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-primary-700">Admin Panel</h1>
        <Link href="/" className="btn-secondary">
          View Presentation
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Users Section */}
        <section className="card">
          <h2 className="text-2xl font-bold mb-4">Users</h2>
          
          {/* Add User Form */}
          <form onSubmit={handleUserSubmit} className="mb-6">
            <div className="mb-4">
              <label htmlFor="userName" className="block text-sm font-medium text-gray-700 mb-1">
                User Name
              </label>
              <input
                type="text"
                id="userName"
                value={newUser.user_name}
                onChange={(e) => setNewUser({ ...newUser, user_name: e.target.value })}
                className="input-field"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="userAge" className="block text-sm font-medium text-gray-700 mb-1">
                User Age
              </label>
              <input
                type="number"
                id="userAge"
                value={newUser.user_age}
                onChange={(e) => setNewUser({ ...newUser, user_age: e.target.value })}
                className="input-field"
                min="0"
                required
              />
            </div>
            
            <button type="submit" className="btn-primary">
              Add User
            </button>
          </form>
          
          {/* Users List */}
          <div className="space-y-4">
            {users.length === 0 ? (
              <p className="text-gray-500">No users found.</p>
            ) : (
              users.map((user) => (
                <div key={user.id} className="border rounded-md p-4">
                  {editingUser === user.id ? (
                    <form onSubmit={handleUpdateUser} className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          User Name
                        </label>
                        <input
                          type="text"
                          value={editingUserData.user_name}
                          onChange={(e) => setEditingUserData({ ...editingUserData, user_name: e.target.value })}
                          className="input-field"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          User Age
                        </label>
                        <input
                          type="number"
                          value={editingUserData.user_age}
                          onChange={(e) => setEditingUserData({ ...editingUserData, user_age: e.target.value })}
                          className="input-field"
                          min="0"
                          required
                        />
                      </div>
                      
                      <div className="flex space-x-2">
                        <button type="submit" className="btn-primary">
                          Save
                        </button>
                        <button 
                          type="button" 
                          onClick={() => setEditingUser(null)} 
                          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-md transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <div>
                          <h3 className="text-lg font-semibold">{user.user_name}</h3>
                          <p className="text-gray-600">Age: {user.user_age}</p>
                        </div>
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => startEditUser(user)} 
                            className="text-primary-600 hover:text-primary-800"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDeleteUser(user.id)} 
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      
                      {user.sensors && user.sensors.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm font-medium text-gray-700">Sensors:</p>
                          <ul className="text-sm text-gray-600 pl-4">
                            {user.sensors.map((sensor) => (
                              <li key={sensor.id}>{sensor.sensor_name}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
        
        {/* Sensors Section */}
        <section className="card">
          <h2 className="text-2xl font-bold mb-4">Sensors</h2>
          
          {/* Add Sensor Form */}
          <form onSubmit={handleSensorSubmit} className="mb-6">
            <div className="mb-4">
              <label htmlFor="sensorName" className="block text-sm font-medium text-gray-700 mb-1">
                Sensor Name
              </label>
              <input
                type="text"
                id="sensorName"
                value={newSensor.sensor_name}
                onChange={(e) => setNewSensor({ ...newSensor, sensor_name: e.target.value })}
                className="input-field"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="dataRate" className="block text-sm font-medium text-gray-700 mb-1">
                Data Rate (Hz)
              </label>
              <input
                type="number"
                id="dataRate"
                value={newSensor.sensor_data_rate}
                onChange={(e) => setNewSensor({ ...newSensor, sensor_data_rate: e.target.value })}
                className="input-field"
                min="1"
                required
              />
            </div>
            
            <button type="submit" className="btn-primary">
              Add Sensor
            </button>
          </form>
          
          {/* Sensors List */}
          <div className="space-y-4">
            {sensors.length === 0 ? (
              <p className="text-gray-500">No sensors found.</p>
            ) : (
              sensors.map((sensor) => (
                <div key={sensor.id} className="border rounded-md p-4">
                  {editingSensor === sensor.id ? (
                    <form onSubmit={handleUpdateSensor} className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Sensor Name
                        </label>
                        <input
                          type="text"
                          value={editingSensorData.sensor_name}
                          onChange={(e) => setEditingSensorData({ ...editingSensorData, sensor_name: e.target.value })}
                          className="input-field"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Data Rate (Hz)
                        </label>
                        <input
                          type="number"
                          value={editingSensorData.sensor_data_rate}
                          onChange={(e) => setEditingSensorData({ ...editingSensorData, sensor_data_rate: e.target.value })}
                          className="input-field"
                          min="1"
                          required
                        />
                      </div>
                      
                      <div className="flex space-x-2">
                        <button type="submit" className="btn-primary">
                          Save
                        </button>
                        <button 
                          type="button" 
                          onClick={() => setEditingSensor(null)} 
                          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-md transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <div>
                          <h3 className="text-lg font-semibold">{sensor.sensor_name}</h3>
                          <p className="text-gray-600">Data Rate: {sensor.sensor_data_rate}Hz</p>
                          <p className="text-gray-600">
                            Status: {sensor.is_active ? 'Active' : 'Inactive'}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => startEditSensor(sensor)} 
                            className="text-primary-600 hover:text-primary-800"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDeleteSensor(sensor.id)} 
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <button 
                          onClick={() => toggleMockData(sensor.id, sensor.is_active)}
                          className={`${
                            sensor.is_active 
                              ? 'bg-red-500 hover:bg-red-600' 
                              : 'bg-green-500 hover:bg-green-600'
                          } text-white font-semibold py-1 px-3 rounded-md text-sm transition-colors`}
                        >
                          {sensor.is_active ? 'Stop' : 'Start'} Mock Data
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
