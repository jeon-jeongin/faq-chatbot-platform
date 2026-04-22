import { API_BASE_URL } from '@/lib/config'
import type { ChatRequest, ChatResponse, ChatSourceDetail } from '@/lib/types'

export async function sendChatMessage(
  payload: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/toss_faq`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return response.json()
}

export async function fetchChatSourceDetail(
  docId: number,
): Promise<ChatSourceDetail> {
  const response = await fetch(`${API_BASE_URL}/api/toss_faq/sources/${docId}`)

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return response.json()
}
