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
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import { EditorView, basicSetup } from 'codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { EditorState } from "@codemirror/state";
import { getSocket } from "../socket";
const socket = getSocket();

// API URL
const API_URL = `http://${window.location.hostname}:8080/api/method/decode.api.update_code`;

const route = useRoute();
const codeMirrorContainer = ref(null);
const editor = ref(null);
const fileName = ref("");
const currentInput = ref('');
const codeContent = ref('');

// Terminal refs
const terminalContainer = ref(null);
const terminal = ref(null);
const fitAddon = ref(null);

const commandHistory = ref([]);
const historyIndex = ref(-1);

// Reactive state
const codeEditorWidth = ref(0);
const consoleWidth = ref(0);

const hasChanges = ref(false);
let pollingInterval = null;
let fetchTimeout = null;
let saveTimeout = null;
let lastSavedContent = "";
let periodicFetchInterval = null;
let lastEditTime = Date.now();
let isExternalUpdate = false;

// Start periodic fetch when component mounts
const startPeriodicFetch = () => {
  // Clear any existing interval first
  if (periodicFetchInterval) {
    clearInterval(periodicFetchInterval);
  }

  // Set up new interval to fetch every 5 seconds if no changes
  periodicFetchInterval = setInterval(() => {
    const timeSinceLastEdit = Date.now() - lastEditTime;

    // Only fetch if no edits in the last 3 seconds
    if (timeSinceLastEdit >= 3000) {
      fetchFileDetailsWithoutResetCursor();
    }
  }, 5000);
};

const getLanguageExtension = () => {
  if (fileName.value.endsWith(".py")) {
    return python();
  } else if (fileName.value.endsWith(".c")) {
    return cpp(); // C/C++ are handled by lang-cpp
  } else {
    return javascript(); // default fallback
  }
};
startPeriodicFetch();

// Modified fetch function that preserves cursor position
const fetchFileDetailsWithoutResetCursor = () => {
  // Make sure editor exists
  if (!editor.value) return;

  // Store current cursor position and selection before fetch
  const cursorPos = editor.value.state.selection.main.head;
  const selection = editor.value.state.selection;

  // Set the flag to indicate an external update is in progress
  isExternalUpdate = true;

  // Call your original fetch function
  fetchFileDetails().then(() => {
    // After fetch completes and editor is updated, restore cursor position
    setTimeout(() => {
      if (editor.value && editor.value.dispatch) {
        // Only restore if the cursor position is valid for the new content
        const newDocLength = editor.value.state.doc.length;
        const validPos = Math.min(cursorPos, newDocLength);

        // Create a new selection at the previous position
        const newSelection = editor.value.state.selection.constructor.create(
          [editor.value.state.selection.constructor.range(validPos, validPos)],
          0
        );

        // Dispatch the selection update
        editor.value.dispatch({
          selection: newSelection,
          scrollIntoView: true
        });
      }

      isExternalUpdate = false;
    }, 10);
  });
};


const initEditor = () => {
  const fileUuid = route.params.uuid;

  if (codeMirrorContainer.value && !editor.value) {
    // Initialize these variables when editor is created
    lastSavedContent = codeContent.value;

    editor.value = new EditorView({
      state: EditorState.create({
        doc: codeContent.value,
        extensions: [
          basicSetup,
          oneDark,
          getLanguageExtension(),
          EditorView.updateListener.of((update) => {
            // Skip processing if this update is from our external update handler
            if (isExternalUpdate) return;

            if (update.docChanged) {
              const newCode = update.state.doc.toString();
              codeContent.value = newCode;

              // Update last edit time
              lastEditTime = Date.now();

              // Clear any pending fetch operation when content changes
              if (fetchTimeout) {
                clearTimeout(fetchTimeout);
              }

              // Don't save if content hasn't changed from last save
              if (newCode === lastSavedContent) {
                return;
              }

              // Debounced save (wait 500ms before saving)
              if (saveTimeout) {
                clearTimeout(saveTimeout);
              }

              saveTimeout = setTimeout(() => {
                // Save to backend
                fetch(`${API_URL}?file_uuid=${encodeURIComponent(fileUuid)}&code=${encodeURIComponent(newCode)}`, {
                  method: "PUT",
                  credentials: 'include',
                  headers: { 'Content-Type': 'application/json' }
                })
                  .then(res => res.json())
                  .then(data => {
                    console.log("Save response:", data);
                    lastSavedContent = newCode; // Update last saved content
                  })
                  .catch(err => console.error("Save error:", err));
              }, 500);

              // Set up fetch timer - only call modified fetch after 3 seconds of inactivity
              fetchTimeout = setTimeout(() => {
                fetchFileDetailsWithoutResetCursor(); // Use the cursor-preserving version
              }, 3000);
            }
          })
        ],
      }),
      parent: codeMirrorContainer.value,
    });

    // Start periodic fetch
    startPeriodicFetch();

    // Join socket room for this file
    socket.emit("join", { room: fileUuid });
  }
};


const fetchFileDetails = async () => {
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
    console.log("File details:", data);

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
      alert(data.message.message);
    }
  } catch (error) {
    console.error("Error fetching file details:", error);
    if (terminal.value) {
      terminal.value.writeln('Error loading file data...');
    }
  }
};

// Handle terminal input
// State variables for interactive mode
const isExecutingPython = ref(false);
const waitingForInput = ref(false);
const inputPromptQueue = ref([]);
const inputResponses = ref([]);
const currentInputPrompt = ref('');

