import { useState } from "react";

import { ChatScreen } from "@/components/chat/chat-screen";
import { AppShell } from "@/components/layout/app-shell";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, DomainId } from "@/lib/types";

const suggestedQuestions = [
  "청년 특별공급 신청 자격이 궁금해요.",
  "무주택 기준은 어떻게 판단하나요?",
  "소득 기준과 자산 기준을 함께 알려주세요.",
  "청약 신청 절차를 단계별로 설명해 주세요.",
];

function createMessage(
  sender: ChatMessage["sender"],
  content: string,
  extra?: Partial<ChatMessage>,
): ChatMessage {
  return {
    id: crypto.randomUUID(),
    sender,
    content,
    createdAt: new Date().toISOString(),
    ...extra,
  };
}

function App() {
  const domain: DomainId = "housing";
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = async () => {
    const question = input.trim();
    if (!question || isLoading) {
      return;
    }

    const userMessage = createMessage("user", question);
    setMessages((previous) => [...previous, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage({ domain, question });
      const botMessage = createMessage("bot", response.answer, {
        sources: response.sources,
        elapsed: response.elapsed,
        status: response.status,
      });
      setMessages((previous) => [...previous, botMessage]);
    } catch {
      const errorMessage = createMessage(
        "bot",
        "The backend request failed. Make sure the FastAPI server is running on http://127.0.0.1:8000.",
        { status: "error" },
      );
      setMessages((previous) => [...previous, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
    setIsLoading(false);
  };

  const handleSuggestionSelect = (value: string) => {
    setInput(value);
  };

  return (
    <AppShell onNewChat={handleNewChat}>
      <ChatScreen
        messages={messages}
        input={input}
        isLoading={isLoading}
        suggestions={suggestedQuestions}
        onInputChange={setInput}
        onSubmit={handleSubmit}
        onSuggestionSelect={handleSuggestionSelect}
      />
    </AppShell>
  );
}

export default App;
