import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";

interface AppHeaderProps {
  onNewChat: () => void;
}

export function AppHeader({ onNewChat }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-end border-b border-border/60 bg-background/80 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          size="sm"
          className="hidden rounded-full md:inline-flex"
          onClick={onNewChat}
        >
          <Plus className="mr-2 h-4 w-4" />새 대화
        </Button>
      </div>
    </header>
  );
}
