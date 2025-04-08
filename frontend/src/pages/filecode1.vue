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
      <span v-if="corrected === 1" class=" absolute text-lg text-black right-[7%]">Corrected</span>
      <!-- Action Buttons Section -->
      <button @click="submitCode"
  class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">
  {{ isSubmitted ? "Unsubmit" : "Submit" }}
</button>

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

const fileId = ref(route.params.uuid);
console.log("fileId:", fileId.value);

const isSubmitted = ref(false);
const submitCode = async () => {
  const newStatus = isSubmitted.value ? 0 : 1; // Toggle submission status
  
  try {
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.toggleSubmit`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_id: fileId.value, submitt: newStatus }),
    });
    
    const data = await response.json();
    
    // Check for error response
    if (data.message && data.message.error === "Already corrected") {
      alert("This submission is already corrected and cannot be changed");
      // Don't change button state if already corrected
      return;
    }
    
    // Check for success response
    if (data.message && data.message.message === "Submission status updated") {
      // Update button state based on the actual submitt value returned from server
      isSubmitted.value = data.message.submitt === 1;
    } else if (data.error) {
      alert(data.error);
      // Don't change button state if there was an error
    } else {
      alert("Something went wrong");
      // Don't change button state if response format is unexpected
    }
  } catch (error) {
    console.error("Error updating submit status:", error);
    alert("Failed to update submission status");
    // Don't change button state if there was an exception
  }
};


const corrected = ref(0); // Store the corrected value
const fetchFileDetails = async () => {
  try {
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.getFileName?search_fileid=${fileId.value}`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    console.log("File Details:", data);

    if (data.message && data.message.filename) {
      fileName.value = data.message.filename;
      corrected.value = Number(data.message.corrected) || 0; // Convert corrected to a number
      isSubmitted.value = Number(data.message.submitted) || 0; // Convert submitted to a number

      if (editor.value) {
        editor.value.dispatch({
          changes: {
            from: 0,
            to: editor.value.state.doc.length,
            insert: data.message.code || ''
          }
        });
      }
    } else {
      alert(data.error || "Unexpected error occurred.");
    }
  } catch (error) {
    console.error("Error fetching file details:", error);
    if (terminal.value) {
      terminal.value.writeln('Error loading file data...');
    }
  }
};


