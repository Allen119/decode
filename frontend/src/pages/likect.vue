<template>
  <div class="p-4 max-w-sm mx-auto bg-white rounded-xl shadow-md space-y-4">
    <p class="text-lg font-semibold">Likes: {{ likes }}</p>
    <button
      @click="sendLike"
      class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
    >
      Like
    </button>
    <div class="mt-4 text-xs text-gray-500 border-t pt-2">
      <div class="flex items-center justify-between">
        <span>
          Socket:
          <span :class="isConnected ? 'text-green-500 font-medium' : 'text-red-500 font-medium'">
            {{ isConnected ? 'Connected' : 'Disconnected' }}
          </span>
        </span>
        <button
          @click="reconnectWebSocket"
          class="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300"
        >
          Reconnect
        </button>
      </div>
      <div v-if="lastUpdateTime" class="mt-1">
        Last update: {{ lastUpdateTime }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { getSocket } from '../socket';

const BASE_URL = `http://${window.location.hostname}:8080/api/method/decode.get`;
const likes = ref(0);
const isConnected = ref(false);
const lastUpdateTime = ref(null);
const connectionAttempts = ref(0);
const maxReconnectAttempts = 3;
let socketInstance = null;

// Document constants for WebSocket subscription
const DOCTYPE = "LikeCounter";
const DOCNAME = "hey";

const fetchLikeCount = async () => {
  try {
    const response = await fetch(`${BASE_URL}.get_likes`, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await response.json();
    if (data?.message?.likes !== undefined) {
      likes.value = data.message.likes;
      console.log('✅ Initial likes:', data.message.likes);
    }
  } catch (error) {
    console.error('❌ Error fetching likes:', error);
  }
};

const sendLike = async () => {
  try {
    const response = await fetch(`${BASE_URL}.send_like`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await response.json();
    if (data?.message?.likes !== undefined) {
      likes.value = data.message.likes;
      console.log('👍 Like sent:', data.message.likes);
    }
  } catch (error) {
    console.error('❌ Error sending like:', error);
  }
};

const handleLikesUpdate = (data) => {
  if (data?.likes !== undefined) {
    likes.value = data.likes;
    lastUpdateTime.value = new Date().toLocaleTimeString();
    console.log('📡 Real-time update received:', data.likes, 'at', lastUpdateTime.value);
  } else {
    console.warn('⚠️ Received update_likes event with invalid data:', data);
  }
};

const debugSocketEvents = () => {
  console.log('🔍 Setting up debug listeners');
  
  // Listen for ALL events to debug
  socketInstance.onAny((event, ...args) => {
    console.log(`🔔 Socket event received: ${event}`, args);
  });
};

const setupRealtimeListeners = () => {
  socketInstance = getSocket();
  isConnected.value = socketInstance.connected;

  if (!isConnected.value && connectionAttempts.value < maxReconnectAttempts) {
    console.log(`🔄 Attempting WebSocket connection (try ${connectionAttempts.value + 1})...`);
    socketInstance.connect();
    connectionAttempts.value++;
  }

  socketInstance.on('connect', () => {
    isConnected.value = true;
    console.log('🟢 WebSocket connected!');
    
    // Subscribe to Frappe's WebSocket channels in different ways to ensure reception
    socketInstance.emit('doctype', DOCTYPE);
    socketInstance.emit('task_subscribe', DOCNAME);
    
    // Join the document room
    const roomName = `doc:${DOCTYPE}:${DOCNAME}`;
    socketInstance.emit('join', roomName);
    console.log(`🔔 Joined room: ${roomName}`);
    
    // Also try standard Socket.io subscription
    socketInstance.emit('subscribe', {
      doctype: DOCTYPE,
      docname: DOCNAME
    });
  });

  socketInstance.on('disconnect', () => {
    isConnected.value = false;
    console.log('🔴 WebSocket disconnected!');
  });

  // Listen for the basic update_likes event (most likely to work)
  socketInstance.on('update_likes', handleLikesUpdate);
  
  // Also listen for namespace'd events in various formats Frappe might use
  socketInstance.on(`${DOCTYPE}:${DOCNAME}:update_likes`, handleLikesUpdate);
  socketInstance.on(`doc:${DOCTYPE}:${DOCNAME}:update_likes`, handleLikesUpdate);
  socketInstance.on(`${DOCTYPE}/${DOCNAME}/update_likes`, handleLikesUpdate);
};

const reconnectWebSocket = () => {
  console.log('🔄 Forcing WebSocket reconnection...');
  socketInstance?.disconnect();
  
  setTimeout(() => {
    socketInstance?.connect();
  }, 300);
};

onMounted(() => {
  fetchLikeCount();
  setupRealtimeListeners();
  debugSocketEvents(); // Add debug listeners
  
  setTimeout(() => {
    if (!isConnected.value) {
      reconnectWebSocket();
    }
  }, 1000);
});

onUnmounted(() => {
  // Clean up all event listeners
  socketInstance?.off('update_likes', handleLikesUpdate);
  socketInstance?.off(`${DOCTYPE}:${DOCNAME}:update_likes`, handleLikesUpdate);
  socketInstance?.off(`doc:${DOCTYPE}:${DOCNAME}:update_likes`, handleLikesUpdate);
  socketInstance?.off(`${DOCTYPE}/${DOCNAME}/update_likes`, handleLikesUpdate);
  socketInstance?.offAny(); // Remove debug listeners
  
  // Leave channels/rooms
  const roomName = `doc:${DOCTYPE}:${DOCNAME}`;
  socketInstance?.emit('leave', roomName);
  
  // Unsubscribe
  socketInstance?.emit('unsubscribe', {
    doctype: DOCTYPE,
    docname: DOCNAME
  });
  
  console.log('🧹 Cleaned up WebSocket listeners and subscriptions');
});
</script>