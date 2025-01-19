<template>
  <div id="app" class="font-sans h-screen w-screen bg-gradient-to-br from-black to-gray-800 text-white flex flex-col">
    <!-- Header -->
    <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%]"
      :style="{ fontFamily: 'Inter, sans-serif' }">
      <!-- Logo and User ID Section -->
      <div class="flex items-center gap-4">
        <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
          :style="{ maxHeight: '80%', width: '15%', height: 'auto' }" />
        <span class="text-lg text-black">File name</span>
      </div>
      <!-- Action Buttons Section -->
      <div class="flex items-center gap-4">
        <button class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">Save</button>
        <button class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">Share</button>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- Code Editor -->
      <div class="bg-gray-900 p-4 flex-shrink-0 h-full overflow-y-auto" :style="{ width: `${codeEditorWidth}px` }">
        <textarea v-model="codeContent" placeholder="Write your code here..."
          class="w-full h-full bg-transparent text-white text-lg outline-none resize-none font-mono p-4"
          @input="updateCode"></textarea>
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
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

// Constants for minimum widths
const MIN_EDITOR_WIDTH = 400;
const MIN_CONSOLE_WIDTH = 300;

// Terminal refs
const terminalContainer = ref(null);
const terminal = ref(null);
const fitAddon = ref(null);

// Reactive state
const codeContent = ref('');
const consoleOutput = ref('No output yet...');
const codeEditorWidth = ref(0);
const consoleWidth = ref(0);

// Calculate initial widths and setup terminal
onMounted(() => {
  const totalWidth = window.innerWidth;
  // Set initial widths - 70% for editor, 30% for console
  codeEditorWidth.value = Math.floor(totalWidth * 0.7);
  consoleWidth.value = totalWidth - codeEditorWidth.value - 8; // 8px for resize handle

  // Initialize terminal
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

  // Initialize fit addon
  fitAddon.value = new FitAddon();
  terminal.value.loadAddon(fitAddon.value);

  // Mount terminal
  if (terminalContainer.value) {
    terminal.value.open(terminalContainer.value);
    fitAddon.value.fit();

    // Welcome message
    terminal.value.writeln('Terminal initialized...');
    terminal.value.writeln('$ ');

    // Handle terminal input
    let currentLine = '';
    terminal.value.onData(data => {
      switch (data) {
        case '\r': // Enter
          terminal.value.writeln('');
          if (currentLine.trim().length > 0) {
            handleCommand(currentLine.trim());
          }
          currentLine = '';
          terminal.value.write('$ ');
          break;
        case '\u007F': // Backspace
          if (currentLine.length > 0) {
            currentLine = currentLine.slice(0, -1);
            terminal.value.write('\b \b');
          }
          break;
        default:
          currentLine += data;
          terminal.value.write(data);
      }
    });
  }

  // Handle terminal resize
  const resizeObserver = new ResizeObserver(() => {
    if (terminal.value && fitAddon.value) {
      fitAddon.value.fit();
    }
  });

  if (terminalContainer.value) {
    resizeObserver.observe(terminalContainer.value);
  }

  // Handle window resize
  window.addEventListener('resize', handleResize);
});

// Cleanup
onUnmounted(() => {
  if (terminal.value) {
    terminal.value.dispose();
  }
  window.removeEventListener('resize', handleResize);
});

// Handle window resize
const handleResize = () => {
  if (fitAddon.value) {
    fitAddon.value.fit();
  }
};

// Handle terminal commands
const handleCommand = (command) => {
  switch (command.toLowerCase()) {
    case 'clear':
      terminal.value.clear();
      break;
    case 'help':
      terminal.value.writeln('Available commands:');
      terminal.value.writeln('- clear: Clear the terminal');
      terminal.value.writeln('- help: Show this help message');
      terminal.value.writeln('- run: Run the code in editor');
      break;
    case 'run':
      terminal.value.writeln('Running code...');
      terminal.value.writeln(codeContent.value);
      break;
    default:
      terminal.value.writeln(`Command not found: ${command}`);
  }
};

// Resize handling
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

    // Fit terminal after resize
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

// Function to update the code content
const updateCode = () => {
  // You can add more functionality here
  // if (terminal.value) {
  //   terminal.value.writeln('Code updated...');
  // }
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
</style>
