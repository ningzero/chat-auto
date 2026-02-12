<template>
  <div class="command-input-container">
    <input
      v-model="inputValue"
      type="text"
      placeholder="Type a message or /command..."
      class="command-input"
      @keydown.enter="handleSend"
      @keydown.up="handleUpArrow"
      @keydown.down="handleDownArrow"
    />
    <button class="send-button" @click="handleSend">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>

    <div v-if="showSuggestions" class="command-suggestions">
      <div
        v-for="(suggestion, index) in filteredSuggestions"
        :key="suggestion"
        :class="['suggestion-item', { active: index === selectedIndex }]"
        @click="selectSuggestion(suggestion)"
      >
        <span class="suggestion-command">{{ suggestion }}</span>
        <span class="suggestion-desc">{{ getCommandDescription(suggestion) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits<{
  send: [value: string]
}>()

const inputValue = ref('')
const commandHistory = ref<string[]>([])
const historyIndex = ref(-1)

const showSuggestions = ref(false)
const selectedIndex = ref(0)

const availableCommands = [
  { name: '/list', description: 'List all available scripts' },
  { name: '/hello', description: 'Run hello script' },
  { name: '/sysinfo', description: 'Show system information' },
  { name: '/date', description: 'Show current date and time' },
  { name: '/status', description: 'Check task status: /status <task_id>' },
]

const filteredSuggestions = computed(() => {
  if (!inputValue.value.startsWith('/')) return []
  const prefix = inputValue.value.toLowerCase()
  return availableCommands
    .filter(c => c.name.toLowerCase().startsWith(prefix))
    .map(c => c.name)
})

function getCommandDescription(command: string) {
  return availableCommands.find(c => c.name === command)?.description || ''
}

function handleSend() {
  const value = inputValue.value.trim()
  if (!value) return

  emit('send', value)

  // Add to history
  if (!commandHistory.value.includes(value)) {
    commandHistory.value.unshift(value)
  }
  historyIndex.value = -1

  inputValue.value = ''
  showSuggestions.value = false
}

function handleUpArrow() {
  if (commandHistory.value.length === 0) return

  if (historyIndex.value < commandHistory.value.length - 1) {
    historyIndex.value++
    inputValue.value = commandHistory.value[historyIndex.value]
  }
}

function handleDownArrow() {
  if (historyIndex.value > 0) {
    historyIndex.value--
    inputValue.value = commandHistory.value[historyIndex.value]
  } else if (historyIndex.value === 0) {
    historyIndex.value = -1
    inputValue.value = ''
  }
}

function selectSuggestion(command: string) {
  inputValue.value = command
  showSuggestions.value = false
}

// Keyboard navigation for suggestions
function handleKeyNavigation(e: KeyboardEvent) {
  if (e.key === 'Tab' && showSuggestions.value) {
    e.preventDefault()
    if (filteredSuggestions.value[selectedIndex.value]) {
      inputValue.value = filteredSuggestions.value[selectedIndex.value]
    }
    showSuggestions.value = false
  }
}
</script>

<style scoped>
.command-input-container {
  position: relative;
  display: flex;
  gap: 8px;
  padding: 16px;
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border);
}

.command-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.command-input:focus {
  outline: none;
  border-color: var(--accent);
}

.command-input::placeholder {
  color: var(--text-secondary);
}

.send-button {
  padding: 0 16px;
  background-color: var(--accent);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.send-button:hover {
  background-color: var(--accent-hover);
}

.send-button:active {
  transform: scale(0.95);
}

.command-suggestions {
  position: absolute;
  bottom: 100%;
  left: 16px;
  right: 16px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 8px;
  z-index: 10;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background-color 0.1s;
}

.suggestion-item:hover,
.suggestion-item.active {
  background-color: var(--bg-primary);
}

.suggestion-command {
  font-family: 'Monaco', 'Menlo', monospace;
  color: var(--success);
}

.suggestion-desc {
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
