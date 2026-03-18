import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatConversation } from "@/components/chat/chat-conversation";
import { ChatEmptyState } from "@/components/chat/chat-empty-state";
import type { ChatMessage } from "@/lib/types";

interface ChatScreenProps {
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  suggestions: string[];
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  onSuggestionSelect: (value: string) => void;
}

export function ChatScreen({
  messages,
  input,
  isLoading,
  suggestions,
  onInputChange,
  onSubmit,
  onSuggestionSelect,
}: ChatScreenProps) {
  const isEmpty = messages.length === 0;

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
      {isEmpty ? (
        <div className="flex min-h-0 flex-1 items-center justify-center px-4 py-6 md:px-6 md:py-8">
          <div className="flex w-full max-w-3xl -translate-y-6 flex-col items-center gap-8 md:-translate-y-8">
            <ChatEmptyState
              suggestions={suggestions}
              onSelectSuggestion={onSuggestionSelect}
            />
            <div className="w-full">
              <ChatComposer
                value={input}
                isLoading={isLoading}
                onValueChange={onInputChange}
                onSubmit={onSubmit}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
          <div className="min-h-0 flex-1 px-4 pt-4 md:px-6">
            <ChatConversation messages={messages} isLoading={isLoading} />
          </div>
          <div className="pointer-events-none fixed right-0 bottom-0 left-0 z-40 bg-gradient-to-t from-background via-background/95 to-transparent px-4 pb-6 pt-6 md:px-6 md:pb-8">
            <div className="pointer-events-auto mx-auto w-full max-w-3xl">
              <ChatComposer
                compact
                value={input}
                isLoading={isLoading}
                onValueChange={onInputChange}
                onSubmit={onSubmit}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
