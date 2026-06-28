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
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, isLoading]);

  return (
    <div className={`space-y-4 overflow-y-auto pr-1 ${className}`}>
      {messages.map((message) => (
        <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={`max-w-[88%] ${message.role === "user" ? "text-right" : "text-left"}`}>
            {message.role === "assistant" ? (
              <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--sys-muted)]">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--theme-primary-soft)] text-[var(--sys-icon-fill)]">
                  <Bot className="h-3 w-3" />
                </span>
                AUTO VOC
              </div>
            ) : null}
            <div
              className={`whitespace-pre-wrap break-words px-3.5 py-2.5 text-sm leading-6 ${
                message.role === "user"
                  ? "rounded-[18px_18px_5px_18px] bg-[var(--theme-selected-bg)] text-[var(--sys-ink)]"
                  : `rounded-[5px_18px_18px_18px] border border-[var(--sys-border)] bg-white text-[var(--sys-body)] shadow-[0_8px_22px_rgba(20,24,38,0.04)] ${
                      message.isError ? "border-[var(--theme-negative)] text-[var(--theme-negative)]" : ""
                    }`
              }`}
            >
              {message.content}
            </div>
            {message.role === "assistant" && message.suggestions?.length ? (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {message.suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => onSuggestionClick(suggestion)}
                    className="rounded-full border border-[var(--sys-border)] bg-[var(--theme-soft-panel)] px-2.5 py-1 text-[11px] font-medium text-[var(--sys-body)] transition hover:border-[var(--sys-icon-fill)] hover:text-[var(--sys-icon-fill)]"
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
          <div className="flex items-center gap-2 rounded-[5px_18px_18px_18px] border border-[var(--sys-border)] bg-white px-3.5 py-2.5 text-xs text-[var(--sys-muted)]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            正在查询并整理答案…
          </div>
        </div>
      ) : null}
      <div ref={endRef} />
    </div>
  );
}