const handleTerminalInput = (data) => {
  const char = data;

  // Handle input differently when in Python execution mode
  if (isExecutingPython.value && waitingForInput.value) {
    if (char === '\x7F' || char === '\b') { // Backspace
      if (currentInput.value.length > 0) {
        currentInput.value = currentInput.value.slice(0, -1);
        terminal.value.write('\b \b');
      }
    }
    else if (char === '\r') { // Enter
      terminal.value.writeln('');
      // Store the input response
      inputResponses.value.push(currentInput.value);

      // Process the next input prompt if any
      processNextInputPrompt();
    }
    else if (char === '\x03') { // Ctrl + C
      if (isExecutingPython.value) {
        terminal.value.writeln('^C');
        isExecutingPython.value = false;
        waitingForInput.value = false;
        currentInput.value = '';
        inputPromptQueue.value = [];
        inputResponses.value = [];
        terminal.value.write('$ ');
      }
      return;
    }
    else { // Regular characters
      terminal.value.write(char);
      currentInput.value += char;
    }
    return;
  }

  // Normal terminal command mode
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
    if (!isExecutingPython.value) {
      terminal.value.write('$ ');
    }
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
      terminal.value.writeln(' clear - Clear terminal');
      terminal.value.writeln(` python ${fileName.value} - Run Python code`);
      terminal.value.writeln(' help - Show this help message');
      break;
    case `python ${fileName.value}`:
      const code = editor.value.state.doc.toString();
      startPythonExecution(code);
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

// Function to parse Python code and extract input prompts
const parseInputPrompts = (code) => {
  const regex = /input\((["']?)(.*?)\1?\)/g;
  const prompts = [];
  let match;

  while ((match = regex.exec(code)) !== null) {
    prompts.push(match[2] || ''); // Default to empty string if no prompt
  }

  return prompts;
};


// Start Python execution with interactive input handling
const startPythonExecution = (code) => {
  isExecutingPython.value = true;
  waitingForInput.value = false;
  inputResponses.value = [];
  terminal.value.writeln('Executing Python script...');

  // Parse code for input prompts
  inputPromptQueue.value = parseInputPrompts(code);

  if (inputPromptQueue.value.length > 0) {
    // Start processing input prompts
    processNextInputPrompt();
  } else {
    // No input needed, execute directly
    executePythonCode(code, []);
  }
};

// Process the next input prompt
const processNextInputPrompt = () => {
  if (inputPromptQueue.value.length > 0) {
    currentInputPrompt.value = inputPromptQueue.value.shift();
    terminal.value.write(currentInputPrompt.value);
    currentInput.value = '';
    waitingForInput.value = true;
  } else {
    // All inputs collected, replace input() with user responses
    let code = editor.value.state.doc.toString();

    inputResponses.value.forEach((input, index) => {
      code = code.replace(/input\((["']?)(.*?)\1?\)/, `"${input}"`);
    });

    executePythonCode(code);
  }
};

const executePythonCode = async (code, inputs = []) => {
  try {
    const response = await fetch('http://decode.local:8080/api/method/decode.api.execute', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, inputs }),
    });

    const data = await response.json();

    if (data.message) {
      if (data.message.output) {
        data.message.output.split("\n").forEach(line => terminal.value.writeln(line));
      }
      if (data.message.error) {
        terminal.value.writeln("Error:");
        data.message.error.split("\n").forEach(line => terminal.value.writeln(line));
      }
    } else {
      terminal.value.writeln("No output received.");
    }
  } catch (error) {
    console.error("API Call Failed:", error);
    terminal.value.writeln(`Error executing Python code: ${error.message}`);
  } finally {
    // Reset states
    isExecutingPython.value = false;
    waitingForInput.value = false;
    currentInput.value = '';
    inputPromptQueue.value = [];
    inputResponses.value = [];

    // Show prompt
    terminal.value.write('$ ');
  }
};


onMounted(() => {
  const totalWidth = window.innerWidth;
  codeEditorWidth.value = Math.floor(totalWidth * 0.7);
  consoleWidth.value = totalWidth - codeEditorWidth.value - 8;

  // 🖥️ Terminal setup
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
    terminal.value.write('$ ');
  }
  startPeriodicFetch();
  fetchFileDetails(); // 🔄 Load file contents
  initEditor();       // 🧠 Set up the code editor

  // ⌨️ Handle terminal input
  terminal.value.onData((data) => {
    handleTerminalInput(data);
  });

  // 📐 Resize terminal with container
  const resizeObserver = new ResizeObserver(() => {
    if (terminal.value && fitAddon.value) {
      fitAddon.value.fit();
    }
  });

  if (terminalContainer.value) {
    resizeObserver.observe(terminalContainer.value);
  }

  // 🔄 Adjust layout on browser resize
  window.addEventListener('resize', handleResize);

  // 🔥 Real-time code sync
  socket.on("code_update", ({ uuid, code }) => {
    if (uuid === route.params.uuid && code !== codeContent.value) {
      codeContent.value = code;

      // 🧠 Replace entire editor content
      editor.value?.dispatch({
        changes: {
          from: 0,
          to: editor.value.state.doc.length,
          insert: code,
        }
      });
    }
  });
  // Start polling for file details
  pollingInterval = setInterval(() => {
    if (hasChanges.value) {
      fetchFileDetails();
      hasChanges.value = false; // Reset after fetching
    }
  }, 3000); // Every 3 seconds
});

onBeforeUnmount(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
  socket.off("code_update");
  window.removeEventListener('resize', handleResize);
  if (saveTimeout) clearTimeout(saveTimeout);
  if (fetchTimeout) clearTimeout(fetchTimeout);
  if (periodicFetchInterval) clearInterval(periodicFetchInterval);
});


const handleResize = () => {
  if (fitAddon.value) {
    fitAddon.value.fit();
  }
};

const saveCode = async () => {
  try {
    const code = editor.value.state.doc.toString();
    const uuid = route.params.uuid;
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
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
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