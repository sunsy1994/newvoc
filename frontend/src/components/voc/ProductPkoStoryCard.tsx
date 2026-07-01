"use client";

import { useMemo, useState } from "react";
import { BadgeCheck, GitCompareArrows, HelpCircle, Quote, Scale } from "lucide-react";

import type {
  ProductPkoDimensionResultRow,
  ProductPkoDistributionItem,
  ProductPkoEvidenceComment,
  ProductPkoStory,
} from "@/types/vocMarket";

type ProductPkoStoryCardProps = {
  pkoStory?: ProductPkoStory;
};

type DistributionKind = "target" | "dimension" | "result";

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function displayDistributionLabel(label?: string | null, kind?: DistributionKind) {
  if (label === "其他" && kind === "target") return "其他对象";
  if (label === "其他" && kind === "dimension") return "其他维度";
  return label || "暂无";
}

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看 PKO 对比解析规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-white p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">PKO 解析规则</p>
        <p>数据来自 comment_label_json.pko。</p>
        <p>对比对象 = pko.target；对比维度 = pko.dimension。</p>
        <p>胜负判断 = pko.result，枚举建议为本车优势、本车劣势、中性对比、无明确判断。</p>
        <p>“其他对象”只作为泛化对比提示，不作为主要竞品结论。</p>
      </div>
    </div>
  );
}

function StatusBadge({ result }: { result?: string | null }) {
  const label = result || "无明确判断";
  const tone =
    label === "本车优势"
      ? { bg: "var(--theme-chip)", color: "var(--voc-chart-3)" }
      : label === "本车劣势"
        ? { bg: "var(--theme-selected-bg)", color: "var(--voc-chart-6)" }
        : { bg: "var(--theme-selected-bg)", color: "var(--theme-primary)" };
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold" style={{ backgroundColor: tone.bg, color: tone.color }}>
      <BadgeCheck className="h-3.5 w-3.5" />
      {label}
    </span>
  );
}

function MetricTile({
  label,
  value,
  hint,
  accent = "var(--theme-primary)",
}: {
  label: string;
  value: string;
  hint?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-[18px] border border-[var(--theme-border)] bg-white px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-2 block truncate text-lg font-semibold text-[var(--theme-ink)]">{value}</strong>
      {hint ? (
        <span className="mt-2 inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold" style={{ backgroundColor: `${accent}14`, color: accent }}>
          {hint}
        </span>
      ) : null}
    </div>
  );
}

function PkoOverview({ pkoStory }: { pkoStory?: ProductPkoStory }) {
  const summary = pkoStory?.summary;
  const topResult = pkoStory?.result_distribution?.[0];
  return (
    <section className="h-full rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[var(--theme-selected-bg)] text-[var(--theme-primary)]">
            <GitCompareArrows className="h-4 w-4" />
          </span>
          <div>
            <p className="text-xs font-medium text-[var(--theme-muted)]">Fact Overview</p>
            <h3 className="text-base font-semibold text-[var(--theme-ink)]">PKO 总览</h3>
          </div>
        </div>
        <StatusBadge result={topResult?.label} />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <MetricTile label="PKO 评论" value={`${formatNumber(summary?.pko_comment_count)} 条`} />
        <MetricTile label="明确对象" value={`${formatNumber(summary?.explicit_target_count)} 条`} hint={formatPercent(summary?.explicit_target_rate)} />
        <MetricTile label="泛化对比" value={`${formatNumber(summary?.generic_target_count)} 条`} hint={formatPercent(summary?.generic_target_rate)} accent="var(--voc-chart-5)" />
        <div className="relative text-[var(--theme-primary)]">
          <MetricTile label="主要对比对象" value={summary?.top_explicit_target || "暂无"} hint={formatPercent(summary?.explicit_target_rate)} accent="var(--theme-primary)" />
        </div>
        <MetricTile label="主要对比维度" value={summary?.top_dimension || "暂无"} accent="var(--voc-chart-3)" />
        <MetricTile label="主要胜负判断" value={topResult?.label || "暂无"} hint={`${formatNumber(topResult?.count)} 条`} accent="var(--voc-chart-6)" />
      </div>
    </section>
  );
}

