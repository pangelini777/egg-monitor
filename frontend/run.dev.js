/**
 * Development server script for the EGG Monitor frontend.
 * This script starts the Next.js development server.
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('EGG Monitor Frontend');
console.log('====================');

// Start the Next.js development server
console.log('\nStarting Next.js development server...');
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

const nextDev = spawn('npm', ['run', 'dev'], {
  stdio: 'inherit',
  shell: true,
  env: {
    ...process.env,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
});

// Handle process exit
nextDev.on('close', (code) => {
  console.log(`Next.js development server exited with code ${code}`);
});

// Handle errors
nextDev.on('error', (err) => {
  console.error('Failed to start Next.js development server:', err);
});

console.log('\nPress Ctrl+C to stop the server');
