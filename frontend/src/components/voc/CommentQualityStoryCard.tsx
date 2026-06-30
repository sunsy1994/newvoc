"use client";

import { useEffect, useMemo, useState } from "react";
import { BadgeCheck, ChevronLeft, ChevronRight, Lightbulb, MessageSquareText, RefreshCw } from "lucide-react";

import { CommentTextWithEmojis } from "@/components/common/EmojiText";
import { apiBaseUrl } from "@/config/navigation";
import type {
  CommentQuality,
  CommentQualityDistributionItem,
  DiscussionPointComment,
  DiscussionPointCommentsPayload,
} from "@/types/vocMarket";

type CommentQualityStoryCardProps = {
  eventId: string;
  quality?: CommentQuality;
};

type DiscussionPointBarsProps = {
  rows: CommentQualityDistributionItem[];
  selectedAspect: string | null;
  onSelectRow: (label: string) => void;
};

type DiscussionPointEvidencePanelProps = {
  eventId: string;
  selectedAspect: string | null;
};

const COMMENTS_PER_PAGE = 5;

const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;
const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");

function buildDiscussionPointCommentsUrl(eventId: string, aspect: string, page: number) {
  const offset = (page - 1) * COMMENTS_PER_PAGE;
  return `${apiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/discussion-points/${encodeURIComponent(
    aspect,
  )}/comments?limit=${COMMENTS_PER_PAGE}&offset=${offset}`;
}

function StatPill({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "primary" | "blue" | "green";
}) {
  const tones = {
    primary: "bg-[var(--theme-chip)] text-[var(--theme-primary)]",
    blue: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-5)]",
    green: "bg-[var(--theme-selected-bg)] text-[var(--voc-chart-3)]",
  };

  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-card)] px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className={`mt-2 inline-flex rounded-lg px-2.5 py-1 text-lg font-semibold ${tones[tone]}`}>{value}</strong>
    </div>
  );
}

function signalLabel(value?: string | null) {
  if (!value) return null;
  if (value.endsWith("购买信号")) return value;
  return `${value}购买信号`;
}

