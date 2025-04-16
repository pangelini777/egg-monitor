"use client";

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for WebSocket connections with automatic reconnection
 * @param {string} url - The WebSocket URL to connect to
 * @param {number} timeRange - Time range in seconds for data subscription
 * @param {function} onMessage - Callback function for handling messages
 * @returns {Object} WebSocket connection state and data
 */
const useWebSocket = (url, timeRange = 60, onMessage = null) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  
  // Use refs for values that shouldn't trigger re-renders
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);
  
  // Function to establish WebSocket connection
  const connect = useCallback(() => {
    // Clear any existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // Clear any existing timeouts/intervals
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    
    try {
      // Create new WebSocket connection
      const ws = new WebSocket(url);
      wsRef.current = ws;
      
      // Set up event handlers
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        
        // Send initial subscription message with time range
        ws.send(JSON.stringify({
          type: 'subscribe',
          time_range: timeRange
        }));
        
        // Set up ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Send ping every 30 seconds
      };
      
      ws.onclose = (event) => {
        setIsConnected(false);
        
        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        // Attempt to reconnect after delay
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000); // Reconnect after 3 seconds
      };
      
      ws.onerror = (event) => {
        setError('WebSocket error');
        console.error('WebSocket error:', event);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          
          // Call custom message handler if provided
          if (onMessage && typeof onMessage === 'function') {
            onMessage(data);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };
    } catch (err) {
      setError(`Failed to connect: ${err.message}`);
      console.error('WebSocket connection error:', err);
      
      // Attempt to reconnect after delay
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    }
  }, [url, timeRange, onMessage]);
  
  // Connect when the component mounts or when dependencies change
  useEffect(() => {
    connect();
    
    // Clean up on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);
  
  // Update subscription when timeRange changes
  useEffect(() => {
    if (isConnected && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        time_range: timeRange
      }));
    }
  }, [timeRange, isConnected]);
  
  // Function to manually send a message
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof message === 'string' ? message : JSON.stringify(message));
    } else {
      setError('WebSocket not connected');
    }
  }, []);
  
  // Function to manually reconnect
  const reconnect = useCallback(() => {
    connect();
  }, [connect]);
  
  return {
    isConnected,
    error,
    lastMessage,
    sendMessage,
    reconnect
  };
};

export default useWebSocket;
