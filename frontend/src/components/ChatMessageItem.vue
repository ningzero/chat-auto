<template>
  <div :class="['message-item', isOwn ? 'own' : 'other']">
    <div class="message-avatar">{{ initial }}</div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">{{ displayName }}</span>
        <span class="message-time">{{ formatTime }}</span>
      </div>
      <div :class="['message-body', isCommand ? 'command' : '']">
        {{ content }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  content: string
  author?: { username: string; nickname?: string }
  created_at?: string
  isCommand?: boolean
  isOwn?: boolean
}>()

const displayName = computed(() => {
  return props.author?.nickname || props.author?.username || 'Unknown'
})

const initial = computed(() => {
  return displayName.value.charAt(0).toUpperCase()
})

const formatTime = computed(() => {
  if (!props.created_at) return ''
  const date = new Date(props.created_at)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})
</script>

<style scoped>
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.own {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.message-item.own .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.message-content {
  max-width: 70%;
}

.message-header {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.message-item.own .message-header {
  flex-direction: row-reverse;
}

.message-body {
  background-color: var(--bg-tertiary);
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.5;
  word-break: break-word;
}

.message-item.own .message-body {
  background-color: var(--accent);
  color: white;
}

.message-body.command {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  background-color: #2d3748;
  border-left: 3px solid var(--success);
}

.message-item.own .message-body.command {
  background-color: #1e3a5f;
  border-left-color: var(--accent);
  color: #e8e8e8;
}
</style>
