<template>
  <div class="p-4 max-w-sm mx-auto bg-white rounded-xl shadow-md space-y-4">
    <!-- Display current like count -->
    <p class="text-lg font-semibold">Likes: {{ likes }}</p>

    <!-- Like button -->
    <button
      @click="sendLike"
      class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
    >
      Like
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import io from 'socket.io-client';

// API and WebSocket URLs
const BASE_URL = `http://${window.location.hostname}:8080/api/method/decode.get`;
const SOCKET_URL = `${window.location.hostname}:9000`;

const likes = ref(0); // Store like count
let socket = null; // WebSocket connection
let intervalId = null; // Interval for auto-refreshing
let inactivityTimer = null; // Timer to stop refreshing
let restartTimer = null; // Timer to restart auto-refresh

// Function to connect to WebSocket for real-time updates
const connectSocket = () => {
  socket = io(SOCKET_URL, { transports: ['websocket'] });

  socket.on('connect', () => console.log('✅ Connected to WebSocket'));
  socket.on('disconnect', () => console.log('❌ Disconnected from WebSocket'));

  socket.on('update_likes', (data) => {
    if (data?.likes !== undefined) {
      likes.value = data.likes; // Update like count when a new like is received
      console.log('🔄 Likes updated:', data.likes);
    }
  });
};

// Function to get the latest like count from the API
const fetchLikeCount = async () => {
  try {
    const response = await fetch(`${BASE_URL}.get_likes`, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await response.json();
    if (data?.message?.likes !== undefined) {
      likes.value = data.message.likes; // Update likes from API
      console.log('✅ Updated likes:', data.message.likes);
    }
  } catch (error) {
    console.error('❌ Error fetching likes:', error);
  }
};

// Function to send a like to the server
const sendLike = async () => {
  try {
    const response = await fetch(`${BASE_URL}.send_like`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await response.json();
    if (data?.message?.likes !== undefined) {
      likes.value = data.message.likes; // Update likes after sending
      console.log('👍 Like sent:', data.message.likes);
    }

    resetInactivityTimer(); // Reset inactivity timer on click
  } catch (error) {
    console.error('❌ Error sending like:', error);
  }
};

// Function to start the auto-refresh interval
const startAutoRefresh = () => {
  if (intervalId) clearInterval(intervalId); // Clear existing interval
  intervalId = setInterval(fetchLikeCount, 2000); // Fetch data every 2 sec
  console.log('⏳ Auto-refresh started');
};

// Function to stop auto-refresh due to inactivity
const stopAutoRefresh = () => {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
    console.log('⏹️ Auto-refresh stopped due to inactivity');
  }

  // Schedule auto-refresh to restart after 10 seconds
  restartTimer = setTimeout(() => {
    startAutoRefresh(); // Restart auto-refresh
    console.log('🔄 Auto-refresh restarted after 10 sec');
  }, 10000);
};

// Function to reset the inactivity timer when user interacts
const resetInactivityTimer = () => {
  if (inactivityTimer) clearTimeout(inactivityTimer); // Clear existing timer
  if (restartTimer) clearTimeout(restartTimer); // Clear restart timer

  startAutoRefresh(); // Restart auto-refresh immediately on user interaction

  inactivityTimer = setTimeout(() => {
    stopAutoRefresh(); // Stop auto-refresh after 5 sec of inactivity
  }, 5000);
};

// Lifecycle hooks: Run when the component is mounted/unmounted
onMounted(() => {
  fetchLikeCount(); // Fetch initial likes
  connectSocket(); // Connect to WebSocket

  // Start listening for user interactions
  window.addEventListener('mousemove', resetInactivityTimer);
  window.addEventListener('keydown', resetInactivityTimer);
  window.addEventListener('click', resetInactivityTimer);

  resetInactivityTimer(); // Start the timer initially
});

onUnmounted(() => {
  if (socket) {
    socket.disconnect(); // Clean up WebSocket connection
    console.log('🔌 Socket disconnected');
  }

  if (intervalId) clearInterval(intervalId); // Stop auto-refresh interval
  if (inactivityTimer) clearTimeout(inactivityTimer); // Clear inactivity timer
  if (restartTimer) clearTimeout(restartTimer); // Clear restart timer

  // Remove event listeners
  window.removeEventListener('mousemove', resetInactivityTimer);
  window.removeEventListener('keydown', resetInactivityTimer);
  window.removeEventListener('click', resetInactivityTimer);

  console.log('🛑 Cleanup complete');
});
</script>
