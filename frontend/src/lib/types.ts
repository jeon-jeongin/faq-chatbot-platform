export interface BackendChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: BackendChatMessage[]
}

export type ChatStatus = 'ok' | 'error'

export interface ChatResponse {
  answer: string
  sources: ChatSource[]
  elapsed: number
  status: ChatStatus
}

export interface ChatSource {
  id: number
  question: string
  answer: string
}

export interface ChatSourceDetail {
  id: number
  title: string
  description_html: string
}

export type Sender = 'user' | 'bot'

export interface ChatMessage {
  id: string
  sender: Sender
  content: string
  createdAt: string
  sources?: ChatSource[]
  elapsed?: number
  status?: ChatStatus
}
