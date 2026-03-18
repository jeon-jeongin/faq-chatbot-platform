import type { ReactNode } from "react";

import { AppHeader } from "@/components/layout/app-header";

interface AppShellProps {
  children: ReactNode;
  onNewChat: () => void;
}

export function AppShell({ children, onNewChat }: AppShellProps) {
  return (
    <div className="dark h-dvh overflow-hidden bg-background text-foreground">
      <div className="flex h-dvh w-full flex-col overflow-hidden">
        <AppHeader onNewChat={onNewChat} />
        <main className="flex min-h-0 flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