const saveFileCode = async () => {
  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.saveFileCode", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_id: fileId.value,
        code: editor.value ? editor.value.state.doc.toString() : "",
      }),
    });

    const data = await response.json();
    console.log("Save Response:", data);

    if (data.message) {
      console.log("Code saved successfully!");
    } else {
      console.log(data.error || "Unexpected error occurred.");
    }
  } catch (error) {
    console.error("Error saving code:", error);
    if (terminal.value) {
      terminal.value.writeln("Error saving file data...");
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
const shownPrompts = ref([]); 

const handleTerminalInput = (data) => {
  const char = data;

  // Input mode for Python or C (interactive input phase)
  if (isExecutingPython.value && waitingForInput.value) {
    if (char === '\x7F' || char === '\b') { // Backspace
      if (currentInput.value.length > 0) {
        currentInput.value = currentInput.value.slice(0, -1);
        terminal.value.write('\b \b');
      }
    } else if (char === '\r') { // Enter
      terminal.value.writeln('');
      
      // Store the user input
      inputResponses.value.push(currentInput.value);
      currentInput.value = '';
      waitingForInput.value = false;

      // Continue execution (for both C and Python)
      if (fileName.value.endsWith('.c')) {
        processNextExecutionStep(editor.value.state.doc.toString());
      } else {
        processNextInputPrompt(); // For Python or other
      }
    } else if (char === '\x03') { // Ctrl + C
      terminal.value.writeln('^C');
      isExecutingPython.value = false;
      waitingForInput.value = false;
      currentInput.value = '';
      inputPromptQueue.value = [];
      inputResponses.value = [];
      terminal.value.write('$ ');
    } else {
      terminal.value.write(char);
      currentInput.value += char;
    }
    return; // Exit early when in execution mode
  }

  // Normal terminal command mode
  if (char === '\x7F' || char === '\b') { // Backspace
    if (currentInput.value.length > 0) {
      currentInput.value = currentInput.value.slice(0, -1);
      terminal.value.write('\b \b');
    }
  } else if (char === '\r') { // Enter key in normal mode
    terminal.value.writeln('');
    if (currentInput.value.trim() !== '') {
      commandHistory.value.unshift(currentInput.value.trim());
      historyIndex.value = -1;
    }
    handleCommand(currentInput.value); // Run normal shell command
    currentInput.value = '';
    if (!isExecutingPython.value) {
      terminal.value.write('$ ');
    }
  } else if (char === '\x1b[A') { // Arrow Up
    if (historyIndex.value < commandHistory.value.length - 1) {
      historyIndex.value++;
      updateTerminalInput(commandHistory.value[historyIndex.value]);
    }
  } else if (char === '\x1b[B') { // Arrow Down
    if (historyIndex.value > -1) {
      historyIndex.value--;
      updateTerminalInput(historyIndex.value === -1 ? '' : commandHistory.value[historyIndex.value]);
    }
  } else { // Regular character
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
      terminal.value.writeln(` run ${fileName.value} - Run current code`);
      terminal.value.writeln(' help - Show this help message');
      break;
    case `python ${fileName.value}`:
      const code = editor.value.state.doc.toString();
      startPythonExecution(code);
      break;
    case `run ${fileName.value}`: {
      const code = editor.value.state.doc.toString();
      if (fileName.value.endsWith('.c')) {
        startCExecution(code);
      } else {
        startPythonExecution(code);
      }
      break;
    }

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

// const parseScanfPrompts = (code) => {
//   const regex = /printf\s*\((["'])(.*?)\1\);?\s*scanf\s*\(/g;
//   const prompts = [];
//   let match;

//   while ((match = regex.exec(code)) !== null) {
//     prompts.push(match[2]); // Just the prompt before scanf
//   }

//   return prompts;
// };


// Start Python execution with interactive input handling
const startPythonExecution = (code) => {
  isExecutingPython.value = true;
  waitingForInput.value = false;
  inputResponses.value = [];
  terminal.value.writeln('Executing Python script...');

  inputPromptQueue.value = parseInputPrompts(code);

  if (inputPromptQueue.value.length > 0) {
    processNextInputPrompt();
  } else {
    executePythonCode(code, []);
  }
};



const startCExecution = (code) => {
  isExecutingPython.value = true;
  waitingForInput.value = false;
  inputResponses.value = [];
  shownPrompts.value = []; // Reset prompt tracking
  terminal.value.writeln('Executing C program...');

  // Get all printf/scanf steps in order
  const steps = parseOrderedExecutionSteps(code);

  executionQueue.value = steps; // Store to process step by step

  processNextExecutionStep(code);
};


const executionQueue = ref([]);

const processNextExecutionStep = (code) => {
  if (executionQueue.value.length === 0) {
    // Done with all steps
    if (fileName.value.endsWith('.c')) {
      executeCCode(code, inputResponses.value);
    } else {
      executePythonCode(code, inputResponses.value);
    }
    return;
  }

  const step = executionQueue.value.shift();
  shownPrompts.value.push(step.prompt); // So we filter later

  terminal.value.write(step.prompt);

  if (step.isInput) {
    waitingForInput.value = true;
    currentInputPrompt.value = step.prompt;
    currentInput.value = '';
  } else {
    processNextExecutionStep(code); // Go to next step immediately
  }
};



const parseOrderedExecutionSteps = (code) => {
  const lines = [];
  const printfScanfRegex = /printf\s*\((["'])(.*?)\1\);(\s*scanf\s*\(.*?\);)?/g;

  let match;
  while ((match = printfScanfRegex.exec(code)) !== null) {
    const prompt = match[2];
    const hasScanf = match[3]?.includes('scanf');
    lines.push({
      prompt,
      isInput: !!hasScanf
    });
  }

  return lines;
};


// Process the next input prompt
const processNextInputPrompt = () => {
  if (inputPromptQueue.value.length > 0) {
    currentInputPrompt.value = inputPromptQueue.value.shift();
    
    // ✅ Store prompt so we can filter repeated printf output later
    shownPrompts.value.push(currentInputPrompt.value);

    terminal.value.write(currentInputPrompt.value);
    currentInput.value = '';
    waitingForInput.value = true;
  } else {
    const code = editor.value.state.doc.toString();

    if (fileName.value.endsWith('.c')) {
      executeCCode(code, inputResponses.value); // Pass inputs to C executor
    } else {
      executePythonCode(code, inputResponses.value); // Or Python executor
    }
  }
};

const executeCCode = async (code, inputs = []) => {
  try {
    const response = await fetch('http://decode.local:8080/api/method/decode.api.execute_c', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        user_input: inputs.join(' ')  // Join inputs for scanf
      }),
    });

    const data = await response.json();

    if (data.message) {
      console.log("C Execution Response:", data);

      if (data.message.output) {
        // 🧼 Filter out prompts that were already printed
        let output = data.message.output;

        shownPrompts.value.forEach(prompt => {
          output = output.replace(prompt, '');
        });

        // Write filtered output to terminal
        output.split("\n").forEach(line => {
          if (line.trim() !== '') {
            terminal.value.writeln(line);
          }
        });
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
    terminal.value.writeln(`Error executing C code: ${error.message}`);
  } finally {
    isExecutingPython.value = false;
    waitingForInput.value = false;
    currentInput.value = '';
    inputPromptQueue.value = [];
    inputResponses.value = [];
    shownPrompts.value = []; // 🧼 Clear prompt tracking

    terminal.value.write('$ ');
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

  if (terminal.value) {
    terminal.value.loadAddon(fitAddon.value);  // 🔹 Ensure addon is loaded
  }

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
          saveFileCode(); // Call save function on change
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

onUnmounted(() => {
  try {
    // Dispose of the terminal
    if (terminal.value) {
      terminal.value.dispose();
      terminal.value = null;
    }

    // Destroy the CodeMirror editor
    if (editor.value) {
      editor.value.destroy();
      editor.value = null;
    }

    // Remove resize event listener
    window.removeEventListener("resize", handleResize);
  } catch (error) {
    console.error("Error during component unmount:", error);
  }
});

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