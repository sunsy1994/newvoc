"use client";

import { Bot, Check, Clipboard, Loader2, Sparkles, X } from "lucide-react";
import { Fragment, useState } from "react";

import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { apiBaseUrl } from "@/config/navigation";
import type { ReportAgentPayload, ReportChartSpec, StructuredReport, StructuredReportTemplateSection } from "@/types/vocMarket";

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
type ReportViewMode = "dashboard" | "report";

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

function formatCell(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function renderChart(chart: ReportChartSpec) {
  if (chart.chart_type === "metric_cards") {
    return (
      <div key={chart.chart_id} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
        <p className="text-sm font-semibold text-[var(--theme-ink)]">{chart.title}</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {chart.data.map((item, index) => (
            <div key={`${chart.chart_id}-${index}`} className="rounded-xl bg-[var(--theme-soft-panel)] p-3">
              <p className="text-xs text-[var(--theme-muted)]">{formatCell(item.label)}</p>
              <p className="mt-1 text-xl font-semibold text-[var(--theme-ink)]">{formatCell(item.value)}</p>
              <p className="mt-1 text-[11px] leading-4 text-[var(--theme-muted)]">{formatCell(item.method)}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }
  if (chart.chart_type === "bar") {
    const yField = chart.y_field ?? "value";
    const maxValue = Math.max(1, ...chart.data.map((item) => Number(item[yField]) || 0));
    return (
      <div key={chart.chart_id} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
        <p className="text-sm font-semibold text-[var(--theme-ink)]">{chart.title}</p>
        <div className="mt-3 space-y-2">
          {chart.data.map((item, index) => {
            const value = Number(item[yField]) || 0;
            return (
              <div key={`${chart.chart_id}-${index}`} className="grid grid-cols-[72px_1fr_48px] items-center gap-2 text-xs">
                <span className="truncate text-[var(--theme-body)]">{formatCell(item[chart.x_field ?? "label"])}</span>
                <span className="h-2 overflow-hidden rounded-full bg-[var(--theme-soft-panel)]">
                  <span className="block h-full rounded-full bg-[var(--theme-primary)]" style={{ width: `${Math.max(6, (value / maxValue) * 100)}%` }} />
                </span>
                <span className="text-right font-semibold text-[var(--theme-ink)]">{value}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }
  if (chart.chart_type === "trend") {
    const hasDailyBars = chart.data.some((item) => "content_count" in item || "comment_count" in item);
    if (hasDailyBars) {
      const maxValue = Math.max(1, ...chart.data.flatMap((item) => [Number(item.content_count) || 0, Number(item.comment_count) || 0]));
      return (
        <div key={chart.chart_id} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <p className="text-sm font-semibold text-[var(--theme-ink)]">{chart.title}</p>
            <div className="flex items-center gap-3 text-[11px] text-[var(--theme-muted)]">
              <span className="inline-flex items-center gap-1"><i className="h-2 w-2 rounded-sm bg-[var(--theme-primary)]" />内容</span>
              <span className="inline-flex items-center gap-1"><i className="h-2 w-2 rounded-sm bg-[var(--theme-selected-text)]" />评论</span>
            </div>
          </div>
          <div className="mt-4 flex min-h-[180px] items-end gap-3 overflow-x-auto pb-2">
            {chart.data.map((item, index) => {
              const contentCount = Number(item.content_count) || 0;
              const commentCount = Number(item.comment_count) || 0;
              return (
                <div key={`${chart.chart_id}-${index}`} className="flex min-w-[54px] flex-1 flex-col items-center gap-2">
                  <div className="flex h-32 items-end gap-1.5">
                    <span
                      title={`内容：${contentCount}`}
                      className="w-3 rounded-t-md bg-[var(--theme-primary)]"
                      style={{ height: `${Math.max(4, (contentCount / maxValue) * 128)}px` }}
                    />
                    <span
                      title={`评论：${commentCount}`}
                      className="w-3 rounded-t-md bg-[var(--theme-selected-text)]"
                      style={{ height: `${Math.max(4, (commentCount / maxValue) * 128)}px` }}
                    />
                  </div>
                  <span className="max-w-[64px] truncate text-[10px] text-[var(--theme-muted)]">{formatCell(item[chart.x_field ?? "date"])}</span>
                </div>
              );
            })}
          </div>
          {chart.note ? <p className="mt-2 text-xs leading-5 text-[var(--theme-muted)]">{chart.note}</p> : null}
        </div>
      );
    }
    return (
      <div key={chart.chart_id} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
        <p className="text-sm font-semibold text-[var(--theme-ink)]">{chart.title}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {chart.data.map((item, index) => (
            <span key={`${chart.chart_id}-${index}`} className="rounded-full bg-[var(--theme-soft-panel)] px-3 py-1 text-xs text-[var(--theme-body)]">
              {formatCell(item.label ?? item.date)}：{formatCell(item.volume)}
            </span>
          ))}
        </div>
        {chart.note ? <p className="mt-3 text-xs leading-5 text-[var(--theme-muted)]">{chart.note}</p> : null}
      </div>
    );
  }
  return (
    <div key={chart.chart_id} className="overflow-hidden rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)]">
      <p className="border-b border-[var(--theme-border)] px-4 py-3 text-sm font-semibold text-[var(--theme-ink)]">{chart.title}</p>
      <table className="w-full text-left text-xs">
        <tbody className="divide-y divide-[var(--theme-border)]">
          {chart.data.map((item, index) => (
            <tr key={`${chart.chart_id}-${index}`}>
              {(chart.columns ?? Object.keys(item)).map((column) => (
                <td key={column} className="px-4 py-3 align-top leading-5 text-[var(--theme-body)]">
                  {formatCell(item[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const templateToneStyles: Record<StructuredReportTemplateSection["tone"], { label: string; shell: string; chip: string; card: string; accent: string }> = {
  red: {
    label: "bg-[#b84545] text-white",
    shell: "bg-[#fff4f4] border-[#f3d7d7]",
    chip: "bg-[#ffe8e8] text-[#a43b3b]",
    card: "bg-white border-[#f0d7d7]",
    accent: "bg-[#d75a5a]",
  },
  green: {
    label: "bg-[#4f9b42] text-white",
    shell: "bg-[#f4fbf0] border-[#dcefd5]",
    chip: "bg-[#e8f7e0] text-[#427b32]",
    card: "bg-white border-[#d8ead0]",
    accent: "bg-[#68af55]",
  },
  brown: {
    label: "bg-[#9a7246] text-white",
    shell: "bg-[#fbf7f0] border-[#eadfce]",
    chip: "bg-[#f3eadc] text-[#795631]",
    card: "bg-white border-[#e8dac5]",
    accent: "bg-[#b58a55]",
  },
  blue: {
    label: "bg-[#3d7b9f] text-white",
    shell: "bg-[#f0f8fb] border-[#d4e8f0]",
    chip: "bg-[#e1f2f8] text-[#2d6d91]",
    card: "bg-white border-[#cfdee7]",
    accent: "bg-[#4f9ec5]",
  },
};

function renderTemplateSection(section: StructuredReportTemplateSection) {
  const tone = templateToneStyles[section.tone] ?? templateToneStyles.blue;
  return (
    <section key={`${section.code}-${section.title}`} className="space-y-3">
      <div className="flex items-center gap-2">
        <span className={`rounded-sm px-2.5 py-1 text-xs font-bold tracking-wide ${tone.label}`}>
          {section.code} / {section.title}
        </span>
        {section.subtitle ? <span className="text-xs text-[var(--theme-muted)]">{section.subtitle}</span> : null}
      </div>
      <div className={`rounded-2xl border p-4 ${tone.shell}`}>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {section.cards.map((card) => (
            <article key={`${section.code}-${card.title}`} className={`relative overflow-hidden rounded-xl border p-4 shadow-[0_10px_24px_rgba(26,32,44,0.05)] ${tone.card}`}>
              <span className={`absolute left-0 top-4 h-10 w-1 rounded-r-full ${tone.accent}`} />
              <div className="flex items-start justify-between gap-3">
                <h3 className="pl-2 text-sm font-semibold text-[var(--theme-ink)]">{card.title}</h3>
                {card.badge ? <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${tone.chip}`}>{card.badge}</span> : null}
              </div>
              <p className="mt-3 min-h-[44px] text-sm leading-6 text-[var(--theme-body)]">{card.body}</p>
              {card.bullets.length ? (
                <ul className="mt-3 space-y-1 rounded-lg bg-[rgba(248,250,252,0.78)] p-3">
                  {card.bullets.map((bullet) => (
                    <li key={`${card.title}-${bullet}`} className="flex gap-2 text-xs leading-5 text-[var(--theme-body)]">
                      <span className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${tone.accent}`} />
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export function StructuredReportView({ report }: { report: StructuredReport }) {
  const [reportViewMode, setReportViewMode] = useState<ReportViewMode>("dashboard");
  const templateSections = report.template_sections?.length
    ? report.template_sections
    : [
        {
          code: "01",
          title: "核心结论",
          subtitle: "兼容旧报告结构生成的摘要区",
          tone: "red" as const,
          cards: [
            {
              title: "执行摘要",
              badge: "摘要",
              body: report.executive_summary[0] || "当前数据不足以生成执行摘要。",
              bullets: report.executive_summary.slice(1, 4),
            },
            {
              title: "判断补充",
              badge: "判断",
              body: report.recommendations[0] || "当前报告按固定模板展示事件判断。",
              bullets: report.recommendations.slice(1, 4),
            },
          ],
        },
      ];
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-[var(--theme-border)] bg-[linear-gradient(135deg,#ffffff,#f7fbfb)] p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--theme-primary)]">Event Report</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--theme-ink)]">{report.title}</h1>
            <p className="mt-2 text-sm text-[var(--theme-muted)]">
              {reportViewMode === "dashboard"
                ? "看板模式：优先展示事件总判断、市场传播判断、产品机会与风险、销售转化判断和业务口径。"
                : "报告模式：展开图表、证据引用和数据计算方式。"}
            </p>
          </div>
          <div className="inline-flex rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-1 text-xs font-semibold shadow-[0_8px_18px_rgba(26,32,44,0.06)]">
            <button
              type="button"
              onClick={() => setReportViewMode("dashboard")}
              className={`rounded-lg px-3 py-1.5 transition ${reportViewMode === "dashboard" ? "bg-[var(--theme-primary)] text-white" : "text-[var(--theme-body)] hover:bg-[var(--theme-hover-bg)]"}`}
            >
              看板模式
            </button>
            <button
              type="button"
              onClick={() => setReportViewMode("report")}
              className={`rounded-lg px-3 py-1.5 transition ${reportViewMode === "report" ? "bg-[var(--theme-primary)] text-white" : "text-[var(--theme-body)] hover:bg-[var(--theme-hover-bg)]"}`}
            >
              报告模式
            </button>
          </div>
        </div>
      </div>
      {reportViewMode === "dashboard" ? (
        <div className="space-y-5">{templateSections.map(renderTemplateSection)}</div>
      ) : null}
      {reportViewMode === "report" ? (
        <div className="space-y-4">
          <div className="grid gap-3 lg:grid-cols-2">{report.charts.map(renderChart)}</div>
          <section className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
            <p className="text-sm font-semibold text-[var(--theme-ink)]">证据引用</p>
            <div className="mt-2 space-y-2">
              {report.evidence_references.map((item, index) => (
                <p key={`${item.source_path}-${index}`} className="text-xs leading-5 text-[var(--theme-body)]">
                  - {item.source}：{item.quote}
                </p>
              ))}
            </div>
          </section>
          <section className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
            <p className="text-sm font-semibold text-[var(--theme-ink)]">数据计算方式</p>
            <div className="mt-2 space-y-2">
              {report.calculation_notes.map((item) => (
                <p key={item.metric} className="text-xs leading-5 text-[var(--theme-body)]">- {item.metric}：{item.method}</p>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </div>
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
  const structuredReport = payload?.summary.structured_report;
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
        <HoverBorderGradient
          as="button"
          onClick={openSummary}
          duration={1.4}
          containerClassName="rounded-xl shadow-[0_8px_20px_rgba(26,32,44,0.08)] hover:shadow-[0_12px_26px_rgba(26,32,44,0.12)]"
          className="inline-flex h-9 items-center gap-2 px-3.5 py-0 text-sm font-semibold transition-colors hover:bg-[var(--theme-hover-bg)]"
        >
          <Sparkles className="h-4 w-4 text-[var(--theme-primary)]" />
          <span>AI 总结</span>
        </HoverBorderGradient>
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
                ) : structuredReport ? (
                  <StructuredReportView report={structuredReport} />
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
