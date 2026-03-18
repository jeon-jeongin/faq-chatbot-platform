import { Clock3, Compass, MessageSquarePlus, PanelLeft, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatSidebarProps {
  items: string[];
  onNewChat: () => void;
}

const quickLinks = [
  { icon: Compass, label: "청약 자격" },
  { icon: Search, label: "입주 조건" },
  { icon: Clock3, label: "자주 묻는 질문" },
];

export function ChatSidebar({ items, onNewChat }: ChatSidebarProps) {
  return (
    <aside className="hidden h-dvh w-72 shrink-0 border-r border-border/70 bg-card/40 md:flex md:flex-col">
      <div className="flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <PanelLeft className="h-4 w-4 text-muted-foreground" />
          FAQ Workspace
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-5 overflow-hidden px-3 pb-4">
        <Button
          variant="secondary"
          className="w-full justify-start rounded-2xl bg-secondary/70"
          onClick={onNewChat}
        >
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          새 FAQ 질문
        </Button>

        <section className="space-y-2">
          <p className="px-2 text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
            빠른 진입
          </p>
          <div className="space-y-1">
            {quickLinks.map(({ icon: Icon, label }) => (
              <button
                key={label}
                type="button"
                className="flex w-full items-center gap-3 rounded-2xl px-3 py-2 text-left text-sm text-muted-foreground transition hover:bg-accent hover:text-accent-foreground"
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>
        </section>

        <section className="min-h-0 flex-1 space-y-2 overflow-hidden">
          <p className="px-2 text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
            최근 질문
          </p>
          <div className="space-y-1 overflow-y-auto pr-1">
            {items.length > 0 ? (
              items.map((item, index) => (
                <div
                  key={`${item}-${index}`}
                  className={cn(
                    "rounded-2xl border border-transparent px-3 py-2 text-sm text-muted-foreground",
                    index === 0 && "bg-secondary/70 text-foreground",
                  )}
                >
                  <p className="line-clamp-2">{item}</p>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-border px-3 py-4 text-sm text-muted-foreground">
                아직 대화가 없습니다. 새 질문을 시작해 보세요.
              </div>
            )}
          </div>
        </section>
      </div>
    </aside>
  );
}
