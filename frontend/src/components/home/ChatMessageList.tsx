"use client";

import { Bot, Loader2 } from "lucide-react";
import { useEffect, useRef } from "react";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  isError?: boolean;
};

type ChatMessageListProps = {
  messages: ChatMessage[];
  isLoading: boolean;
  onSuggestionClick: (question: string) => void;
  className?: string;
};

export function ChatMessageList({ messages, isLoading, onSuggestionClick, className = "" }: ChatMessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldFollowRef = useRef(true);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !shouldFollowRef.current) return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const frame = window.requestAnimationFrame(() => {
      container.scrollTo({ top: container.scrollHeight, behavior: reduceMotion ? "auto" : "smooth" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [messages, isLoading]);

  return (
    <div
      ref={containerRef}
      onScroll={(event) => {
        const element = event.currentTarget;
        shouldFollowRef.current = element.scrollHeight - element.scrollTop - element.clientHeight < 120;
      }}
      className={`space-y-5 overflow-y-auto pr-1 ${className}`}
    >
      {messages.map((message) => (
        <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={message.role === "user" ? "max-w-[82%] text-right sm:max-w-[72%]" : "w-full text-left"}>
            {message.role === "assistant" ? (
              <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--sys-muted)]">
                <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-[var(--theme-primary-soft)] text-[var(--sys-icon-fill)]">
                  <Bot className="h-3.5 w-3.5" />
                </span>
                AUTO VOC
              </div>
            ) : null}
            <div
              className={`whitespace-pre-wrap break-words text-sm ${
                message.role === "user"
                  ? "rounded-[18px_18px_6px_18px] bg-[var(--theme-selected-bg)] px-4 py-2.5 leading-6 text-[var(--sys-ink)]"
                  : `rounded-[18px] border border-[var(--sys-border)] bg-white px-4 py-4 leading-7 text-[var(--sys-body)] shadow-[0_10px_28px_rgba(31,43,39,0.04)] sm:px-5 ${
                      message.isError ? "border-[var(--theme-negative)] text-[var(--theme-negative)]" : ""
                    }`
              }`}
            >
              {message.content}
            </div>
            {message.role === "assistant" && message.suggestions?.length ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => onSuggestionClick(suggestion)}
                    className="rounded-xl border border-[var(--sys-border)] bg-[var(--theme-soft-panel)] px-3 py-1.5 text-[11px] font-medium text-[var(--sys-body)] transition hover:border-[var(--sys-icon-fill)] hover:bg-white hover:text-[var(--sys-icon-fill)] focus-visible:outline-none focus-visible:shadow-[var(--sys-focus-ring)]"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      ))}
      {isLoading ? (
        <div className="flex justify-start">
          <div className="flex items-center gap-2 rounded-[18px] border border-[var(--sys-border)] bg-white px-4 py-3 text-xs text-[var(--sys-muted)] shadow-[0_10px_28px_rgba(31,43,39,0.04)]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            正在查询并整理答案…
          </div>
        </div>
      ) : null}
    </div>
  );
}
