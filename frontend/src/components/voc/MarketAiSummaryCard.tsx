"use client";

import { Bot, Check, Clipboard, Loader2, Sparkles, X } from "lucide-react";
import { useState } from "react";

import { apiBaseUrl } from "@/config/navigation";
import type { MarketReportAgentPayload, MarketReportSummary } from "@/types/vocMarket";

type MarketAiSummaryCardProps = {
  eventId: string;
};

const emptySummary: MarketReportSummary = {
  event_overview: "",
  scale_summary: "",
  topic_summary: "",
  kol_summary: "",
  audience_summary: "",
  feedback_summary: "",
  market_conclusion: "",
  data_limits: "",
};

const storySections: Array<{ key: keyof MarketReportSummary; title: string }> = [
  { key: "event_overview", title: "事件概况" },
  { key: "scale_summary", title: "传播规模" },
  { key: "topic_summary", title: "热门话题" },
  { key: "kol_summary", title: "KOL 与作者" },
  { key: "audience_summary", title: "受众画像" },
  { key: "feedback_summary", title: "用户反馈质量" },
  { key: "market_conclusion", title: "市场部结论" },
];

function buildRunUrl(eventId: string) {
  return `${apiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/market/report-agent/run`;
}

function formatSummary(summary: MarketReportSummary) {
  return storySections
    .map((section) => `${section.title}：${summary[section.key]}`)
    .concat(summary.data_limits ? [`数据限制：${summary.data_limits}`] : [])
    .filter((line) => !line.endsWith("："))
    .join("\n");
}

function StorySection({ title, value, wide = false }: { title: string; value: string; wide?: boolean }) {
  return (
    <section className={`rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-card)] p-4 ${wide ? "md:col-span-2" : ""}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--theme-muted)]">{title}</p>
      <p className="mt-2 text-sm leading-6 text-[var(--theme-body)]">{value || "本次生成未返回该部分内容。"}</p>
    </section>
  );
}

function DetailsBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
      <summary className="cursor-pointer text-sm font-semibold text-[var(--theme-ink)]">{title}</summary>
      <div className="mt-3 max-h-72 overflow-auto rounded-xl bg-[var(--theme-white)] p-3 text-xs leading-5 text-[var(--theme-body)]">
        {children}
      </div>
    </details>
  );
}

export function MarketAiSummaryCard({ eventId }: MarketAiSummaryCardProps) {
  const [payload, setPayload] = useState<MarketReportAgentPayload | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const summary = payload?.summary ?? emptySummary;

  async function runSummary() {
    setIsOpen(true);
    setIsLoading(true);
    setError("");
    setCopied(false);
    try {
      const response = await fetch(buildRunUrl(eventId), { method: "POST" });
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(detail?.detail ?? `AI 总结生成失败：${response.status}`);
      }
      setPayload((await response.json()) as MarketReportAgentPayload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "AI 总结生成失败，请稍后重试。");
    } finally {
      setIsLoading(false);
    }
  }

  async function copySummary() {
    if (!payload?.summary) return;
    await navigator.clipboard.writeText(formatSummary(payload.summary));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <>
      <div className="flex justify-end">
        <button
          type="button"
          onClick={runSummary}
          className="inline-flex h-10 items-center gap-2 rounded-xl bg-[var(--theme-primary)] px-4 text-sm font-semibold text-white shadow-[0_10px_24px_rgba(26,32,44,0.12)] transition hover:opacity-90"
        >
          <Sparkles className="h-4 w-4" />
          AI 总结
        </button>
      </div>

      {isOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/18 p-4 backdrop-blur-sm">
          <div className="max-h-[88vh] w-full max-w-5xl overflow-hidden rounded-[28px] border border-[var(--theme-border)] bg-[var(--theme-white)] shadow-[0_24px_80px_rgba(26,32,44,0.2)]">
            <header className="flex items-start justify-between gap-4 border-b border-[var(--theme-border)] bg-[linear-gradient(135deg,var(--theme-selected-bg),var(--theme-card))] p-5">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--theme-primary)] text-white">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--theme-muted)]">Market Report Agent</p>
                  <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">AI 市场总结故事卡</h2>
                  <p className="mt-1 text-sm text-[var(--theme-body)]">基于当前事件市场看板数据生成，支持查看 Prompt 与输入数据。</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)] transition hover:bg-[var(--theme-hover-bg)]"
                aria-label="关闭"
              >
                <X className="h-4 w-4" />
              </button>
            </header>

            <div className="max-h-[calc(88vh-92px)] overflow-auto p-5">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="text-xs text-[var(--theme-muted)]">
                  {payload?.prompt_version ? <span>Prompt：{payload.prompt_version}</span> : <span>等待生成</span>}
                  {payload?.generated_at ? <span className="ml-3">生成时间：{payload.generated_at}</span> : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={runSummary}
                    disabled={isLoading}
                    className="inline-flex h-9 items-center gap-2 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-xs font-semibold text-[var(--theme-body)] transition hover:bg-[var(--theme-hover-bg)] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                    {isLoading ? "生成中" : payload ? "重新生成" : "生成"}
                  </button>
                  <button
                    type="button"
                    onClick={copySummary}
                    disabled={!payload}
                    className="inline-flex h-9 items-center gap-2 rounded-xl bg-[var(--theme-primary)] px-3 text-xs font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Clipboard className="h-4 w-4" />}
                    {copied ? "已复制" : "复制摘要"}
                  </button>
                </div>
              </div>

              {error ? <p className="mb-4 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2 text-xs text-[var(--theme-negative)]">{error}</p> : null}

              <div className="grid gap-3 md:grid-cols-2">
                {storySections.map((section) => (
                  <StorySection key={section.key} title={section.title} value={summary[section.key]} wide={section.key === "market_conclusion"} />
                ))}
                {summary.data_limits ? <StorySection title="数据限制" value={summary.data_limits} wide /> : null}
              </div>

              <div className="mt-4 grid gap-3 lg:grid-cols-2">
                <DetailsBlock title="使用的 Prompt">
                  <pre className="whitespace-pre-wrap break-words">{payload?.rendered_prompt || "生成后展示完整 Prompt。"}</pre>
                </DetailsBlock>
                <DetailsBlock title="输入给 AI 的结构化数据">
                  <pre className="whitespace-pre-wrap break-words">{payload?.context ? JSON.stringify(payload.context, null, 2) : "生成后展示本次输入数据。"}</pre>
                </DetailsBlock>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
