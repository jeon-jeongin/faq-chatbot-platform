import { Button } from "@/components/ui/button";

interface ChatEmptyStateProps {
  suggestions: string[];
  onSelectSuggestion: (value: string) => void;
}

export function ChatEmptyState({
  suggestions,
  onSelectSuggestion,
}: ChatEmptyStateProps) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
      <h1 className="max-w-2xl text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
        무엇이 궁금하신가요?
      </h1>

      <div className="mt-10 flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion) => (
          <Button
            key={suggestion}
            variant="outline"
            className="rounded-full bg-background/70 text-sm text-muted-foreground"
            onClick={() => onSelectSuggestion(suggestion)}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}
