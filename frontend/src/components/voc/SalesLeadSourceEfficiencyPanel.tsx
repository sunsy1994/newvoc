"use client";

import { ExternalLink, MessageCircleMore, PieChart, Sparkles, UserRound, UserRoundCheck } from "lucide-react";
import { useMemo, useState } from "react";

import { PostDetailModal } from "@/components/voc/PostDetailModal";
import type { HotPostItem, SalesContentLeadItem, SalesEvidenceComment, SalesLeadSourceEfficiency, SalesPlatformEfficiencyItem } from "@/types/vocMarket";

type SalesLeadSourceEfficiencyPanelProps = {
  sourceEfficiency?: SalesLeadSourceEfficiency;
  eventId?: string;
};

type SourceModeKey = "all" | "high" | "mid" | "low";
type SourceModeOption = {
  key: SourceModeKey;
  label: string;
  valueKey: "comment_count" | "strong_signal_comment_count" | "mid_signal_comment_count" | "low_signal_comment_count";
  signal?: string;
};
type PieSlice = {
  platform: string;
  value: number;
  percent: number;
  color: string;
  startAngle: number;
  endAngle: number;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;
const channelColors = [
  "var(--voc-chart-1)",
  "var(--voc-chart-2)",
  "var(--voc-chart-3)",
  "var(--voc-chart-4)",
  "var(--voc-chart-5)",
  "var(--voc-chart-6)",
  "#6F7A91",
  "#B7C0D0",
];
const sourceModeOptions: SourceModeOption[] = [
  { key: "all", label: "全部评论", valueKey: "comment_count" },
  { key: "high", label: "高购买强度", valueKey: "strong_signal_comment_count", signal: "强" },
  { key: "mid", label: "中购买强度", valueKey: "mid_signal_comment_count", signal: "中" },
  { key: "low", label: "低购买强度", valueKey: "low_signal_comment_count", signal: "弱" },
];

const signalBadgeClass: Record<string, string> = {
  强: "bg-[var(--sales-chip-strong)] text-[var(--sales-chip-strong-text)]",
  中: "bg-[var(--sales-chip-mid)] text-[var(--sales-chip-mid-text)]",
  弱: "bg-[var(--sales-chip-weak)] text-[var(--sales-chip-weak-text)]",
};

function buildPieSlices(data: SalesPlatformEfficiencyItem[], option: SourceModeOption) {
  const rows = data
    .map((item, index) => ({
      platform: item.platform,
      value: Number(item[option.valueKey] ?? 0),
      color: channelColors[index % channelColors.length],
    }))
    .filter((item) => item.value > 0);
  const total = rows.reduce((sum, item) => sum + item.value, 0);
  let cursor = 0;
  return rows.map((item) => {
    const angle = total ? (item.value / total) * 360 : 0;
    const slice: PieSlice = {
      ...item,
      percent: total ? (item.value * 100) / total : 0,
      startAngle: cursor,
      endAngle: cursor + angle,
    };
    cursor += angle;
    return slice;
  });
}

function describeDonutSegment(slice: PieSlice, circumference: number, gap = 13) {
  const rawLength = ((slice.endAngle - slice.startAngle) / 360) * circumference;
  const visibleLength = Math.max(4, rawLength - gap);
  const offset = -(slice.startAngle / 360) * circumference - gap / 2;
  return {
    strokeDasharray: `${visibleLength} ${Math.max(0, circumference - visibleLength)}`,
    strokeDashoffset: offset,
  };
}

function matchesMode(comment: SalesEvidenceComment, option: SourceModeOption) {
  return !option.signal || comment.purchase_signal === option.signal;
}

function selectedChannelRows<T extends { platform?: string | null }>(rows: T[], platform: string) {
  return rows.filter((item) => item.platform === platform);
}

function toHotPostItem(item: SalesContentLeadItem): HotPostItem {
  return {
    content_id: item.content_id,
    title: item.title,
    total_engagement: Number(item.comment_count ?? 0) + Number(item.high_intent_comment_count ?? 0) + Number(item.strong_signal_comment_count ?? 0),
  };
}

function SeparatedDonutChart({
  data,
  mode,
  selectedPlatform,
  onSelectPlatform,
}: {
  data: SalesPlatformEfficiencyItem[];
  mode: SourceModeOption;
  selectedPlatform: string;
  onSelectPlatform: (platform: string) => void;
}) {
  const slices = buildPieSlices(data, mode);
  const total = slices.reduce((sum, item) => sum + item.value, 0);
  const radius = 86;
  const circumference = 2 * Math.PI * radius;

  return (
    <div className="rounded-[26px] border border-[var(--theme-track)] bg-[var(--theme-card)] p-5 shadow-[0_18px_38px_rgba(30,36,50,0.06)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
          <PieChart className="h-4 w-4 text-[var(--theme-icon)]" />
          渠道数据量
        </div>
        <span className="rounded-full bg-[var(--theme-white)] px-2.5 py-1 text-xs text-[var(--theme-muted)]">当前：{mode.label}</span>
      </div>

      {slices.length ? (
        <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
          <div className="flex justify-center rounded-[24px] bg-[var(--theme-soft-panel)] px-4 py-5">
            <svg className="h-[270px] w-[270px]" viewBox="0 0 260 260" role="img" aria-label={`${mode.label}渠道分离式环图`}>
              <circle cx="130" cy="130" r={radius} fill="none" stroke="var(--theme-track)" strokeWidth="35" />
              {slices.map((slice) => {
                const isSelected = slice.platform === selectedPlatform;
                const segment = describeDonutSegment(slice, circumference);
                const tooltip = `${slice.platform}: ${mode.label} ${formatNumber(slice.value)} 条，占比 ${formatPercent(slice.percent)}`;
                return (
                  <circle
                    key={slice.platform}
                    cx="130"
                    cy="130"
                    r={radius}
                    fill="none"
                    stroke={slice.color}
                    strokeWidth={isSelected ? 39 : 34}
                    strokeLinecap="round"
                    strokeDasharray={segment.strokeDasharray}
                    strokeDashoffset={segment.strokeDashoffset}
                    transform="rotate(-90 130 130)"
                    opacity={isSelected ? 1 : 0.82}
                    className="cursor-pointer drop-shadow-sm transition"
                    onClick={() => onSelectPlatform(slice.platform)}
                  >
                    <title>{tooltip}</title>
                  </circle>
                );
              })}
              <circle cx="130" cy="130" r="57" fill="var(--theme-white)" />
              <text x="130" y="121" textAnchor="middle" className="fill-[var(--theme-muted)] text-[11px] font-medium">
                中心总数
              </text>
              <text x="130" y="148" textAnchor="middle" className="fill-[var(--theme-ink)] text-[24px] font-semibold">
                {formatNumber(total)}
              </text>
            </svg>
          </div>
          <div className="space-y-2.5">
            {slices.map((slice) => {
              const isSelected = slice.platform === selectedPlatform;
              return (
                <button
                  key={slice.platform}
                  type="button"
                  onClick={() => onSelectPlatform(slice.platform)}
                  className={`flex w-full items-center justify-between rounded-2xl border px-3.5 py-3 text-left shadow-[0_8px_18px_rgba(30,36,50,0.035)] transition ${
                    isSelected ? "border-[var(--theme-selected-border)] bg-[var(--theme-selected-bg)] text-[var(--theme-selected-text)]" : "border-[var(--theme-track)] bg-[var(--theme-white)] hover:border-[var(--theme-border)] hover:bg-[var(--theme-hover-bg)]"
                  }`}
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <span className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: slice.color }} />
                    <span className="truncate text-sm font-medium text-[var(--theme-ink)]">{slice.platform}</span>
                  </span>
                  <span className="shrink-0 text-sm font-semibold text-[var(--theme-ink)]">{formatNumber(slice.value)}</span>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="flex h-[270px] items-center justify-center rounded-2xl border border-dashed border-[var(--theme-track)] bg-[var(--theme-white)] text-sm text-[var(--theme-muted)]">
          暂无{mode.label}渠道数据
        </div>
      )}
    </div>
  );
}

function KeyContentList({
  contents,
  selectedPlatform,
  onSelectContent,
}: {
  contents: SalesContentLeadItem[];
  selectedPlatform: string;
  onSelectContent: (content: HotPostItem) => void;
}) {
  const rows = contents.slice(0, 5);
  return (
    <div className="rounded-[26px] border border-[var(--theme-track)] bg-[var(--theme-card)] p-5 shadow-[0_18px_38px_rgba(30,36,50,0.06)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
          <Sparkles className="h-4 w-4 text-[var(--theme-icon)]" />
          重点内容
        </div>
        <span className="rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs text-[var(--theme-muted)]">{selectedPlatform || "全部渠道"}</span>
      </div>
      <div className="space-y-2">
        {rows.map((item, index) => (
          <button
            key={item.content_id}
            type="button"
            onClick={() => onSelectContent(toHotPostItem(item))}
            className="group w-full rounded-2xl border border-[var(--theme-track)] bg-[var(--theme-soft-panel)] p-3 text-left transition hover:border-[var(--theme-selected-border)] hover:bg-[var(--theme-selected-bg)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-[var(--theme-ink)]">
                  <span className="mr-2 text-[var(--theme-selected-border)]">#{index + 1}</span>
                  {item.title}
                </p>
                <p className="mt-1 truncate text-xs text-[var(--theme-muted)]">
                  {item.author_name} · {item.platform}
                </p>
              </div>
              {item.source_url ? (
                <a
                  href={item.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="openSourceUrl shrink-0 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] p-1.5 text-[var(--theme-muted)] transition hover:bg-[var(--theme-hover-bg)] hover:text-[var(--theme-primary)]"
                  aria-label="打开原帖"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              ) : null}
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
              <span className="rounded-xl bg-[var(--theme-selected-bg)] px-2 py-1 text-[var(--theme-selected-border)]">中/强 {formatNumber(item.high_intent_comment_count)}</span>
              <span className="rounded-xl bg-[var(--sales-chip-strong)] px-2 py-1 text-[var(--sales-chip-strong-text)]">强 {formatNumber(item.strong_signal_comment_count)}</span>
              <span className="rounded-xl bg-[var(--theme-chip)] px-2 py-1 text-[var(--theme-selected-text)]">{item.dominant_intent}</span>
            </div>
          </button>
        ))}
        {!rows.length ? <div className="py-12 text-center text-sm text-[var(--theme-muted)]">暂无该渠道重点内容</div> : null}
      </div>
    </div>
  );
}

function SuggestedFollowUpUserList({ leadComments }: { leadComments: SalesEvidenceComment[] }) {
  const rows = leadComments.slice(0, 5);
  return (
    <div className="rounded-[26px] border border-[var(--theme-track)] bg-[var(--theme-card)] p-5 shadow-[0_18px_38px_rgba(30,36,50,0.06)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
          <UserRoundCheck className="h-4 w-4 text-[var(--theme-icon)]" />
          建议跟进用户
        </div>
        <span className="rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs text-[var(--theme-muted)]">用户轻列表</span>
      </div>
      <div className="grid gap-2 xl:grid-cols-5">
        {rows.map((comment, index) => (
          <div
            key={comment.comment_id ?? `${comment.comment_text}-${index}`}
            className="flex min-w-0 items-center gap-3 rounded-2xl border border-[var(--theme-border)] bg-white px-3.5 py-3 shadow-[0_8px_18px_rgba(30,36,50,0.035)]"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--theme-track)] text-[var(--theme-muted)]">
              <UserRound className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="truncate text-xs font-semibold text-[var(--theme-ink)]">{comment.comment_author_name || "评论用户"}</p>
                <span className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-[var(--theme-muted)]">
                  <span className="h-2.5 w-2.5 rounded-full bg-[var(--theme-icon)]" />
                  {formatNumber(comment.interaction_cnt)}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-1.5">
                <span className={`rounded-full px-2 py-0.5 text-[10px] ${signalBadgeClass[comment.purchase_signal] ?? "bg-[var(--theme-soft-panel)] text-[var(--theme-muted)]"}`}>
                  {comment.purchase_signal || "未标注"}
                </span>
                <span className="truncate text-[10px] text-[var(--theme-muted)]">{comment.comment_intent}</span>
              </div>
            </div>
          </div>
        ))}
        {!rows.length ? <div className="py-10 text-center text-sm text-[var(--theme-muted)] xl:col-span-5">暂无建议跟进用户</div> : null}
      </div>
    </div>
  );
}

export function SalesLeadSourceEfficiencyPanel({ sourceEfficiency, eventId }: SalesLeadSourceEfficiencyPanelProps) {
  const summary = sourceEfficiency?.summary;
  const platformRows = sourceEfficiency?.platform_efficiency ?? [];
  const contentRows = sourceEfficiency?.content_leads ?? [];
  const leadComments = sourceEfficiency?.lead_comments ?? [];
  const [modeKey, setModeKey] = useState<SourceModeKey>("all");
  const [selectedContent, setSelectedContent] = useState<HotPostItem | null>(null);
  const selectedMode = sourceModeOptions.find((option) => option.key === modeKey) ?? sourceModeOptions[0];
  const slices = useMemo(() => buildPieSlices(platformRows, selectedMode), [platformRows, selectedMode]);
  const [selectedPlatform, setSelectedPlatform] = useState(summary?.top_platform ?? platformRows[0]?.platform ?? "");
  const activePlatform = selectedPlatform || slices[0]?.platform || summary?.top_platform || "";
  const filteredContents = useMemo(() => {
    const selectedRows = selectedChannelRows(contentRows, activePlatform);
    return selectedRows.length ? selectedRows : contentRows;
  }, [contentRows, activePlatform]);
  const filteredLeadComments = useMemo(() => {
    const byMode = leadComments.filter((comment) => matchesMode(comment, selectedMode));
    const byPlatform = selectedChannelRows(byMode, activePlatform);
    return byPlatform.length ? byPlatform : byMode;
  }, [leadComments, selectedMode, activePlatform]);
  const totalForMode = slices.reduce((sum, item) => sum + item.value, 0);
  const conclusion = summary?.rule_based_conclusion
    ? summary.rule_based_conclusion
    : "补充 purchase_signal 与 comment_intent 后，这里会展示渠道、内容入口与建议跟进用户。";

  return (
    <section className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Sales Source Efficiency</p>
          <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">线索来源效率</h2>
          <p className="mt-3 max-w-4xl rounded-[18px] border border-[var(--theme-track)] bg-[var(--theme-soft-panel)] px-4 py-3 text-sm leading-6 text-[var(--theme-body)]">{conclusion}</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--theme-selected-bg)] px-3 py-2 text-xs font-medium text-[var(--theme-selected-border)]">
          <MessageCircleMore className="h-3.5 w-3.5" />
          {selectedMode.label} {formatNumber(totalForMode)}
        </span>
      </div>

      <div className="mb-4 inline-flex max-w-full flex-wrap gap-1 rounded-2xl border border-[var(--theme-track)] bg-[var(--theme-soft-panel)] p-1">
        {sourceModeOptions.map((option) => (
          <button
            key={option.key}
            type="button"
            onClick={() => setModeKey(option.key)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
              modeKey === option.key ? "bg-[var(--theme-primary)] text-white shadow-[0_8px_18px_rgba(45,43,49,0.18)]" : "bg-[var(--theme-soft-panel)] text-[var(--theme-muted)] hover:bg-[var(--theme-hover-bg)] hover:text-[var(--theme-ink)]"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(340px,0.82fr)_minmax(0,1.18fr)]">
        <SeparatedDonutChart data={platformRows} mode={selectedMode} selectedPlatform={activePlatform} onSelectPlatform={setSelectedPlatform} />
        <KeyContentList contents={filteredContents} selectedPlatform={activePlatform} onSelectContent={setSelectedContent} />
      </div>

      <div className="mt-4">
        <SuggestedFollowUpUserList leadComments={filteredLeadComments} />
      </div>

      {selectedContent && eventId ? (
        <PostDetailModal eventId={eventId} post={selectedContent} onClose={() => setSelectedContent(null)} />
      ) : null}
    </section>
  );
}
