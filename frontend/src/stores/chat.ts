import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useWebSocket } from '@/api/websocket'

interface Message {
  id?: number
  content: string
  is_command: number
  author_id: number
  room_id?: string
  created_at?: string
  author?: {
    id: number
    username: string
    nickname?: string
  }
}

interface CommandResult {
  id?: number
  command: string
  result: any
  user_id?: number
}

export const useChatStore = defineStore('chat', () => {
  const room = ref('general')
  const messages = ref<Message[]>([])
  const commandResults = ref<CommandResult[]>([])
  const connected = ref(false)
  const currentUser = ref<{ id: number; username: string } | null>(null)

  const ws = useWebSocket(room)

  const connect = () => {
    ws.connect()

    ws.on('message', (data: Message) => {
      messages.value.push(data)
      scrollToBottom()
    })

    ws.on('command_result', (data: CommandResult) => {
      commandResults.value.push(data)
    })

    ws.on('error', (data: any) => {
      console.error('WebSocket error:', data)
    })

    ws.on('open', () => {
      connected.value = true
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

  const allMessages = computed(() => {
    // 合并普通消息和命令结果
    const combined = [
      ...messages.value.map(m => ({ ...m, type: 'message' })),
      ...commandResults.value.map(r => ({ ...r, type: 'command' }))
    ]
    // 按时间排序
    return combined.sort((a, b) => {
      const timeA = a.created_at ? new Date(a.created_at).getTime() : 0
      const timeB = b.created_at ? new Date(b.created_at).getTime() : 0
      return timeA - timeB
    })
  })

  return {
    room,
    messages,
    commandResults,
    connected,
    currentUser,
    connect,
    disconnect,
    sendMessage,
    executeCommand,
    clearResults,
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
