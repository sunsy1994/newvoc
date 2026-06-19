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
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#e8ecf3] bg-white text-[#8b92a1] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-primary)]/30"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[#e8ecf3] bg-white p-4 text-xs leading-5 text-[#4a5160] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[#151720]">PKO 解析规则</p>
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
    <div className="rounded-[18px] border border-[#e8ecf3] bg-white px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[#8b92a1]">{label}</p>
      <strong className="mt-2 block truncate text-lg font-semibold text-[#151720]">{value}</strong>
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
    <section className="rounded-[24px] border border-[#e8ecf3] bg-[#f7f9fc] p-4">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[var(--theme-selected-bg)] text-[var(--theme-primary)]">
            <GitCompareArrows className="h-4 w-4" />
          </span>
          <div>
            <p className="text-xs font-medium text-[#8b92a1]">Fact Overview</p>
            <h3 className="text-base font-semibold text-[#151720]">PKO 总览</h3>
          </div>
        </div>
        <StatusBadge result={topResult?.label} />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <MetricTile label="PKO 评论" value={`${formatNumber(summary?.pko_comment_count)} 条`} />
        <MetricTile label="明确对象" value={`${formatNumber(summary?.explicit_target_count)} 条`} hint={formatPercent(summary?.explicit_target_rate)} />
        <MetricTile label="泛化对比" value={`${formatNumber(summary?.generic_target_count)} 条`} hint={formatPercent(summary?.generic_target_rate)} accent="var(--voc-chart-5)" />
        <MetricTile label="明确对象率" value={formatPercent(summary?.explicit_target_rate)} hint={summary?.top_explicit_target || "暂无主对象"} accent="var(--voc-chart-2)" />
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
      <div className="flex h-full min-h-[220px] items-center justify-center rounded-[22px] border border-dashed border-[#d9deea] bg-[#f7f9fc] text-sm text-[#8b92a1]">
        暂无明确竞品对象
      </div>
    );
  }

  return (
    <section className="rounded-[24px] border border-[#e8ecf3] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Explicit Targets</p>
          <h3 className="text-base font-semibold text-[#151720]">明确对比对象</h3>
        </div>
        <span className="rounded-full bg-[var(--theme-selected-bg)] px-3 py-1 text-xs font-semibold text-[var(--theme-primary)]">Top {targets.length}</span>
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
                  : "border-[#e8ecf3] bg-white hover:bg-[#f7f9fc]"
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-[11px] font-semibold text-[#8b92a1]">#{index + 1}</p>
                  <strong className="mt-1 block truncate text-sm font-semibold text-[#151720]">{displayDistributionLabel(item.label, "target")}</strong>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-[var(--theme-primary)]">{formatPercent(item.rate)}</p>
                  <p className="text-[11px] text-[#8b92a1]">{formatNumber(item.count)} 条</p>
                </div>
              </div>
              <div className="mt-3 h-1 rounded-full bg-[#edf0f5]">
                <div className="h-1 rounded-full bg-[var(--theme-primary)]" style={{ width: `${Math.min(100, item.rate)}%` }} />
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function GenericTargetNote({ summary }: { summary?: ProductPkoDistributionItem }) {
  return (
    <section className="rounded-[22px] border border-[#e8ecf3] bg-[#f7f9fc] p-4">
      <p className="text-xs font-medium text-[#8b92a1]">Generic Comparison</p>
      <div className="mt-2 flex items-end justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-[#151720]">泛化对比</h3>
          <p className="mt-1 text-xs leading-5 text-[#7b8190]">底表为“其他”的评论单独呈现，避免误判为明确竞品。</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-semibold text-[#151720]">{formatNumber(summary?.count)} 条</p>
          <p className="text-xs font-semibold text-[var(--voc-chart-5)]">{formatPercent(summary?.rate)}</p>
        </div>
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
    <section className="rounded-[22px] border border-[#e8ecf3] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-[#151720]">
          <Quote className="h-4 w-4 text-[var(--voc-chart-3)]" />
          典型评论
        </div>
        {selectedTarget ? <span className="rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[11px] text-[var(--theme-primary)]">{selectedTarget}</span> : null}
      </div>
      {evidence ? (
        <>
          <p className="line-clamp-4 min-h-[72px] text-sm leading-6 text-[#4a5160]">{evidence.comment_text}</p>
          <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
            <span className="rounded-full bg-[var(--theme-selected-bg)] px-2.5 py-1 text-[var(--theme-primary)]">{displayDistributionLabel(evidence.target, "target")}</span>
            <span className="rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[var(--voc-chart-2)]">{displayDistributionLabel(evidence.dimension, "dimension")}</span>
            <span className="rounded-full bg-[var(--theme-chip)] px-2.5 py-1 text-[var(--voc-chart-3)]">{evidence.result}</span>
          </div>
          {evidence.reason ? <p className="mt-3 line-clamp-2 text-xs leading-5 text-[#8b92a1]">依据：{evidence.reason}</p> : null}
        </>
      ) : (
        <div className="flex h-32 items-center justify-center rounded-2xl border border-dashed border-[#d9deea] bg-[#f7f9fc] text-sm text-[#8b92a1]">
          暂无可展示的评论
        </div>
      )}
    </section>
  );
}

function DimensionResultMatrix({ rows }: { rows: ProductPkoDimensionResultRow[] }) {
  const maxTotal = Math.max(...rows.map((row) => row.total_count), 1);
  return (
    <section className="rounded-[24px] border border-[#e8ecf3] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Dimension x Result</p>
          <h3 className="text-base font-semibold text-[#151720]">维度胜负矩阵</h3>
        </div>
        <span className="text-xs text-[#8b92a1]">按评论量排序</span>
      </div>
      <div className="overflow-hidden rounded-[18px] border border-[#e8ecf3]">
        <div className="grid grid-cols-[1.3fr_1fr_2fr] bg-[#f7f9fc] px-4 py-2 text-[11px] font-semibold text-[#8b92a1]">
          <span>维度</span>
          <span>主要对象</span>
          <span>胜负分布</span>
        </div>
        {rows.length ? (
          rows.map((row) => {
            const advantageWidth = (row.advantage_count / maxTotal) * 100;
            const disadvantageWidth = (row.disadvantage_count / maxTotal) * 100;
            const neutralWidth = (row.neutral_count / maxTotal) * 100;
            const unclearWidth = (row.unclear_count / maxTotal) * 100;
            return (
              <div key={row.dimension} className="grid grid-cols-[1.3fr_1fr_2fr] items-center gap-3 border-t border-[#eef1f6] px-4 py-3">
                <div className="min-w-0">
                  <strong className="block truncate text-sm font-semibold text-[#151720]">{displayDistributionLabel(row.dimension, "dimension")}</strong>
                  <span className="text-[11px] text-[#8b92a1]">{formatNumber(row.total_count)} 条</span>
                </div>
                <span className="truncate text-xs text-[#4a5160]">{displayDistributionLabel(row.top_target, "target")}</span>
                <div className="space-y-1.5">
                  <div className="flex h-2 overflow-hidden rounded-full bg-[#edf0f5]">
                    <span className="bg-[var(--voc-chart-3)]" style={{ width: `${advantageWidth}%` }} />
                    <span className="bg-[var(--voc-chart-6)]" style={{ width: `${disadvantageWidth}%` }} />
                    <span className="bg-[var(--voc-chart-2)]" style={{ width: `${neutralWidth}%` }} />
                    <span className="bg-[#c8ceda]" style={{ width: `${unclearWidth}%` }} />
                  </div>
                  <p className="text-[11px] text-[#8b92a1]">
                    优 {row.advantage_count} / 劣 {row.disadvantage_count} / 中 {row.neutral_count} / 未明 {row.unclear_count}
                  </p>
                </div>
              </div>
            );
          })
        ) : (
          <div className="flex h-24 items-center justify-center text-sm text-[#8b92a1]">暂无维度矩阵数据</div>
        )}
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
    <article className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Product PKO Story</p>
          <h2 className="mt-1 text-base font-semibold text-[#151720]">PKO 对比与竞争位置</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-selected-bg)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <Scale className="h-3.5 w-3.5" />
            底表结构化标签
          </span>
          <RuleTooltip />
        </div>
      </div>

      <p className="mb-4 rounded-[20px] border border-[#e8ecf3] bg-[#f7f9fc] px-4 py-3 text-sm leading-6 text-[#4a5160]">
        {pkoStory?.summary?.rule_based_conclusion ?? "暂未解析到 PKO 对比评论。"}
      </p>

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <PkoOverview pkoStory={pkoStory} />
        <div className="grid gap-4 md:grid-cols-[0.9fr_1.1fr] xl:grid-cols-1">
          <GenericTargetNote summary={pkoStory?.generic_target_summary} />
          <QuoteCard evidence={evidence} selectedTarget={activeTarget} />
        </div>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
        <ExplicitTargetList targets={explicitTargets} selectedTarget={activeTarget} onSelect={setSelectedTarget} />
        <DimensionResultMatrix rows={pkoStory?.dimension_result_matrix ?? []} />
      </div>
    </article>
  );
}

// Legacy architecture-test markers kept during the PKO redesign:
// OverviewMetricGrid PrimaryDistributionCard 对比对象 对比维度 胜负判断 主要对比对象 主要对比维度 主要胜负判断
