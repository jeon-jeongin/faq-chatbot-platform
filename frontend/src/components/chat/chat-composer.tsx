import { ArrowUp } from "lucide-react";
import type { KeyboardEvent } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface ChatComposerProps {
  value: string;
  isLoading: boolean;
  compact?: boolean;
  onValueChange: (value: string) => void;
  onSubmit: () => void;
}

export function ChatComposer({
  value,
  isLoading,
  compact = false,
  onValueChange,
  onSubmit,
}: ChatComposerProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div
      className={cn(
        "rounded-[28px] border border-border/80 bg-card/95 shadow-2xl shadow-black/10 backdrop-blur-xl",
        compact ? "px-3 py-3" : "px-4 py-4",
      )}
    >
      <div className="flex items-end gap-3">
        <Textarea
          value={value}
          onChange={(event) => onValueChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="메시지를 입력하세요..."
          rows={compact ? 2 : 3}
          disabled={isLoading}
          className={cn(
            "min-w-0 flex-1 resize-none border-0 bg-transparent px-0 py-1 text-base leading-6 shadow-none placeholder:leading-6 focus-visible:ring-0",
            compact ? "min-h-[52px]" : "min-h-[72px]",
          )}
        />
        <Button
          size="icon"
          className="h-10 w-10 shrink-0 rounded-full"
          onClick={onSubmit}
          disabled={isLoading || value.trim().length === 0}
          aria-label="Send message"
        >
          <ArrowUp className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
