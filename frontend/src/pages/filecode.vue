<template>
  <div id="app" class="font-sans h-screen w-screen bg-gradient-to-br from-black to-gray-800 text-white flex flex-col">
    <!-- Header -->
    <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%]"
      :style="{ fontFamily: 'Inter, sans-serif' }">
      <!-- Logo and User ID Section -->
      <div class="flex items-center gap-4">
        <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
          :style="{ maxHeight: '80%', width: '10%', height: 'auto' }" />
        <span class="text-lg text-black">{{ fileName }}</span> <!-- File name displayed here -->
      </div>
      <!-- Action Buttons Section -->
      <div class="flex items-center gap-4">
        <button @click="saveCode"
          class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">Save</button>
        <button @click="shareCode"
          class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">Share</button>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- Code Editor -->
      <div class="bg-gray-900 p-4 flex-shrink-0 h-full overflow-y-auto " :style="{ width: `${codeEditorWidth}px` }">
        <!-- CodeMirror Editor -->
        <div ref="codeMirrorContainer" class="w-full h-full"></div>
      </div>

      <!-- Resize Handle -->
      <div class="w-2 cursor-ew-resize bg-gray-700 hover:bg-gray-500 transition-colors" @mousedown="startResize"></div>

      <!-- Console Output with Terminal -->
      <div class="bg-gray-800 p-4 flex flex-col flex-shrink-0 h-full overflow-y-auto"
        :style="{ width: `${consoleWidth}px` }">
        <h3 class="text-lg font-semibold text-orange-500">Console Output</h3>
        <div class="bg-black rounded mt-4 flex-1 relative">
          <div ref="terminalContainer" class="absolute inset-0"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import { EditorView, basicSetup } from 'codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import io from 'socket.io-client'

// API and WebSocket URLs
const API_URL = `http://${window.location.hostname}:8080/api/method/decode.api.update_code`;
const SOCKET_URL = `${window.location.hostname}:9000`;

const route = useRoute();
const codeMirrorContainer = ref(null);
const editor = ref(null);
const fileName = ref(""); // Store filename
const currentInput = ref('');
const socket = ref(null);
const codeContent = ref('');
let isUpdating = false;
let intervalId = null; 
let inactivityTimeout = null;
let isPaused = false; // Track if auto-refresh is paused

// Constants for minimum widths
const MIN_EDITOR_WIDTH = 400;
const MIN_CONSOLE_WIDTH = 300;

// Terminal refs
const terminalContainer = ref(null);
const terminal = ref(null);
const fitAddon = ref(null);

const commandHistory = ref([]);
const historyIndex = ref(-1);

// Reactive state
const codeEditorWidth = ref(0);
const consoleWidth = ref(0);

const connectSocket = () => {
  try {
    console.log('🔄 Attempting to connect to WebSocket at:', SOCKET_URL);
    
    socket.value = io(SOCKET_URL, { 
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      debug: true  // Enable socket.io debugging
    });

    // Add debugging for all socket events
    socket.value.onAny((event, ...args) => {
      console.log('🔍 Socket Event:', event, 'Data:', args);
    });

    socket.value.on('connect', () => {
      console.log('✅ Connected to WebSocket');
      console.log('🔌 Socket Details:', {
        id: socket.value.id,
        connected: socket.value.connected,
        disconnected: socket.value.disconnected,
        transport: socket.value.io.engine.transport.name
      });
    });

    // Add specific handler for code_update
    socket.value.on('code_update', (data) => {
      console.log('📥 Received code update:', {
        event: 'code_update',
        fileUuid: data?.file_uuid,
        currentFileUuid: route.params.uuid,
        hasCode: Boolean(data?.code),
        codeLength: data?.code?.length,
        modified: data?.modified
      });

      if (data?.file_uuid === route.params.uuid && data?.code !== undefined) {
        updateEditorContent(data.code);
        console.log('✅ Editor updated with new code');
      }
    });

    // Error handling
    socket.value.on('connect_error', (error) => {
      console.error('⚠️ Socket connection error:', {
        error: error.message,
        type: error.type,
        description: error.description
      });
    });

    socket.value.on('disconnect', (reason) => {
      console.log('❌ Socket disconnected:', {
        reason,
        wasConnected: socket.value?.connected,
        transport: socket.value?.io?.engine?.transport?.name
      });
    });

  } catch (error) {
    console.error('❌ Socket initialization error:', error);
  }
};

// Cleanup socket connection
const cleanupSocket = () => {
  try {
    if (socket.value) {
      socket.value.disconnect();
      socket.value = null;
      console.log('🔌 Socket disconnected and cleaned up');
    }
  } catch (error) {
    console.error('⚠️ Error cleaning up socket:', error);
  }
};

