import { ChevronDown, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";

interface AppHeaderProps {
  onNewChat: () => void;
}

export function AppHeader({ onNewChat }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border/60 bg-background/80 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded-full px-1.5 py-1 text-sm font-medium text-foreground transition hover:bg-accent"
        >
          GPT 5
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          size="sm"
          className="hidden rounded-full md:inline-flex"
          onClick={onNewChat}
        >
          <Plus className="mr-2 h-4 w-4" />
          새 대화
        </Button>
      </div>
    </header>
  );
}
