export type DomainId = "housing";

export interface DomainOption {
  id: DomainId;
  label: string;
  description: string;
}

export interface ChatRequestPayload {
  domain: DomainId;
  question: string;
}

export type ChatStatus = "ok" | "error";

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  elapsed: number;
  status: ChatStatus;
}

export interface ChatSource {
  id: string;
  question: string;
  answer: string;
}

export type Sender = "user" | "bot";

export interface ChatMessage {
  id: string;
  sender: Sender;
  content: string;
  createdAt: string;
  sources?: ChatSource[];
  elapsed?: number;
  status?: ChatStatus;
}

