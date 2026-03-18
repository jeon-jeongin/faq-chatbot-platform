import { Sparkles } from "lucide-react";
import { useEffect, useMemo, useRef } from "react";

import { ChatMessage } from "@/components/chat/chat-message";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatConversationProps {
  messages: ChatMessageType[];
  isLoading: boolean;
}

export function ChatConversation({
  messages,
  isLoading,
}: ChatConversationProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewport = scrollAreaRef.current?.querySelector(
      "[data-radix-scroll-area-viewport]",
    );
    if (!(viewport instanceof HTMLDivElement) || messages.length === 0) {
      return;
    }

    const lastMessage = messages[messages.length - 1];
    const lastUserMessage = [...messages].reverse().find(
      (message) => message.sender === "user",
    );

    if (lastMessage?.sender === "user" && lastUserMessage) {
      const anchor = viewport.querySelector<HTMLElement>(
        `[data-message-id="${lastUserMessage.id}"]`,
      );
      if (anchor) {
        viewport.scrollTo({
          top: Math.max(anchor.offsetTop - 24, 0),
          behavior: "smooth",
        });
        return;
      }
    }

    if (!isLoading) {
      viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isLoading]);

  const visibleMessages = useMemo(() => messages, [messages]);

  return (
    <ScrollArea ref={scrollAreaRef} className="h-full overscroll-contain">
      <div className="pb-44 pt-6 md:pb-48">
        {visibleMessages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="mx-auto flex w-full max-w-3xl gap-3 px-4 py-3 md:px-6 md:py-4">
            <Avatar className="mt-1 h-8 w-8 border border-border/80 bg-card">
              <AvatarFallback className="bg-primary/10 text-primary">
                <Sparkles className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div className="rounded-[24px] bg-card px-4 py-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.2s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.1s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
              </div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
