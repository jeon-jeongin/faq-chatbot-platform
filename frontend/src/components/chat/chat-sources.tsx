import { Clock3, FileText, Info, LoaderCircle } from "lucide-react";
import { useMemo, useState } from "react";

import { fetchChatSourceDetail } from "@/lib/api";
import type { ChatMessage, ChatSourceDetail } from "@/lib/types";

type Source = NonNullable<ChatMessage["sources"]>[number];

interface ChatSourcesProps {
  message: ChatMessage;
}

export function ChatSources({ message }: ChatSourcesProps) {
  const hasSources = !!message.sources?.length;
  const hasElapsed = typeof message.elapsed === "number";
  const isError = message.status === "error";

  const [activeSourceId, setActiveSourceId] = useState<number | null>(null);
  const [detailBySourceId, setDetailBySourceId] = useState<
    Record<number, ChatSourceDetail>
  >({});
  const [loadingSourceId, setLoadingSourceId] = useState<number | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  const activeSource = useMemo(() => {
    if (!activeSourceId) return null;
    return message.sources?.find((s) => s.id === activeSourceId) ?? null;
  }, [activeSourceId, message.sources]);

  const activeSourceDetail = activeSourceId
    ? detailBySourceId[activeSourceId] ?? null
    : null;

  async function handleSourceClick(sourceId: number) {
    if (activeSourceId === sourceId) {
      setActiveSourceId(null);
      setDetailError(null);
      return;
    }

    setActiveSourceId(sourceId);
    setDetailError(null);

    // 이미 조회한 근거는 재호출하지 않고 캐시된 내용을 그대로 사용합니다.
    if (detailBySourceId[sourceId]) {
      return;
    }

    setLoadingSourceId(sourceId);

    try {
      const detail = await fetchChatSourceDetail(sourceId);
      setDetailBySourceId((previous) => ({
        ...previous,
        [sourceId]: detail,
      }));
    } catch {
      setDetailError("상세 근거를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.");
    } finally {
      setLoadingSourceId((current) => (current === sourceId ? null : current));
    }
  }

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
                  onClick={() => handleSourceClick(source.id)}
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
                  {activeSourceDetail?.title ?? activeSource.question}
                </div>

                {loadingSourceId === activeSource.id && (
                  <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                    <LoaderCircle className="h-4 w-4 animate-spin" />
                    선택한 근거의 상세 내용을 불러오는 중이에요.
                  </div>
                )}

                {detailError && loadingSourceId !== activeSource.id && (
                  <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
                    {detailError}
                  </div>
                )}

                {activeSourceDetail && (
                  <div
                    className="prose prose-sm max-w-none break-words text-foreground leading-6 prose-headings:my-2 prose-p:my-2 prose-p:leading-6 prose-ul:my-2 prose-ol:my-2 prose-li:my-1 prose-li:leading-6 prose-br:leading-6 prose-img:my-2 prose-img:max-h-64 prose-img:w-auto prose-img:rounded-lg prose-strong:text-foreground prose-a:text-primary prose-p:text-muted-foreground prose-li:text-muted-foreground"
                    // 백엔드 CSV에 저장된 FAQ HTML을 그대로 렌더링해 원문 서식을 살려줍니다.
                    dangerouslySetInnerHTML={{
                      __html: activeSourceDetail.description_html,
                    }}
                  />
                )}

                {!activeSourceDetail &&
                  loadingSourceId !== activeSource.id &&
                  !detailError && (
                    <div className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
                      {activeSource.answer}
                    </div>
                  )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