// Update editor content without triggering the update listener
const updateEditorContent = (newCode) => {
  if (editor.value && !isUpdating) {
    isUpdating = true;
    const transaction = editor.value.state.update({
      changes: {
        from: 0,
        to: editor.value.state.doc.length,
        insert: newCode
      }
    });
    editor.value.dispatch(transaction);
    isUpdating = false;
  }
};

const initEditor = () => {
  const fileUuid = route.params.uuid;
  if (codeMirrorContainer.value && !editor.value) {
    editor.value = new EditorView({
      doc: codeContent.value,
      extensions: [
        basicSetup,
        javascript(),
        oneDark,
        EditorView.updateListener.of(async (update) => {
          if (update.docChanged && !isUpdating) {
            const newCode = update.state.doc.toString();
            codeContent.value = newCode;

            // Debug log before saving
            console.log('📤 Saving code:', {
              fileUuid,
              codeLength: newCode.length,
              timestamp: new Date().toISOString()
            });

            try {
              const response = await fetch(
                `${API_URL}?file_uuid=${encodeURIComponent(fileUuid)}&code=${encodeURIComponent(newCode)}`,
                {
                  method: "PUT",
                  credentials: 'include',
                  headers: { 'Content-Type': 'application/json' }
                }
              );

              if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
              }

              const data = await response.json();
              
              // Enhanced success logging
              console.log('💾 Save response:', {
                status: data.status,
                message: data.message,
                fileDetails: data.file,
                timestamp: new Date().toISOString()
              });

              // Check if we received a websocket broadcast confirmation
              if (data.message?.websocket_broadcast == true) {
                console.log('📡 WebSocket broadcast confirmed by server');
              }

            } catch (error) {
              // Enhanced error logging
              console.error('❌ Save error:',{
                error: error.message,
                type: error.name,
                fileUuid,
                timestamp: new Date().toISOString()
              });
            }
          }
        }),
      ],
      parent: codeMirrorContainer.value,
    });

    console.log('✨ Editor initialized:', {
      fileUuid,
      initialContentLength: codeContent.value.length,
      timestamp: new Date().toISOString()
    });
  }
};


