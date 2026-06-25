"use client";

import { Bot, Check, Clipboard, Loader2, Sparkles, X } from "lucide-react";
import { Fragment, useState } from "react";

import { apiBaseUrl } from "@/config/navigation";
import type { ReportAgentPayload } from "@/types/vocMarket";

type ReportAiSummaryCardProps = {
  eventId: string;
  departmentName: string;
  agentLabel: string;
  reportTitle: string;
  emptyText: string;
  latestPath: string;
  runPath: string;
};

type LoadingMode = "latest" | "generate" | "";

function buildUrl(path: string, eventId: string) {
  return `${apiBaseUrl}${path.replace("{eventId}", encodeURIComponent(eventId))}`;
}

function stripMarkdownFence(markdown: string) {
  const trimmed = markdown.trim();
  const fenced = trimmed.match(/^```(?:markdown|md)?\s*([\s\S]*?)\s*```$/i);
  return fenced ? fenced[1].trim() : markdown;
}

function renderInlineMarkdown(text: string) {
  const segments = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).filter(Boolean);
  return segments.map((segment, index) => {
    if (segment.startsWith("**") && segment.endsWith("**")) {
      return (
        <strong key={`${index}-${segment}`} className="font-semibold text-[var(--theme-ink)]">
          {segment.slice(2, -2)}
        </strong>
      );
    }
    if (segment.startsWith("`") && segment.endsWith("`")) {
      return (
        <code key={`${index}-${segment}`} className="rounded-md bg-[var(--theme-soft-panel)] px-1.5 py-0.5 text-xs text-[var(--theme-primary)]">
          {segment.slice(1, -1)}
        </code>
      );
    }
    return <Fragment key={`${index}-${segment}`}>{segment}</Fragment>;
  });
}

