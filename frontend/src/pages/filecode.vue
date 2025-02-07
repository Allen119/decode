<template>
  <div id="app" class="font-sans h-screen w-screen bg-gradient-to-br from-black to-gray-800 text-white flex flex-col">
    <!-- Header -->
    <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%]"
      :style="{ fontFamily: 'Inter, sans-serif' }">
      <!-- Logo and User ID Section -->
      <div class="flex items-center gap-4">
        <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
          :style="{ maxHeight: '80%', width: '15%', height: 'auto' }" />
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
import { keymap } from '@codemirror/view';
import { indentWithTab } from '@codemirror/commands';


const route = useRoute();
const codeMirrorContainer = ref(null);
const editor = ref(null);
const fileName = ref(""); // Store filename
const currentInput = ref('');

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
const codeContent = ref('');
const codeEditorWidth = ref(0);
const consoleWidth = ref(0);

// Fetch file details from the backend
const fetchFileDetails = async () => {
  try {
    const uuid = route.params.uuid;
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.getfiles?search_uuid=${uuid}`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
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
    }
  } catch (error) {
    console.error("Error fetching file details:", error);
    if (terminal.value) {
      terminal.value.writeln('Error loading file data...');
    }
  }
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

  // Initialize the CodeMirror editor
  editor.value = new EditorView({
    doc: codeContent.value,
    extensions: [
      basicSetup,
      javascript(),
      oneDark,
      EditorView.updateListener.of(update => {
        if (update.docChanged) {
          codeContent.value = update.state.doc.toString();
        }
      }),
      EditorView.theme({
        '&': { height: '100%' },
        '.cm-scroller': { overflow: 'auto' },
        '&.cm-focused': { outline: 'none' }
      }),
    ],
    parent: codeMirrorContainer.value
  });

  // Fetch file details when the component is mounted
  fetchFileDetails();

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
  if (terminal.value) {
    terminal.value.dispose();
  }
  if (editor.value) {
    editor.value.destroy();
  }
  window.removeEventListener('resize', handleResize);
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
      `http://decode.local:8080/api/method/decode.api.updatecode?file_uuid=${encodedUuid}&code=${encodedCode}`,
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

    if (data.message.status === 'success') {
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



