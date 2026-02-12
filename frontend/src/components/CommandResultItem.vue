<template>
  <div class="command-result">
    <div class="command-header">
      <span class="command-type">{{ commandType }}</span>
      <span class="command-input">> {{ data.command }}</span>
    </div>

    <div v-if="result.type === 'list_scripts'" class="scripts-list">
      <div v-if="result.scripts.length === 0" class="empty">No scripts available</div>
      <div v-else>
        <div v-for="script in result.scripts" :key="script.command" class="script-item">
          <code class="script-command">{{ script.command }}</code>
          <span class="script-name">{{ script.name }}</span>
          <span v-if="script.description" class="script-desc">{{ script.description }}</span>
        </div>
      </div>
    </div>

    <div v-else-if="result.type === 'script_started'" class="script-started">
      <span class="status running">Executing...</span>
      <span>Script "{{ result.script }}" started (Task #{{ result.task_id }})</span>
    </div>

    <div v-else-if="result.type === 'script_completed'" class="script-completed">
      <div class="status-info">
        <span :class="['status', result.status]">
          {{ result.status === 'completed' ? 'Success' : 'Failed' }}
        </span>
        <span v-if="result.exit_code !== undefined" class="exit-code">
          Exit: {{ result.exit_code }}
        </span>
      </div>

      <div class="result-section">
        <div class="result-section-title">Output:</div>
        <pre class="result-output">{{ result.output || '(no output)' }}</pre>
      </div>

      <div v-if="result.error" class="result-section error">
        <div class="result-section-title">Error:</div>
        <pre class="result-output">{{ result.error }}</pre>
      </div>
    </div>

    <div v-else-if="result.type === 'task_status'" class="task-status">
      <div class="status-info">
        <span :class="['status', result.task.status]">
          {{ result.task.status }}
        </span>
      </div>
      <div class="result-section">
        <pre class="result-output">{{ result.task.output || '(no output)' }}</pre>
      </div>
    </div>

    <pre v-else class="result-raw">{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: {
    command: string
    result: any
  }
}>()

const result = computed(() => props.data.result)

const commandType = computed(() => {
  return result.value.type || 'command'
})
</script>

<style scoped>
.command-result {
  background-color: #0d1b2a;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin: 16px 0;
  overflow: hidden;
}

.command-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background-color: var(--bg-tertiary);
  border-bottom: 1px solid var(--border);
}

.command-type {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: var(--accent);
  text-transform: uppercase;
  font-weight: 600;
}

.command-input {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: var(--text-secondary);
}

.scripts-list {
  padding: 12px;
}

.script-item {
  display: grid;
  grid-template-columns: auto auto 1fr;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.script-item:last-child {
  border-bottom: none;
}

.script-command {
  font-family: 'Monaco', 'Menlo', monospace;
  background-color: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--success);
}

.script-name {
  font-weight: 600;
  color: var(--text-primary);
}

.script-desc {
  color: var(--text-secondary);
  font-size: 13px;
}

.empty {
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.script-started,
.task-status {
  padding: 12px 14px;
}

.status-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 600;
}

.status.running {
  background-color: #ffd93d40;
  color: var(--warning);
}

.status.completed,
.status.success {
  background-color: #4ecdc440;
  color: var(--success);
}

.status.failed,
.status.error {
  background-color: #ff6b6b40;
  color: var(--error);
}

.exit-code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.script-completed {
  padding: 0;
}

.result-section {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
}

.result-section:last-child {
  border-bottom: none;
}

.result-section.error {
  background-color: rgba(255, 107, 107, 0.1);
}

.result-section-title {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
  font-weight: 600;
}

.result-output {
  margin: 0;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.result-raw {
  margin: 0;
  padding: 14px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: var(--text-primary);
  white-space: pre-wrap;
}
</style>
