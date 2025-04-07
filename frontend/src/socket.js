// socket.js

import { io } from 'socket.io-client';

let socket;

const getSocket = () => {
  if (!socket) {
    const baseUrl = window.location.hostname;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const port = ':9000';

    socket = io(`${protocol}//${baseUrl}${port}`, {
      transports: ['websocket'],
      withCredentials: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000,
      query: {
        clientId: 'like-app-' + Math.random().toString(36).substring(2, 15),
        sessionId: localStorage.getItem('frappe_session_id') || ''
      }
    });

    socket.on('connect', () => {
      console.log('🔌 Connected to WebSocket');
    });

    socket.on('connect_error', (error) => {
      console.error('❌ Socket connection error:', error);
    });

    socket.on('reconnect', (attempt) => {
      console.log(`✅ Reconnected after ${attempt} attempt(s)`);
    });

    socket.onAny((event, ...args) => {
      console.log(`📡 [Socket Event]: ${event}`, args);
    });
  }

  return socket;
};

// Optional debug utility to test connection and track emits
export const debugSocketConnection = () => {
  const socket = getSocket();

  // Emit test event
  socket.emit('test_connection', {
    timestamp: Date.now(),
    message: 'Testing connection'
  });

  // Listen for response
  socket.on('test_connection_ack', (data) => {
    console.log('✅ Server acknowledged test connection:', data);
  });

  // Override emit to log all outgoing events
  const originalEmit = socket.emit;
  socket.emit = function (event, ...args) {
    console.log(`📤 Emitting event: ${event}`, args);
    return originalEmit.apply(this, [event, ...args]);
  };

  return socket;
};

export { getSocket };
