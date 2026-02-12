<template>
  <div class="chat-page">
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <header class="chat-header">
      <div class="header-content">
        <button class="menu-toggle" @click="toggleSidebar" aria-label="Toggle menu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <div class="logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>ChatAuto</span>
        </div>
        <div class="connection-status" :class="store.connected ? 'connected' : 'disconnected'">
          <div class="status-dot" />
          {{ store.connected ? 'Connected' : 'Disconnected' }}
        </div>
      </div>
    </header>

    <div class="chat-body">
      <div :class="['sidebar', { open: sidebarOpen }]">
        <div class="section-title">Quick Commands</div>
        <div class="command-list">
          <button
            v-for="cmd in quickCommands"
            :key="cmd.command"
            class="command-btn"
            @click="executeQuickCommand(cmd.command)"
          >
            <span class="cmd-icon">{{ cmd.icon }}</span>
            <span class="cmd-text">{{ cmd.name }}</span>
            <span class="cmd-shortcut">{{ cmd.command }}</span>
          </button>
        </div>

        <div class="section-title">Help</div>
        <div class="help-text">
          Type <code>/list</code> to see available scripts.
          <br><br>
          Commands start with <code>/</code>.
        </div>
      </div>

      <div class="chat-area">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="store.loadingHistory" class="loading-state">
            <div class="spinner"></div>
            <p>Loading chat history...</p>
          </div>

          <div v-else-if="store.allMessages.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p>Start chatting or use commands</p>
            <p class="hint">Try <code>/list</code> to get started</p>
          </div>

          <template v-for="item in store.allMessages.filter(i => i && i.type)" :key="item._index || item.id || Date.now()">
            <ChatMessageItem
              v-if="item.type === 'message' && item.content"
              :content="item.content"
              :author="item.author"
              :created-at="item.created_at"
              :is-command="!!item.is_command"
              :is-own="item.author_id === store.currentUser?.id"
            />

            <CommandResultItem
              v-else-if="item.type === 'command' && item.data"
              :data="item.data"
            />
          </template>
        </div>

        <CommandInput @send="handleSend" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessageItem from '@/components/ChatMessageItem.vue'
import CommandResultItem from '@/components/CommandResultItem.vue'
import CommandInput from '@/components/CommandInput.vue'

const store = useChatStore()
const messagesContainer = ref<HTMLElement | null>(null)
const sidebarOpen = ref(false)

const quickCommands = [
  { name: 'List Scripts', command: '/list', icon: '📋' },
  { name: 'Hello', command: '/hello', icon: '👋' },
  { name: 'System Info', command: '/sysinfo', icon: '💻' },
  { name: 'Date & Time', command: '/date', icon: '🕐' },
]

onMounted(() => {
  store.connect()
  store.currentUser = { id: 1, username: 'user' }
})

onUnmounted(() => {
  store.disconnect()
})

async function handleSend(content: string) {
  if (content.startsWith('/')) {
    store.executeCommand(content)
  } else {
    store.sendMessage(content)
  }

  await nextTick()
  scrollToBottom()
}

function executeQuickCommand(command: string) {
  handleSend(command)
  sidebarOpen.value = false
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.chat-header {
  padding: 16px 24px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: 8px;
  margin-right: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.menu-toggle:hover {
  background-color: var(--bg-tertiary);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 18px;
  color: var(--text-primary);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 20px;
  background-color: var(--bg-tertiary);
}

.connection-status.connected {
  color: var(--success);
}

.connection-status.disconnected {
  color: var(--error);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}

.chat-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  padding: 20px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border);
  overflow-y: auto;
}

.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  margin-top: 24px;
}

.section-title:first-child {
  margin-top: 0;
}

.command-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.command-btn {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.command-btn:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--border);
}

.cmd-icon {
  font-size: 16px;
}

.cmd-text {
  font-size: 14px;
}

.cmd-shortcut {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.help-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.help-text code {
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  color: var(--accent);
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  gap: 12px;
}

.empty-state svg {
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
}

.empty-state .hint {
  font-size: 13px;
}

.empty-state code {
  background-color: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--accent);
  font-family: 'Monaco', 'Menlo', monospace;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--bg-tertiary);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .logo {
    font-size: 16px;
  }

  .logo svg {
    width: 24px;
    height: 24px;
  }

  .connection-status {
    font-size: 11px;
    padding: 4px 8px;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: -280px;
    width: 280px;
    height: 100vh;
    z-index: 101;
    transition: left 0.3s ease;
    border-right: none;
  }

  .sidebar.open {
    left: 0;
  }

  .messages-container {
    padding: 16px 12px;
  }

  .empty-state svg {
    width: 40px;
    height: 40px;
  }

  .empty-state p {
    font-size: 13px;
  }

  .command-btn {
    padding: 12px 14px;
  }

  .cmd-text {
    font-size: 15px;
  }

  .cmd-shortcut {
    font-size: 11px;
  }
}
</style>
