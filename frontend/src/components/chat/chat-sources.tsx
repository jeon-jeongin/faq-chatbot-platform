import { Clock3, FileText, Info } from "lucide-react";
import { useMemo, useState } from "react";

import type { ChatMessage } from "@/lib/types";

type Source = NonNullable<ChatMessage["sources"]>[number];

interface ChatSourcesProps {
  message: ChatMessage;
}

export function ChatSources({ message }: ChatSourcesProps) {
  const hasSources = !!message.sources?.length;
  const hasElapsed = typeof message.elapsed === "number";
  const isError = message.status === "error";

  const [activeSourceId, setActiveSourceId] = useState<string | null>(null);

  const activeSource = useMemo(() => {
    if (!activeSourceId) return null;
    return message.sources?.find((s) => s.id === activeSourceId) ?? null;
  }, [activeSourceId, message.sources]);

  if (!hasSources && !hasElapsed && !isError) {
    return null;
  }

  return (
    <div className="mt-3 space-y-3 border-t border-border/70 pt-3">
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        {hasElapsed && (
          <span className="inline-flex items-center gap-1">
            <Clock3 className="h-3.5 w-3.5" />
            {message.elapsed?.toFixed(2)}s
          </span>
        )}
        {isError && (
          <span className="inline-flex items-center gap-1 text-destructive">
            <Info className="h-3.5 w-3.5" />
            연결 또는 검색 오류
          </span>
        )}
      </div>

      {hasSources && (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            Sources
          </p>
          <div className="grid gap-2 sm:grid-cols-1">
            {message.sources?.map((source: Source) => {
              const active = source.id === activeSourceId;
              return (
                <button
                  key={source.id}
                  type="button"
                  onClick={() => setActiveSourceId(active ? null : source.id)}
                  className="rounded-2xl border border-border/70 bg-background/80 px-3 py-2 text-left text-sm text-muted-foreground transition hover:bg-accent/60"
                  aria-expanded={active}
                >
                  <div className="inline-flex items-center gap-2 text-foreground">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{source.question}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {activeSource && (
            <div className="rounded-2xl border border-border/70 bg-background/80 px-3 py-3">
              <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
                선택한 근거
              </div>
              <div className="space-y-2">
                <div className="text-sm text-foreground">
                  {activeSource.question}
                </div>
                <div className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
                  {activeSource.answer}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
