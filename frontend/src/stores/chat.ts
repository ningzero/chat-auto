import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useWebSocket } from '@/api/websocket'
import { getMessages } from '@/api/messages'

interface Message {
  id?: number
  content: string
  is_command?: number
  author_id?: number
  room_id?: string
  command_result?: string | null
  error_message?: string | null
  created_at?: string
  author?: {
    id: number
    username: string
    nickname?: string
  }
}

interface CommandResult {
  id?: number
  command?: string
  result?: any
  user_id?: number
  data?: {
    command?: string
    result?: any
  }
}

interface ChatMessage {
  type: 'message' | 'command'
  _index: number
  id?: number
  content?: string
  is_command?: number
  author_id?: number
  author?: Message['author']
  created_at?: string
  data?: CommandResult['data']
}

export const useChatStore = defineStore('chat', () => {
  const room = ref('general')
  const messages = ref<Message[]>([])
  const commandResults = ref<CommandResult[]>([])
  const connected = ref(false)
  const loadingHistory = ref(false)
  const currentUser = ref<{ id: number; username: string } | null>(null)
  let messageIndex = 0

  const ws = useWebSocket(room)

  const connect = () => {
    ws.connect()

    ws.on('message', (data: Message & { type: string }) => {
      if (data && data.content) {
        messages.value.push(data)
        scrollToBottom()
      }
    })

    ws.on('command_result', (data: CommandResult & { type: string }) => {
      if (data) {
        commandResults.value.push(data)
      }
    })

    ws.on('error', (data: any) => {
      console.error('WebSocket error:', data)
    })

    ws.on('open', () => {
      connected.value = true
      loadHistory()
    })

    ws.on('close', () => {
      connected.value = false
    })
  }

  const disconnect = () => {
    ws.disconnect()
  }

  const sendMessage = (content: string) => {
    ws.send({
      type: 'message',
      content,
      room_id: room.value
    })
  }

  const executeCommand = (command: string) => {
    ws.send({
      type: 'message',
      content: command,
      room_id: room.value
    })
  }

  const clearResults = () => {
    commandResults.value = []
  }

  const loadHistory = async () => {
    if (loadingHistory.value) return
    loadingHistory.value = true
    try {
      const history = await getMessages(room.value, 100)
      messages.value = history
      scrollToBottom()
    } catch (error) {
      console.error('Failed to load message history:', error)
    } finally {
      loadingHistory.value = false
    }
  }

  const allMessages = computed((): ChatMessage[] => {
    const result: ChatMessage[] = []

    // 添加普通消息
    for (const m of messages.value) {
      if (m && m.content) {
        result.push({
          type: 'message',
          _index: messageIndex++,
          id: m.id,
          content: m.content,
          is_command: m.is_command,
          author_id: m.author_id,
          author: m.author,
          created_at: m.created_at
        })

        // 如果有保存的命令结果，也添加
        if (m.command_result || m.error_message) {
          try {
            const parsed = m.command_result ? JSON.parse(m.command_result) : null
            result.push({
              type: 'command',
              _index: messageIndex++,
              data: {
                command: m.content,
                result: m.error_message ? { error: m.error_message } : (parsed || {})
              }
            })
          } catch {
            // 如果解析失败，直接显示错误信息
            result.push({
              type: 'command',
              _index: messageIndex++,
              data: {
                command: m.content,
                result: { error: m.error_message || 'Unknown error' }
              }
            })
          }
        }
      }
    }

    // 添加实时命令结果（WebSocket）
    for (const r of commandResults.value) {
      if (r && (r.command || (r.data && r.data.command))) {
        result.push({
          type: 'command',
          _index: messageIndex++,
          data: r.data || { command: r.command, result: r.result }
        })
      }
    }

    return result
  })

  return {
    room,
    messages,
    commandResults,
    connected,
    loadingHistory,
    currentUser,
    connect,
    disconnect,
    sendMessage,
    executeCommand,
    clearResults,
    loadHistory,
    allMessages
  }
})

function scrollToBottom() {
  setTimeout(() => {
    const container = document.querySelector('.messages-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, 100)
}
