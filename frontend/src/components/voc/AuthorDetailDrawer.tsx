"use client";

import { useEffect, useState } from "react";
import { ExternalLink, Loader2, X } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { AuthorDetailPayload } from "@/types/vocMarket";

import { AuthorDetailPage } from "./AuthorDetailPage";

type AuthorDetailDrawerProps = {
  authorId: string | null;
  onClose: () => void;
};

type LoadState = "idle" | "loading" | "error";

function buildAuthorDetailUrl(authorId: string) {
  return `${apiBaseUrl}/voc/authors/${encodeURIComponent(authorId)}/detail`;
}

export function AuthorDetailDrawer({ authorId, onClose }: AuthorDetailDrawerProps) {
  const [payload, setPayload] = useState<AuthorDetailPayload | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");

  useEffect(() => {
    if (!authorId) {
      setPayload(null);
      setLoadState("idle");
      return;
    }
    let active = true;
    setLoadState("loading");
    setPayload(null);
    fetch(buildAuthorDetailUrl(authorId), { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<AuthorDetailPayload>;
      })
      .then((nextPayload) => {
        if (!active) return;
        setPayload(nextPayload);
        setLoadState("idle");
      })
      .catch(() => {
        if (!active) return;
        setPayload(null);
        setLoadState("error");
      });
    return () => {
      active = false;
    };
  }, [authorId]);

  useEffect(() => {
    if (!authorId) return;
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [authorId, onClose]);

  if (!authorId) return null;

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        aria-label="关闭作者详情遮罩"
        className="absolute inset-0 cursor-default bg-[var(--theme-ink)]/20 backdrop-blur-[2px]"
        onClick={onClose}
      />
      <aside className="absolute right-0 top-0 flex h-full w-full max-w-[880px] flex-col overflow-hidden rounded-l-3xl border-l border-[var(--theme-border)] bg-[var(--theme-soft-panel)] shadow-[-18px_0_50px_rgba(26,32,44,0.16)]">
        <div className="flex items-center justify-between gap-3 border-b border-[var(--theme-border)] bg-[var(--theme-white)]/85 px-5 py-4 backdrop-blur">
          <div>
            <p className="text-xs font-medium text-[var(--theme-muted)]">Author Drilldown</p>
            <h2 className="mt-0.5 text-base font-semibold text-[var(--theme-ink)]">作者详情</h2>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={`/voc/authors/${encodeURIComponent(authorId)}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-xs font-medium text-[var(--theme-body)] hover:text-[var(--theme-primary)]"
            >
              独立页
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] hover:text-[var(--theme-ink)]"
              aria-label="关闭作者详情"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 [&_.author-back-link]:hidden">
          {loadState === "loading" ? (
            <div className="flex h-80 items-center justify-center rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] text-sm text-[var(--theme-muted)]">
              <Loader2 className="mr-2 h-4 w-4 animate-spin text-[var(--theme-primary)]" />
              正在加载作者详情
            </div>
          ) : null}

          {loadState === "error" ? (
            <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-white text-sm text-[var(--theme-muted)]">
              作者详情加载失败，请确认后端服务与作者资产数据。
            </div>
          ) : null}

          {payload ? <AuthorDetailPage payload={payload} showBackLink={false} /> : null}
        </div>
      </aside>
    </div>
  );
}
