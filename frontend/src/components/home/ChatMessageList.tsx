"use client";

import { Bot, FileSearch, Loader2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { StructuredReportView } from "@/components/voc/ReportAiSummaryCard";
import { InsightResultCard } from "@/components/home/InsightResultCard";
import type { CompetitorReportAsset, InsightResult, ReportAgentPayload } from "@/types/vocMarket";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  isError?: boolean;
  reportPayload?: ReportAgentPayload;
  reportAsset?: CompetitorReportAsset;
  insightPayload?: InsightResult;
  retryQuestion?: string;
  retryCapability?: string;
};

type ChatMessageListProps = {
  messages: ChatMessage[];
  isLoading: boolean;
  onSuggestionClick: (question: string) => void;
  onRetry: (question: string, capability: string) => void;
  className?: string;
};

export function ChatMessageList({ messages, isLoading, onSuggestionClick, onRetry, className = "" }: ChatMessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldFollowRef = useRef(true);
  const [openReport, setOpenReport] = useState<ReportAgentPayload | null>(null);

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
            {message.role === "assistant" && message.insightPayload ? <InsightResultCard result={message.insightPayload} /> : null}
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
            {message.role === "assistant" && message.reportPayload?.summary.structured_report ? (
              <button
                type="button"
                onClick={() => setOpenReport(message.reportPayload ?? null)}
                className="mt-3 inline-flex items-center gap-2 rounded-xl border border-[var(--sys-border)] bg-[var(--theme-soft-panel)] px-3 py-2 text-xs font-semibold text-[var(--sys-icon-fill)] transition hover:border-[var(--sys-icon-fill)] hover:bg-white"
              >
                <FileSearch className="h-4 w-4" />
                查看报告
              </button>
            ) : null}
            {message.role === "assistant" && message.retryQuestion && message.retryCapability ? (
              <button
                type="button"
                disabled={isLoading}
                onClick={() => onRetry(message.retryQuestion ?? "", message.retryCapability ?? "")}
                className="mt-3 inline-flex items-center rounded-xl border border-[var(--theme-negative)] bg-white px-3 py-2 text-xs font-semibold text-[var(--theme-negative)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                重试生成
              </button>
            ) : null}
            {message.role === "assistant" && message.reportAsset?.report_run_id != null ? (
              <a
                href={`/assets/reports?report_type=competitor_report&report_run_id=${encodeURIComponent(String(message.reportAsset.report_run_id))}`}
                className="mt-3 inline-flex items-center gap-2 rounded-xl border border-[var(--sys-border)] bg-[var(--theme-soft-panel)] px-3 py-2 text-xs font-semibold text-[var(--sys-icon-fill)] transition hover:border-[var(--sys-icon-fill)] hover:bg-white"
              >
                <FileSearch className="h-4 w-4" />
                查看竞品报告
              </a>
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
      {openReport?.summary.structured_report ? (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/20 p-4 backdrop-blur-sm">
          <div className="max-h-[88vh] w-full max-w-5xl overflow-hidden rounded-[28px] border border-[var(--theme-border)] bg-[var(--theme-white)] shadow-[0_24px_80px_rgba(26,32,44,0.2)]">
            <header className="flex items-center justify-between gap-3 border-b border-[var(--theme-border)] bg-[linear-gradient(135deg,var(--theme-selected-bg),var(--theme-card))] p-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--theme-muted)]">Event Report</p>
                <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">{openReport.summary.structured_report.title}</h2>
              </div>
              <button
                type="button"
                onClick={() => setOpenReport(null)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)] transition hover:bg-[var(--theme-hover-bg)]"
                aria-label="关闭报告"
              >
                <X className="h-4 w-4" />
              </button>
            </header>
            <div className="max-h-[calc(88vh-86px)] overflow-auto p-5">
              <StructuredReportView report={openReport.summary.structured_report} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
