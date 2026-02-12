import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''  // Empty string to use relative URLs (works with Vite proxy)

export interface Message {
  id: number
  content: string
  author_id: number
  room_id: string
  is_command: number
  created_at: string
  author?: {
    id: number
    username: string
    nickname?: string
  }
}

export interface Command {
  name: string
  description: string
}

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export async function getMessages(roomId: string = 'general', limit: number = 50): Promise<Message[]> {
  const response = await api.get<Message[]>('/api/messages', {
    params: { room_id: roomId, limit }
  })
  return response.data
}

export async function createMessage(content: string, roomId: string = 'general', isCommand: boolean = false): Promise<Message> {
  const response = await api.post<Message>('/api/messages', {
    content,
    room_id: roomId,
    is_command: isCommand ? 1 : 0
  })
  return response.data
}

export async function getCommands(): Promise<Command[]> {
  const response = await api.get<Command[]>('/api/scripts/commands')
  return response.data
}
