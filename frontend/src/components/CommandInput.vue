<template>
  <div class="command-input-container">
    <!-- 命令下拉按钮 -->
    <button class="command-dropdown-btn" @click.stop="toggleDropdown" :class="{ active: showDropdown }">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <!-- 命令下拉列表 -->
    <div v-if="showDropdown" class="command-dropdown" ref="dropdownRef">
      <div
        v-for="cmd in availableCommands"
        :key="cmd.name"
        class="dropdown-item"
        @click="selectCommand(cmd.name)"
      >
        <span class="dropdown-command">{{ cmd.name }}</span>
        <span class="dropdown-desc">{{ cmd.description }}</span>
      </div>
    </div>

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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getCommands, type Command } from '@/api/messages'

const emit = defineEmits<{
  send: [value: string]
}>()

const inputValue = ref('')
const commandHistory = ref<string[]>([])
const historyIndex = ref(-1)

const showSuggestions = ref(false)
const selectedIndex = ref(0)

const showDropdown = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const availableCommands = ref<Command[]>([])
const commandsLoading = ref(false)

const filteredSuggestions = computed(() => {
  if (!inputValue.value.startsWith('/')) return []
  const prefix = inputValue.value.toLowerCase()
  return availableCommands.value
    .filter(c => c.name.toLowerCase().startsWith(prefix))
    .map(c => c.name)
})

function getCommandDescription(command: string) {
  return availableCommands.value.find(c => c.name === command)?.description || ''
}

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    showSuggestions.value = false
    if (availableCommands.value.length === 0 && !commandsLoading.value) {
      loadCommands()
    }
  }
}

function selectCommand(command: string) {
  inputValue.value = command
  showDropdown.value = false
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showDropdown.value = false
  }
}

async function loadCommands() {
  commandsLoading.value = true
  try {
    availableCommands.value = await getCommands()
  } catch (error) {
    console.error('Failed to load commands:', error)
  } finally {
    commandsLoading.value = false
  }
}

onMounted(async () => {
  await loadCommands()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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

.command-dropdown-btn {
  padding: 0 12px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.command-dropdown-btn:hover,
.command-dropdown-btn.active {
  background-color: var(--bg-primary);
  border-color: var(--accent);
}

.command-dropdown {
  position: absolute;
  bottom: 100%;
  left: 16px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 8px;
  z-index: 20;
  min-width: 200px;
}

.dropdown-item {
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.1s;
  gap: 4px;
}

.dropdown-item:hover {
  background-color: var(--bg-primary);
}

.dropdown-command {
  font-family: 'Monaco', 'Menlo', monospace;
  color: var(--success);
  font-size: 14px;
}

.dropdown-desc {
  color: var(--text-secondary);
  font-size: 12px;
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
