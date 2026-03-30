import { API_BASE_URL } from "@/lib/config";
import type { ChatRequestPayload, ChatResponse } from "@/lib/types";

export async function sendChatMessage(
  payload: ChatRequestPayload,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

