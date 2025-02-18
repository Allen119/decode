<template>
    <div class="chat-room">
      <div v-if="typingUsers.length > 0" class="typing-indicator">
        {{ typingUsers.join(', ') }} {{ typingUsers.length === 1 ? 'is' : 'are' }} typing...
      </div>
      <div class="message-input">
        <input
          type="text"
          v-model="message"
          @input="handleTyping"
          placeholder="Type a message..."
        />
        <button @click="sendMessage">Send</button>
      </div>
      <!-- Debug info -->
      <div class="debug-info">
        <p>Socket Status: {{ socketStatus }}</p>
        <p>Typing Users: {{ typingUsers }}</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import io from 'socket.io-client'
  
  const roomId = 'global-chat'
  const message = ref('')
  const typingUsers = ref([])
  const socketStatus = ref('Not connected')
  let typingTimeout = null
  
  // Initialize socket connection
  const initSocket = () => {
    console.log('Initializing socket...')  // Debug log
    const socket = io(`${window.location.hostname}:9000`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5
    })
    
    window.socket = socket
  
    socket.on('connect', () => {
      console.log('Socket connected')
      socketStatus.value = 'Connected'
    })
  
    socket.on('disconnect', () => {
      console.log('Socket disconnected')
      socketStatus.value = 'Disconnected'
    })
  
    socket.on('error', (error) => {
      console.error('Socket error:', error)
      socketStatus.value = 'Error'
    })
  
    return socket
  }
  
  // Setup Frappe realtime
  window.frappe = {
    socketio_port: 9000,
    realtime: {
      on: (event, callback) => {
        console.log(`Setting up listener for event: ${event}`)  // Debug log
        if (!window.socket) {
          initSocket()
        }
        window.socket.on(event, (data) => {
          console.log(`Received ${event} event:`, data)  // Debug log
          callback(data)
        })
      },
      off: (event, callback) => {
        if (window.socket) {
          window.socket.off(event, callback)
        }
      }
    }
  }
  
  const setupSocketListener = () => {
    window.frappe.realtime.on('typing_update', (data) => {
      console.log('Received typing update:', data)  // Debug log
      if (data.room_id === roomId) {
        updateTypingUsers(data.user, data.is_typing)
      }
    })
  }
  
  const handleTyping = async () => {
    if (typingTimeout) clearTimeout(typingTimeout)
    
    console.log('Sending typing notification...')  // Debug log
    
    try {
      const response = await fetch('/api/method/decode.get.notify_typing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          room_id: roomId, 
          is_typing: true 
        })
      })
      const data = await response.json()
      console.log('Typing notification response:', data)  // Debug log
    } catch (error) {
      console.error('Error sending typing notification:', error)
    }
  
    typingTimeout = setTimeout(async () => {
      try {
        const response = await fetch('/api/method/decode.get.notify_typing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            room_id: roomId, 
            is_typing: false 
          })
        })
        const data = await response.json()
        console.log('Clear typing notification response:', data)  // Debug log
      } catch (error) {
        console.error('Error clearing typing notification:', error)
      }
    }, 2000)
  }
  
  const updateTypingUsers = (user, isTyping) => {
    console.log(`Updating typing users: ${user} is ${isTyping ? 'typing' : 'not typing'}`)  // Debug log
    if (isTyping && !typingUsers.value.includes(user)) {
      typingUsers.value.push(user)
    } else if (!isTyping) {
      typingUsers.value = typingUsers.value.filter(u => u !== user)
    }
  }
  
  const sendMessage = () => {
    console.log('Sending message:', message.value)
    message.value = ''
  }
  
  onMounted(() => {
    console.log('Component mounted, setting up socket...')  // Debug log
    setupSocketListener()
  })
  
  onUnmounted(() => {
    console.log('Component unmounting, cleaning up...')  // Debug log
    if (window.socket) {
      window.socket.off('typing_update')
    }
  })
  </script>
  
  <style scoped>
  .chat-room {
    padding: 20px;
  }
  
  .typing-indicator {
    color: #666;
    font-style: italic;
    margin-bottom: 10px;
  }
  
  .message-input {
    display: flex;
    gap: 10px;
  }
  
  input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  button {
    padding: 8px 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #45a049;
  }
  </style>
  