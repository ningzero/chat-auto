import { ref, onUnmounted, type Ref } from 'vue'

const WS_URL = import.meta.env.VITE_WS_URL ||
  `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

type EventCallback = (data: any) => void

export function useWebSocket(room: Ref<string>) {
  const ws = ref<WebSocket | null>(null)
  const listeners = ref<Map<string, Set<EventCallback>>>(new Map())

  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) return

    const roomId = room.value || 'general'
    ws.value = new WebSocket(`${WS_URL}/${roomId}`)

    ws.value.onopen = () => {
      listeners.value.get('open')?.forEach(cb => cb(null))
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        listeners.value.get(data.type)?.forEach(cb => cb(data))
      } catch (e) {
        console.error('Failed to parse WS message:', e)
      }
    }

    ws.value.onerror = (error) => {
      listeners.value.get('error')?.forEach(cb => cb(error))
    }

    ws.value.onclose = () => {
      listeners.value.get('close')?.forEach(cb => cb(null))
    }
  }

  const disconnect = () => {
    ws.value?.close()
    ws.value = null
  }

  const send = (data: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected')
    }
  }

  const on = (event: string, callback: EventCallback) => {
    if (!listeners.value.has(event)) {
      listeners.value.set(event, new Set())
    }
    listeners.value.get(event)!.add(callback)
  }

  const off = (event: string, callback: EventCallback) => {
    listeners.value.get(event)?.delete(callback)
  }

  // 清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    send,
    on,
    off
  }
}