function CommentEvidenceItem({ comment }: { comment: DiscussionPointComment }) {
  const purchaseSignal = signalLabel(comment.purchase_signal);

  return (
    <article className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3.5 py-3">
      <div className="mb-2 flex items-center justify-between gap-3 text-[11px] text-[var(--theme-muted)]">
        <span className="truncate font-medium text-[var(--theme-body)]">{comment.comment_author_name || "未知用户"}</span>
        <span className="shrink-0">{comment.published_at ? new Date(comment.published_at).toLocaleString("zh-CN") : "未知时间"}</span>
      </div>
      <p className="line-clamp-2 text-sm leading-6 text-[var(--theme-title)]">
        “<CommentTextWithEmojis text={comment.comment_text} />”
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5 text-[11px] text-[var(--theme-muted)]">
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">互动 {formatNumber(comment.interaction_cnt)}</span>
        {comment.comment_sentiment ? <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">{comment.comment_sentiment}</span> : null}
        {purchaseSignal && ["中购买信号", "强购买信号"].includes(purchaseSignal) ? (
          <span className="rounded-lg bg-[var(--theme-chip)] px-2 py-1 text-[var(--theme-primary)]">{purchaseSignal}</span>
        ) : null}
        {comment.source_title ? <span className="max-w-full truncate rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">来源：{comment.source_title}</span> : null}
      </div>
    </article>
  );
}

function DiscussionPointBars({ rows, selectedAspect, onSelectRow }: DiscussionPointBarsProps) {
  const visibleRows = rows.slice(0, 8);
  const max = Math.max(...visibleRows.map((item) => item.count), 1);

  return (
    <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-[var(--theme-title)]">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--theme-white)] text-[var(--theme-primary)] shadow-sm">
          <Lightbulb className="h-4 w-4" />
        </span>
        用户讨论点 Top 8
      </div>

      {visibleRows.length ? (
        <div className="space-y-3">
          {visibleRows.map((item) => {
            const isSelected = item.label === selectedAspect;
            return (
              <button
                key={item.label}
                type="button"
                onClick={() => onSelectRow(item.label)}
                title={`${item.label}: ${formatNumber(item.count)}条，占比 ${formatPercent(item.rate)}`}
                className={`block w-full rounded-xl px-3 py-2.5 text-left transition ${
                  isSelected
                    ? "bg-[var(--theme-selected-bg)] ring-1 ring-[var(--theme-primary)]"
                    : "bg-[var(--theme-white)] hover:bg-[var(--theme-selected-bg)]"
                }`}
              >
                <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
                  <span className="truncate font-medium text-[var(--theme-body)]">{item.label}</span>
                  <span className="shrink-0 text-[var(--theme-muted)]">
                    {formatNumber(item.count)} · {formatPercent(item.rate)}
                  </span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-[var(--theme-track)]">
                  <div className="h-full rounded-full bg-[var(--voc-chart-3)]" style={{ width: `${(item.count / max) * 100}%` }} />
                </div>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] text-sm text-[var(--theme-muted)]">
          暂无讨论点标签数据
        </div>
      )}
    </div>
  );
}

function DiscussionPointEvidencePanel({ eventId, selectedAspect }: DiscussionPointEvidencePanelProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [payload, setPayload] = useState<DiscussionPointCommentsPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedAspect]);

  useEffect(() => {
    if (!selectedAspect) {
      setPayload(null);
      setError(null);
      return;
    }

    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    fetch(buildDiscussionPointCommentsUrl(eventId, selectedAspect, currentPage), { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error(`评论加载失败：${response.status}`);
        return response.json() as Promise<DiscussionPointCommentsPayload>;
      })
      .then((data) => {
        if (!isCancelled) setPayload(data);
      })
      .catch((requestError: Error) => {
        if (!isCancelled) setError(requestError.message);
      })
      .finally(() => {
        if (!isCancelled) setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [currentPage, eventId, selectedAspect]);

  const totalPages = useMemo(() => Math.max(1, Math.ceil((payload?.total ?? 0) / COMMENTS_PER_PAGE)), [payload?.total]);

  return (
    <div className="flex min-h-[430px] flex-col rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Discussion Evidence</p>
          <h3 className="mt-1 text-sm font-semibold text-[var(--theme-title)]">{selectedAspect ? `「${selectedAspect}」评论证据` : "评论证据"}</h3>
        </div>
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1 text-[11px] text-[var(--theme-muted)]">
          共 {formatNumber(payload?.total)} 条
        </span>
      </div>

      <div className="min-h-0 flex-1 space-y-2.5 overflow-hidden">
        {!selectedAspect ? (
          <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl border border-dashed border-[var(--theme-border)] text-sm text-[var(--theme-muted)]">
            选择左侧讨论点后查看评论
          </div>
        ) : null}
        {isLoading ? (
          <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
            正在加载评论...
          </div>
        ) : null}
        {error && !isLoading ? (
          <div className="flex h-full min-h-[300px] flex-col items-center justify-center gap-3 rounded-xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
            <span>{error}</span>
            <button
              type="button"
              onClick={() => setCurrentPage((page) => page)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 py-1.5 text-xs text-[var(--theme-body)]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              重新加载
            </button>
          </div>
        ) : null}
        {!isLoading && !error && payload?.comments.length === 0 ? (
          <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl border border-dashed border-[var(--theme-border)] text-sm text-[var(--theme-muted)]">
            暂无该讨论点评论
          </div>
        ) : null}
        {!isLoading && !error && payload?.comments.map((comment) => <CommentEvidenceItem key={comment.comment_id} comment={comment} />)}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-[var(--theme-border)] pt-3 text-xs text-[var(--theme-muted)]">
        <span>
          第 {currentPage} / {totalPages} 页
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={currentPage <= 1 || isLoading}
            onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
            className="inline-flex items-center gap-1 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            上一页
          </button>
          <button
            type="button"
            disabled={currentPage >= totalPages || isLoading}
            onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
            className="inline-flex items-center gap-1 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
          >
            下一页
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export function CommentQualityStoryCard({ eventId, quality }: CommentQualityStoryCardProps) {
  const rows = quality?.aspect_distribution ?? [];
  const [selectedAspect, setSelectedAspect] = useState<string | null>(rows[0]?.label ?? null);
  const summary = quality?.summary;
  const hasData = Boolean(summary?.labeled_comment_count);
  const topAspect = summary?.top_aspect ?? "暂无";
  const decisionText = hasData
    ? `有效评论率 ${formatPercent(summary?.vehicle_related_rate)}，用户讨论最集中在「${topAspect}」。正向评论率 ${formatPercent(
        summary?.positive_rate,
      )}，中/强购买信号占 ${formatPercent(summary?.mid_high_purchase_signal_rate)}。`
    : "还没有可解析的评论标签。上传 comment_label_json 后，这里会汇总有效评论率和用户讨论点。";

  useEffect(() => {
    if (!selectedAspect && rows[0]?.label) setSelectedAspect(rows[0].label);
  }, [rows, selectedAspect]);

  return (
    <article className="voc-story-card rounded-[20px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Discussion Quality Story</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-title)]">用户讨论点与有效反馈</h2>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
          <BadgeCheck className="h-3.5 w-3.5" />
          已打标 {formatNumber(summary?.labeled_comment_count)} 条
        </span>
      </div>

      <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {decisionText}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <StatPill label="有效评论率" value={formatPercent(summary?.vehicle_related_rate)} tone="primary" />
        <StatPill label="正向评论率" value={formatPercent(summary?.positive_rate)} tone="blue" />
        <StatPill label="中/强购买信号率" value={formatPercent(summary?.mid_high_purchase_signal_rate)} tone="green" />
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-[var(--theme-muted)]">
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">有效评论 {formatNumber(summary?.vehicle_related_count)} 条</span>
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">负向率 {formatPercent(summary?.negative_rate)}</span>
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">中/强购买信号 {formatNumber(summary?.mid_high_purchase_signal_count)} 条</span>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(360px,1.1fr)]">
        <DiscussionPointBars rows={rows} selectedAspect={selectedAspect} onSelectRow={setSelectedAspect} />
        <DiscussionPointEvidencePanel eventId={eventId} selectedAspect={selectedAspect} />
      </div>

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-[var(--theme-muted)]">
        <MessageSquareText className="h-3.5 w-3.5" />
        讨论点来自 comment_label_json.mentioned_aspect，右侧展示对应评论原文与互动证据。
      </p>
    </article>
  );
}