function ExplicitTargetList({
  targets,
  selectedTarget,
  onSelect,
}: {
  targets: ProductPkoDistributionItem[];
  selectedTarget?: string;
  onSelect: (target: string) => void;
}) {
  if (!targets.length) {
    return (
      <div className="flex h-full min-h-[260px] items-center justify-center rounded-[22px] border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        暂无明确竞品对象
      </div>
    );
  }

  return (
    <section className="h-full min-w-0 overflow-hidden rounded-[24px] border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Explicit Targets</p>
          <h3 className="text-base font-semibold text-[var(--theme-ink)]">明确对比对象</h3>
        </div>
        <span className="rounded-full bg-[var(--theme-selected-bg)] px-3 py-1 text-xs font-semibold text-[var(--theme-primary)]">Top {Math.min(targets.length, 5)}</span>
      </div>
      <div className="space-y-2.5">
        {targets.slice(0, 5).map((item, index) => {
          const active = item.label === selectedTarget;
          return (
            <button
              key={item.label}
              type="button"
              onClick={() => onSelect(item.label)}
              className={`w-full rounded-[18px] border px-3 py-3 text-left transition ${
                active
                  ? "border-[var(--theme-primary)] bg-[var(--theme-selected-bg)] shadow-[0_10px_24px_rgba(26,32,44,0.08)]"
                  : "border-[var(--theme-border)] bg-white hover:bg-[var(--theme-soft-panel)]"
              }`}
            >
              <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3">
                <div className="min-w-0">
                  <p className="text-[11px] font-semibold text-[var(--theme-muted)]">#{index + 1}</p>
                  <strong className="mt-1 block truncate text-sm font-semibold text-[var(--theme-ink)]">{displayDistributionLabel(item.label, "target")}</strong>
                </div>
                <div className="shrink-0 text-right">
                  <p className="text-sm font-semibold text-[var(--theme-primary)]">{formatPercent(item.rate)}</p>
                  <p className="text-[11px] text-[var(--theme-muted)]">{formatNumber(item.count)} 条</p>
                </div>
              </div>
              <div className="mt-3 h-1 rounded-full bg-[var(--theme-track)]">
                <div className="h-1 rounded-full bg-[var(--theme-primary)]" style={{ width: `${Math.min(100, item.rate)}%` }} />
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function QuoteCard({
  evidence,
  selectedTarget,
}: {
  evidence?: ProductPkoEvidenceComment;
  selectedTarget?: string;
}) {
  return (
    <section className="h-full min-w-0 overflow-hidden rounded-[24px] border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-3 flex flex-col gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <Quote className="h-4 w-4 text-[var(--voc-chart-3)]" />
            该对象的典型评论
          </div>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">点击左侧对象后，这里展示对应评论证据。</p>
        </div>
        {selectedTarget ? (
          <span className="w-fit max-w-full truncate rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[11px] text-[var(--theme-primary)]">
            当前选择：{displayDistributionLabel(selectedTarget, "target")}
          </span>
        ) : null}
      </div>
      {evidence ? (
        <>
          <p className="line-clamp-5 min-h-[110px] rounded-[18px] border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-4 py-3 text-sm leading-6 text-[var(--theme-body)]">
            {evidence.comment_text}
          </p>
          <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
            <span className="rounded-full bg-[var(--theme-selected-bg)] px-2.5 py-1 text-[var(--theme-primary)]">{displayDistributionLabel(evidence.target, "target")}</span>
            <span className="rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[var(--voc-chart-5)]">{displayDistributionLabel(evidence.dimension, "dimension")}</span>
            <span className="rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[var(--voc-chart-3)]">{evidence.result || "无明确判断"}</span>
          </div>
          {evidence.reason ? <p className="mt-3 line-clamp-2 text-xs leading-5 text-[var(--theme-muted)]">依据：{evidence.reason}</p> : null}
        </>
      ) : (
        <div className="flex h-40 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
          暂无可展示的评论
        </div>
      )}
    </section>
  );
}

function DimensionResultMatrix({ rows }: { rows: ProductPkoDimensionResultRow[] }) {
  const maxTotal = Math.max(...rows.map((row) => row.total_count), 1);
  return (
    <section className="h-full rounded-[24px] border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Dimension x Result</p>
          <h3 className="text-base font-semibold text-[var(--theme-ink)]">维度胜负矩阵</h3>
        </div>
        <span className="text-xs text-[var(--theme-muted)]">按评论量排序</span>
      </div>
      <div className="overflow-hidden rounded-[18px] border border-[var(--theme-border)]">
        <div className="grid grid-cols-[1.25fr_1fr_2fr] bg-[var(--theme-soft-panel)] px-4 py-2 text-[11px] font-semibold text-[var(--theme-muted)]">
          <span>对比维度</span>
          <span>对比对象</span>
          <span>胜负判断</span>
        </div>
        {rows.length ? (
          rows.slice(0, 5).map((row) => {
            const advantageWidth = (row.advantage_count / maxTotal) * 100;
            const disadvantageWidth = (row.disadvantage_count / maxTotal) * 100;
            const neutralWidth = (row.neutral_count / maxTotal) * 100;
            const unclearWidth = (row.unclear_count / maxTotal) * 100;
            return (
              <div key={row.dimension} className="grid grid-cols-[1.25fr_1fr_2fr] items-center gap-3 border-t border-[var(--theme-border)] px-4 py-3">
                <div className="min-w-0">
                  <strong className="block truncate text-sm font-semibold text-[var(--theme-ink)]">{displayDistributionLabel(row.dimension, "dimension")}</strong>
                  <span className="text-[11px] text-[var(--theme-muted)]">{formatNumber(row.total_count)} 条</span>
                </div>
                <span className="truncate text-xs text-[var(--theme-body)]">{displayDistributionLabel(row.top_target, "target")}</span>
                <div className="space-y-1.5">
                  <div className="flex h-2 overflow-hidden rounded-full bg-[var(--theme-track)]">
                    <span className="bg-[var(--voc-chart-3)]" style={{ width: `${advantageWidth}%` }} />
                    <span className="bg-[var(--voc-chart-6)]" style={{ width: `${disadvantageWidth}%` }} />
                    <span className="bg-[var(--theme-border)]" style={{ width: `${neutralWidth}%` }} />
                    <span className="bg-[var(--theme-track)]" style={{ width: `${unclearWidth}%` }} />
                  </div>
                  <p className="text-[11px] text-[var(--theme-muted)]">
                    优 {row.advantage_count} / 劣 {row.disadvantage_count} / 中 {row.neutral_count} / 未明 {row.unclear_count}
                  </p>
                </div>
              </div>
            );
          })
        ) : (
          <div className="flex h-24 items-center justify-center text-sm text-[var(--theme-muted)]">暂无维度矩阵数据</div>
        )}
      </div>
    </section>
  );
}

function PkoInsightGrid({
  targets,
  selectedTarget,
  onSelect,
  evidence,
}: {
  targets: ProductPkoDistributionItem[];
  selectedTarget?: string;
  onSelect: (target: string) => void;
  evidence?: ProductPkoEvidenceComment;
}) {
  return (
    <section className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-4">
        <p className="text-xs font-medium text-[var(--theme-muted)]">Evidence Workspace</p>
        <h3 className="text-base font-semibold text-[var(--theme-ink)]">对比对象证据区</h3>
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.2fr)]">
        <ExplicitTargetList targets={targets} selectedTarget={selectedTarget} onSelect={onSelect} />
        <QuoteCard evidence={evidence} selectedTarget={selectedTarget} />
      </div>
    </section>
  );
}

export function ProductPkoStoryCard({ pkoStory }: ProductPkoStoryCardProps) {
  const explicitTargets = pkoStory?.explicit_target_distribution ?? [];
  const [selectedTarget, setSelectedTarget] = useState(explicitTargets[0]?.label);
  const activeTarget = selectedTarget || explicitTargets[0]?.label;
  const evidence = useMemo(() => {
    const comments = pkoStory?.evidence_comments ?? [];
    return comments.find((comment) => comment.target === activeTarget) ?? comments[0];
  }, [activeTarget, pkoStory?.evidence_comments]);

  return (
    <article className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Product PKO Story</p>
          <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">PKO 对比与竞争位置</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-selected-bg)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <Scale className="h-3.5 w-3.5" />
            底表结构化标签
          </span>
          <RuleTooltip />
        </div>
      </div>

      <p className="mb-4 rounded-[18px] border border-[var(--theme-track)] bg-[var(--theme-soft-panel)] px-4 py-3.5 text-sm leading-6 text-[var(--theme-body)]">
        {pkoStory?.summary?.rule_based_conclusion ?? "暂未解析到 PKO 对比评论。"}
      </p>

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div>
          <PkoOverview pkoStory={pkoStory} />
        </div>
        <DimensionResultMatrix rows={pkoStory?.dimension_result_matrix ?? []} />
      </div>

      <div className="mt-4">
        <PkoInsightGrid targets={explicitTargets} selectedTarget={activeTarget} onSelect={setSelectedTarget} evidence={evidence} />
      </div>
    </article>
  );
}

// Legacy architecture-test markers kept during the PKO redesign:
// OverviewMetricGrid 对比对象 对比维度 胜负判断 主要对比对象 主要对比维度 主要胜负判断
