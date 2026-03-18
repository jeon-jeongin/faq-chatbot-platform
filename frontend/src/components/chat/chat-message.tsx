import { Copy, Sparkles, UserRound } from "lucide-react";

import { ChatSources } from "@/components/chat/chat-sources";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import type { ChatMessage as ChatMessageType } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === "user";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
    } catch {
      // Ignore clipboard failures in unsupported environments.
    }
  };

  return (
    <div
      className={cn(
        "group mx-auto flex w-full max-w-3xl gap-4 px-4 py-6 md:px-6",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <Avatar className="mt-1 h-8 w-8 border border-border/80 bg-card">
          <AvatarFallback className="bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div
        className={cn(
          "max-w-[85%] space-y-2",
          isUser ? "items-end text-right" : "items-start text-left",
        )}
      >
        <div
          className={cn(
            "rounded-[24px] px-4 py-3 text-sm leading-7 shadow-sm",
            isUser
              ? "ml-auto bg-secondary text-secondary-foreground"
              : "bg-card text-card-foreground",
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
          {!isUser && <ChatSources message={message} />}
        </div>

        <div
          className={cn(
            "flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100",
            isUser ? "justify-end" : "justify-start",
          )}
        >
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full text-muted-foreground"
            onClick={handleCopy}
            aria-label="Copy message"
          >
            <Copy className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {isUser && (
        <Avatar className="mt-1 h-8 w-8 border border-border/80 bg-card">
          <AvatarFallback className="bg-secondary text-secondary-foreground">
            <UserRound className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