// Fetch file details from the API
const fetchFileDetails = async () => {
  if (isPaused) return; // Skip fetching if paused

  try {
    const uuid = route.params.uuid;
    const response = await fetch(
      `http://decode.local:8080/api/method/decode.api.getfiles?search_uuid=${uuid}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    const data = await response.json();
    console.log("API Response:", data);

    if (data.message.message === "You should log in first.") {
      alert("Login please!!");
      return;
    }

    if (data.message && data.message.file) {
      fileName.value = data.message.file.filename;
      if (editor.value) {
        editor.value.dispatch({
          changes: {
            from: 0,
            to: editor.value.state.doc.length,
            insert: data.message.file.code || ''
          }
        });
      }
    } else {
      alert(data.message);
    }
  } catch (error) {
    console.error("Error fetching file details:", error);
    if (terminal.value) {
      terminal.value.writeln('Error loading file data...');
    }
  }
};

// Start auto-refresh
const startAutoRefresh = () => {
  if (intervalId) clearInterval(intervalId);
  intervalId = setInterval(fetchFileDetails, 5000); // Fetch every 5 sec
  console.log('⏳ Auto-refresh started');
};

// Pause and Resume Mechanism
const resetInactivityTimer = () => {
  clearTimeout(inactivityTimeout);
  
  if (isPaused) {
    isPaused = false;
    console.log("🔄 Resuming auto-refresh...");
    startAutoRefresh(); // Restart auto-refresh if it was paused
  }

  inactivityTimeout = setTimeout(() => {
    console.log("🛑 No activity detected! Pausing updates for 10 sec...");
    isPaused = true;
    clearInterval(intervalId); // Stop auto-refresh

    setTimeout(() => {
      console.log("✅ Resuming updates after 10 sec...");
      isPaused = false;
      startAutoRefresh();
    }, 10000); // Wait 10 sec before resuming
  }, 5000); // 5 sec of inactivity triggers pause
};


// Handle terminal input
const handleTerminalInput = (data) => {
  const char = data;

  if (char === '\x7F' || char === '\b') { // Backspace
    if (currentInput.value.length > 0) {
      currentInput.value = currentInput.value.slice(0, -1);
      terminal.value.write('\b \b');
    }
  }
  else if (char === '\r') { // Enter
    terminal.value.writeln('');
    if (currentInput.value.trim() !== '') {
      commandHistory.value.unshift(currentInput.value.trim()); // Store command in history
      historyIndex.value = -1; // Reset history navigation
    }
    handleCommand(currentInput.value);
    currentInput.value = '';
    terminal.value.write('$ ');
  }
  else if (char === '\x1b[A') { // Up arrow
    if (historyIndex.value < commandHistory.value.length - 1) {
      historyIndex.value++;
      updateTerminalInput(commandHistory.value[historyIndex.value]);
    }
  }
  else if (char === '\x1b[B') { // Down arrow
    if (historyIndex.value > -1) {
      historyIndex.value--;
      updateTerminalInput(historyIndex.value === -1 ? '' : commandHistory.value[historyIndex.value]);
    }
  }
  else { // Regular characters
    terminal.value.write(char);
    currentInput.value += char;
  }
};

const handleCommand = (command) => {
  switch (command.trim()) {
    case 'clear':
      clearTerminal();
      break;
    case 'help':
      terminal.value.writeln('Available commands:');
      terminal.value.writeln('  clear - Clear terminal');
      terminal.value.writeln(`  python ${fileName.value} - Run Python code`);
      terminal.value.writeln('  help - Show this help message');
      break;
    case `python ${fileName.value}`:
      executePythonCode(editor.value.state.doc.toString());
      break;
    default:
      terminal.value.writeln(`Command not found: ${command}`);
      break;
  }
};

const updateTerminalInput = (newInput) => {
  // Clear current line
  while (currentInput.value.length > 0) {
    terminal.value.write('\b \b');
    currentInput.value = currentInput.value.slice(0, -1);
  }
  // Write new input
  currentInput.value = newInput;
  terminal.value.write(currentInput.value);
};

const clearTerminal = () => {
  terminal.value.clear();
  terminal.value.write('$ ');
  currentInput.value = '';
};



// Execute Python code on the backend
const executePythonCode = async (code) => {
  try {
    const response = await fetch('http://decode.local:8080/api/method/decode.api.execute', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    const data = await response.json();
    console.log("API Response:", data); // Debugging API Response

    // Print the output if available
    if (data.message && data.message.output) {
      data.message.output.split("\n").forEach(line => terminal.value.writeln(line));
    }

    // Print the error properly if available
    if (data.message && data.message.error) {
      terminal.value.writeln("Error:");
      data.message.error.split("\n").forEach(line => terminal.value.writeln(line));
    }

  } catch (error) {
    console.error("API Call Failed:", error);
    terminal.value.writeln(`Error executing Python code: ${error.message}`);
  }
};


onMounted(() => {
  const totalWidth = window.innerWidth;
  codeEditorWidth.value = Math.floor(totalWidth * 0.7);
  consoleWidth.value = totalWidth - codeEditorWidth.value - 8;

  // Initialize the terminal
  terminal.value = new Terminal({
    theme: {
      background: '#000000',
      foreground: '#00ff00',
      cursor: '#00ff00',
      cursorAccent: '#000000',
      selection: 'rgba(0, 255, 0, 0.3)',
    },
    fontSize: 14,
    fontFamily: 'monospace',
    cursorBlink: true,
    rows: 24,
    cols: 80,
    allowTransparency: true
  });


  fitAddon.value = new FitAddon();
  terminal.value.loadAddon(fitAddon.value);

  if (terminalContainer.value) {
    terminal.value.open(terminalContainer.value);
    fitAddon.value.fit();
    terminal.value.writeln('Terminal initialized...');
    terminal.value.writeln('$ ');
  }
  // Fetch file details when the component is mounted
  fetchFileDetails();
  initEditor ();
  connectSocket();
  startAutoRefresh();

  // Detect user activity
  window.addEventListener("mousemove", resetInactivityTimer);
  window.addEventListener("keydown", resetInactivityTimer);
  // Add terminal input event listener
  terminal.value.onData((data) => {
    handleTerminalInput(data);
  });
  // Handle window resizing
  const resizeObserver = new ResizeObserver(() => {
    if (terminal.value && fitAddon.value) {
      fitAddon.value.fit();
    }
  });

  if (terminalContainer.value) {
    resizeObserver.observe(terminalContainer.value);
  }

  window.addEventListener('resize', handleResize);

});

onUnmounted(() => {
  // First, disable and null any references to the resize observer
  if (typeof resizeObserver !== 'undefined' && resizeObserver) {
    resizeObserver.disconnect();
  }
  
  // Clear all timers and intervals first
  clearInterval(intervalId);
  clearTimeout(inactivityTimeout);
  
  // Remove event listeners
  window.removeEventListener('resize', handleResize);
  window.removeEventListener("mousemove", resetInactivityTimer);
  window.removeEventListener("keydown", resetInactivityTimer);
  
  // Nullify the fitAddon reference without trying to dispose it
  fitAddon.value = null;
  
  // Dispose the terminal - this should handle addon cleanup internally
  if (terminal.value) {
    // Create a local reference and null the reactive reference
    const term = terminal.value;
    terminal.value = null;
    
    // Now dispose the terminal with a small delay to ensure Vue has processed the nullification
    setTimeout(() => {
      try {
        term.dispose();
      } catch (error) {
        console.log("Terminal disposal error:", error);
      }
    }, 0);
  }
  
  // Clean up the editor
  if (editor.value) {
    editor.value.destroy();
    editor.value = null;
  }
  
  console.log("🛑 Cleanup complete, stopping auto-refresh.");
  cleanupSocket();
});
// Handle window resize
const handleResize = () => {
  if (fitAddon.value) {
    fitAddon.value.fit();
  }
};

// Handle resizing of the editor and console
const startResize = (e) => {
  e.preventDefault();
  const startX = e.clientX;
  const startEditorWidth = codeEditorWidth.value;
  const startConsoleWidth = consoleWidth.value;
  const totalWidth = startEditorWidth + startConsoleWidth + 8;

  const onMouseMove = (moveEvent) => {
    moveEvent.preventDefault();
    const dx = moveEvent.clientX - startX;

    let newEditorWidth = startEditorWidth + dx;
    let newConsoleWidth = startConsoleWidth - dx;

    if (newEditorWidth < MIN_EDITOR_WIDTH) {
      newEditorWidth = MIN_EDITOR_WIDTH;
      newConsoleWidth = totalWidth - MIN_EDITOR_WIDTH - 8;
    } else if (newConsoleWidth < MIN_CONSOLE_WIDTH) {
      newConsoleWidth = MIN_CONSOLE_WIDTH;
      newEditorWidth = totalWidth - MIN_CONSOLE_WIDTH - 8;
    }

    codeEditorWidth.value = newEditorWidth;
    consoleWidth.value = newConsoleWidth;

    if (fitAddon.value) {
      setTimeout(() => fitAddon.value.fit(), 0);
    }
  };

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);

};

// Save code function (PATCH request)
const saveCode = async () => {
  try {
    const code = editor.value.state.doc.toString();
    const uuid = route.params.uuid;

    // Encode parameters properly
    const encodedCode = encodeURIComponent(code);
    const encodedUuid = encodeURIComponent(uuid);

    const response = await fetch(
      `http://decode.local:8080/api/method/decode.api.update_code?file_uuid=${encodedUuid}&code=${encodedCode}`,
      {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      // If the response is not successful, print status and status text
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    console.log('Response Data:', data); // Log the response for debugging

    if (data.message.message.status === 'success') {
      alert('Code saved successfully!');
    } else {
      alert(`${data.message.status}`);
    }
  } catch (error) {
    console.error('Error saving code:', error);
    alert(`An error occurred while saving the code: ${error.message}`);
  }
};

const shareCode = () => {
  try {
    const uuid = route.params.uuid;
    const encodedUuid = encodeURIComponent(uuid);
    alert(`UUID: ${encodedUuid}`);
  } catch (error) {
    console.error("Error encoding UUID:", error);
  }
};

</script>
<style scoped>
/* Prevent text selection during resize */
.cursor-ew-resize {
  user-select: none;
}

/* Ensure smooth width transitions */
.bg-gray-900,
.bg-gray-800 {
  transition: width 0.05s ease-out;
}

/* Terminal styles */
:deep(.xterm) {
  padding: 8px;
  height: 100%;
}

:deep(.xterm-viewport) {
  overflow-y: auto !important;
}

/* Custom scrollbar */
:deep(.xterm-viewport::-webkit-scrollbar) {
  width: 8px;
}

:deep(.xterm-viewport::-webkit-scrollbar-track) {
  background: #1a1a1a;
}

:deep(.xterm-viewport::-webkit-scrollbar-thumb) {
  background: #333;
  border-radius: 4px;
}

:deep(.xterm-viewport::-webkit-scrollbar-thumb:hover) {
  background: #444;
}

.cm-editor {
  height: 100%;
}

.cm-scroller {
  overflow: auto;
}

.cm-editor .cm-content {
  font-family: monospace;
  font-size: 30%;
}
</style>


<!-- sudo sysctl net.ipv6.conf.all.disable_ipv6=1----solved the issue related to npm install monaco-editor -->
<!-- 01952532-a3b9-7290-b079-20743e573ed7 -->