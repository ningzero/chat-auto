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

interface ChatMessage {
  type: 'message' | 'command'
  key: string  // 稳定的 key，用于 Vue 的 v-for
  id?: number
  content?: string
  is_command?: number
  author_id?: number
  author?: Message['author']
  created_at?: string
  data?: {
    command?: string
    result?: any
  }
}

export const useChatStore = defineStore('chat', () => {
  const room = ref('general')
  const messages = ref<Message[]>([])
  const connected = ref(false)
  const loadingHistory = ref(false)
  const currentUser = ref<{ id: number; username: string } | null>(null)

  const ws = useWebSocket(room)

  const connect = () => {
    ws.connect()

    ws.on('message', (eventData: { type: string; data: Message }) => {
      const data = eventData.data
      if (data && data.content) {
        // 检查是否已存在 id 为 -1 的临时消息（我们发送的消息）
        const existingIndex = messages.value.findIndex(
          m => m.id === -1 && m.content === data.content
        )

        if (existingIndex !== -1) {
          // 更新临时消息为 confirmed 消息
          messages.value[existingIndex] = {
            ...messages.value[existingIndex],
            id: data.id,
            author_id: data.author_id,
            created_at: data.created_at,
            command_result: data.command_result,
            error_message: data.error_message
          }
        } else {
          // 查找是否已存在相同 id 的消息（命令结果更新）
          const foundIndex = messages.value.findIndex(m => m.id === data.id)
          if (foundIndex !== -1) {
            // 更新现有消息（命令结果更新）
            messages.value[foundIndex] = {
              ...messages.value[foundIndex],
              command_result: data.command_result,
              error_message: data.error_message
            }
          } else {
            // 新消息，直接添加
            messages.value.push(data)
          }
        }
        scrollToBottom()
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
    // 立即添加消息到本地列表进行回显（使用特殊的 ID 标记为临时消息）
    const tempMessage: Message = {
      id: -1,  // 使用 -1 标记临时消息
      content,
      is_command: content.startsWith('/') ? 1 : 0,
      author_id: currentUser.value?.id,
      room_id: room.value,
      created_at: new Date().toISOString(),
      author: currentUser.value ? {
        id: currentUser.value.id,
        username: currentUser.value.username
      } : undefined
    }
    messages.value.push(tempMessage)
    scrollToBottom()

    // 通过 WebSocket 发送给服务器
    ws.send({
      type: 'message',
      content,
      room_id: room.value
    })
  }

  const executeCommand = (command: string) => {
    // 立即添加消息到本地列表进行回显
    const tempMessage: Message = {
      id: -1,
      content: command,
      is_command: 1,
      author_id: currentUser.value?.id,
      room_id: room.value,
      created_at: new Date().toISOString(),
      author: currentUser.value ? {
        id: currentUser.value.id,
        username: currentUser.value.username
      } : undefined
    }
    messages.value.push(tempMessage)
    scrollToBottom()

    ws.send({
      type: 'message',
      content: command,
      room_id: room.value
    })
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
        const messageId = m.id || m.content  // 使用 id 或 content 作为唯一标识
        result.push({
          type: 'message',
          key: `msg-${messageId}`,
          id: m.id,
          content: m.content,
          is_command: m.is_command,
          author_id: m.author_id,
          author: m.author,
          created_at: m.created_at
        })

        // 如果有保存的命令结果，也添加
        if (m.command_result || m.error_message) {
          const resultId = `${messageId}-result`
          try {
            const parsed = m.command_result ? JSON.parse(m.command_result) : null
            result.push({
              type: 'command',
              key: `cmd-${resultId}`,
              data: {
                command: m.content,
                result: m.error_message ? { error: m.error_message } : (parsed || {})
              }
            })
          } catch {
            // 如果解析失败，直接显示错误信息
            result.push({
              type: 'command',
              key: `cmd-${resultId}`,
              data: {
                command: m.content,
                result: { error: m.error_message || 'Unknown error' }
              }
            })
          }
        }
      }
    }

    return result
  })

  return {
    room,
    messages,
    connected,
    loadingHistory,
    currentUser,
    connect,
    disconnect,
    sendMessage,
    executeCommand,
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
