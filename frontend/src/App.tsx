import { useState } from "react";

import { ChatScreen } from "@/components/chat/chat-screen";
import { AppShell } from "@/components/layout/app-shell";
import { sendChatMessage } from "@/lib/api";
import type { BackendChatMessage, ChatMessage } from "@/lib/types";

const suggestedQuestions = [
  "토스에서 자동이체 등록은 어떻게 하나요?",
  "잔액 부족으로 자동이체가 실패되었는데 어떻게 해야 하나요?",
  "토스 앱에서 송금한 뒤 송금확인증은 어떻게 발급받나요?",
  "해외송금 서비스는 누가 이용할 수 있나요?",
  "토스뱅크의 송금 수수료는 어떻게 되나요?",
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

function toBackendRole(
  sender: ChatMessage["sender"],
): BackendChatMessage["role"] {
  return sender === "user" ? "user" : "assistant";
}

function buildRequestMessages(messages: ChatMessage[]): BackendChatMessage[] {
  const recentMessages = messages
    .filter((message) => message.content.trim().length > 0)
    // 전송 실패 안내 문구는 실제 대화 맥락이 아니므로 히스토리에서 제외합니다.
    .filter((message) => message.status !== "error")
    // 최근 10개 메시지만 보내서 요청 본문이 과도하게 커지지 않도록 제한합니다.
    .slice(-10);

  // 앞 질문이 잘려서 assistant 답변으로 시작하면 문맥이 어색해지므로 제거합니다.
  while (recentMessages.length > 0 && recentMessages[0].sender === "bot") {
    recentMessages.shift();
  }

  return recentMessages.map((message) => ({
    role: toBackendRole(message.sender),
    content: message.content.trim(),
  }));
}

function App() {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = async () => {
    const question = input.trim();
    if (!question || isLoading) {
      return;
    }

    const userMessage = createMessage("user", question);
    // 방금 입력한 사용자 메시지까지 포함한 최신 대화 목록을 먼저 만들고,
    // 이 값을 그대로 화면 표시와 API 요청에 함께 사용합니다.
    const nextMessages = [...messages, userMessage];

    setMessages(nextMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        messages: buildRequestMessages(nextMessages),
      });
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
        {
          status: "error",
        },
      );
      setIsLoading(false);
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