function renderMarkdownReport(markdown: string) {
  const lines = stripMarkdownFence(markdown).split(/\r?\n/);
  return lines.map((rawLine, index) => {
    const line = rawLine.trim();
    const key = `${index}-${line}`;
    if (!line) return <div key={key} className="h-3" />;
    if (/^---+$/.test(line)) return <hr key={key} className="my-5 border-[var(--theme-border)]" />;
    if (line.startsWith("# ")) {
      return (
        <h1 key={key} className="mb-3 text-2xl font-semibold tracking-tight text-[var(--theme-ink)]">
          {renderInlineMarkdown(line.slice(2))}
        </h1>
      );
    }
    if (line.startsWith("## ")) {
      return (
        <h2 key={key} className="mt-7 border-t border-[var(--theme-border)] pt-5 text-base font-semibold text-[var(--theme-ink)]">
          {renderInlineMarkdown(line.slice(3))}
        </h2>
      );
    }
    if (line.startsWith("### ")) {
      return (
        <h3 key={key} className="mt-5 text-sm font-semibold text-[var(--theme-ink)]">
          {renderInlineMarkdown(line.slice(4))}
        </h3>
      );
    }
    if (line.startsWith("> ")) {
      return (
        <blockquote key={key} className="my-3 rounded-2xl border-l-4 border-[var(--theme-primary)] bg-[var(--theme-soft-panel)] px-4 py-3 text-sm leading-7 text-[var(--theme-body)]">
          {renderInlineMarkdown(line.slice(2))}
        </blockquote>
      );
    }
    if (line.startsWith("- ") || line.startsWith("* ")) {
      return (
        <div key={key} className="ml-1 flex gap-3 text-sm leading-7 text-[var(--theme-body)]">
          <span className="mt-[11px] h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--theme-primary)]" />
          <span>{renderInlineMarkdown(line.slice(2))}</span>
        </div>
      );
    }
    const numbered = line.match(/^(\d+)\.\s+(.*)$/);
    if (numbered) {
      return (
        <div key={key} className="flex gap-2 text-sm leading-7 text-[var(--theme-body)]">
          <span className="font-semibold text-[var(--theme-primary)]">{numbered[1]}.</span>
          <span>{renderInlineMarkdown(numbered[2])}</span>
        </div>
      );
    }
    return (
      <p key={key} className="text-sm leading-7 text-[var(--theme-body)]">
        {renderInlineMarkdown(line)}
      </p>
    );
  });
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

export function ReportAiSummaryCard({
  eventId,
  departmentName,
  agentLabel,
  reportTitle,
  emptyText,
  latestPath,
  runPath,
}: ReportAiSummaryCardProps) {
  const [payload, setPayload] = useState<ReportAgentPayload | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [hasCheckedLatest, setHasCheckedLatest] = useState(false);
  const [loadingMode, setLoadingMode] = useState<LoadingMode>("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const reportMarkdown = payload?.summary.report_markdown ?? "";
  const dataNotes = payload?.summary.data_notes ?? [];
  const isLoading = Boolean(loadingMode);

  async function loadLatestSummary() {
    setLoadingMode("latest");
    setError("");
    try {
      const response = await fetch(buildUrl(latestPath, eventId));
      if (response.status === 404) {
        setPayload(null);
        await regenerateSummary();
        return;
      }
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(detail?.detail ?? `读取历史 AI 总结失败：${response.status}`);
      }
      setPayload((await response.json()) as ReportAgentPayload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "读取历史 AI 总结失败，请稍后重试。");
    } finally {
      setHasCheckedLatest(true);
      setLoadingMode("");
    }
  }

  async function openSummary() {
    setIsOpen(true);
    setCopied(false);
    if (!hasCheckedLatest && !payload) {
      await loadLatestSummary();
    }
  }

  async function regenerateSummary() {
    setIsOpen(true);
    setLoadingMode("generate");
    setError("");
    setCopied(false);
    try {
      const response = await fetch(buildUrl(runPath, eventId), { method: "POST" });
      if (!response.ok) {
        const detail = (await response.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(detail?.detail ?? `AI 总结生成失败：${response.status}`);
      }
      setPayload((await response.json()) as ReportAgentPayload);
      setHasCheckedLatest(true);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "AI 总结生成失败，请稍后重试。");
    } finally {
      setLoadingMode("");
    }
  }

  async function copySummary() {
    if (!reportMarkdown) return;
    const notesText = dataNotes.length ? `\n\n数据说明：\n${dataNotes.map((note) => `- ${note}`).join("\n")}` : "";
    await navigator.clipboard.writeText(`${reportMarkdown}${notesText}`);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <>
      <div className="flex justify-end">
        <button
          type="button"
          onClick={openSummary}
          className="group relative inline-flex h-10 items-center gap-2 overflow-hidden rounded-xl bg-[linear-gradient(135deg,var(--theme-primary),var(--theme-selected-text),var(--theme-status-text))] px-4 text-sm font-semibold text-white shadow-[0_12px_26px_rgba(26,32,44,0.14)] transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_16px_34px_rgba(26,32,44,0.18)]"
        >
          <span className="absolute inset-y-0 -left-10 w-8 rotate-12 bg-white/30 blur-md transition-transform duration-700 group-hover:translate-x-40" />
          <Sparkles className="relative h-4 w-4" />
          <span className="relative">AI 总结</span>
        </button>
      </div>

      {isOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/18 p-4 backdrop-blur-sm">
          <div className="max-h-[88vh] w-full max-w-5xl overflow-hidden rounded-[28px] border border-[var(--theme-border)] bg-[var(--theme-white)] shadow-[0_24px_80px_rgba(26,32,44,0.2)]">
            <header className="flex items-start justify-between gap-4 border-b border-[var(--theme-border)] bg-[linear-gradient(135deg,var(--theme-selected-bg),var(--theme-card))] p-5">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,var(--theme-primary),var(--theme-selected-text))] text-white shadow-[0_12px_26px_rgba(26,32,44,0.12)]">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--theme-muted)]">{agentLabel}</p>
                  <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">{reportTitle}</h2>
                  <p className="mt-1 text-sm text-[var(--theme-body)]">优先展示最近一次生成结果，只有点击重新生成才会再次调用模型。</p>
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
                  {payload?.prompt_version ? <span>Prompt：{payload.prompt_version}</span> : <span>{loadingMode === "latest" ? "正在读取历史总结" : `暂无${departmentName}历史总结`}</span>}
                  {payload?.generated_at ? <span className="ml-3">生成时间：{payload.generated_at}</span> : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={regenerateSummary}
                    disabled={isLoading}
                    className="inline-flex h-9 items-center gap-2 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-xs font-semibold text-[var(--theme-body)] transition hover:bg-[var(--theme-hover-bg)] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loadingMode === "generate" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                    {loadingMode === "generate" ? "生成中" : payload ? "重新生成" : "生成报告"}
                  </button>
                  <button
                    type="button"
                    onClick={copySummary}
                    disabled={!reportMarkdown}
                    className="inline-flex h-9 items-center gap-2 rounded-xl bg-[var(--theme-primary)] px-3 text-xs font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Clipboard className="h-4 w-4" />}
                    {copied ? "已复制" : "复制报告"}
                  </button>
                </div>
              </div>

              {error ? <p className="mb-4 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2 text-xs text-[var(--theme-negative)]">{error}</p> : null}

              <article className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-6 shadow-[0_14px_36px_rgba(26,32,44,0.05)]">
                {loadingMode === "latest" ? (
                  <div className="flex items-center justify-center gap-2 rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-8 text-sm text-[var(--theme-muted)]">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    正在读取最近一次 AI 总结...
                  </div>
                ) : reportMarkdown ? (
                  <div className="space-y-1">{renderMarkdownReport(reportMarkdown)}</div>
                ) : (
                  <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-8 text-center text-sm leading-6 text-[var(--theme-muted)]">
                    {emptyText}
                  </div>
                )}
              </article>

              {dataNotes.length ? (
                <section className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
                  <p className="text-sm font-semibold text-[var(--theme-ink)]">数据说明</p>
                  <div className="mt-2 space-y-1">
                    {dataNotes.map((note, index) => (
                      <Fragment key={`${index}-${note}`}>
                        <p className="text-xs leading-5 text-[var(--theme-body)]">- {note}</p>
                      </Fragment>
                    ))}
                  </div>
                </section>
              ) : null}

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
