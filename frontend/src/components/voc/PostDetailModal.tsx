"use client";

import { useCallback, useEffect, useState } from "react";
import { ExternalLink, Heart, MessageCircle, RefreshCw, Repeat2, Share2, Star, X } from "lucide-react";

import { CommentTextWithEmojis } from "@/components/common/EmojiText";
import { DataPagination } from "@/components/shared/DataPagination";
import { apiBaseUrl } from "@/config/navigation";
import type { HotPostItem, PostDetailComment, PostDetailPayload, PostDetailSort, PostDetailTimelinePoint } from "@/types/vocMarket";

type PostDetailModalProps = {
  eventId: string;
  post: HotPostItem;
  onClose: () => void;
};

const defaultPageSize = 10;

function buildApiUrl(eventId: string, contentId: string, sort: PostDetailSort, pageSize: number, offset: number) {
  const params = new URLSearchParams({ sort, limit: String(pageSize), offset: String(offset) });
  return `${apiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/contents/${encodeURIComponent(contentId)}/detail?${params}`;
}

function formatNumber(value?: number | null) {
  return Number(value ?? 0).toLocaleString("zh-CN");
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  return value.replace("T", " ").replace("Z", "").slice(0, 19);
}

function MetricPill({ icon, label, value }: { icon: React.ReactNode; label: string; value?: number | null }) {
  return (
    <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-3 py-2">
      <div className="flex items-center gap-1.5 text-[11px] text-[var(--theme-muted)]">
        {icon}
        {label}
      </div>
      <p className="mt-1 text-base font-semibold text-[var(--theme-ink)]">{formatNumber(value)}</p>
    </div>
  );
}

function toTimestamp(value?: string | null) {
  if (!value) return null;
  const timestamp = new Date(value.replace(" ", "T")).getTime();
  return Number.isFinite(timestamp) ? timestamp : null;
}

function CommentTimelineChart({
  points,
  publishedAt,
}: {
  points: PostDetailTimelinePoint[];
  publishedAt?: string | null;
}) {
  const width = 760;
  const height = 180;
  const padding = { top: 20, right: 18, bottom: 34, left: 34 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const visiblePoints = points.slice(0, 7);
  const maxComment = Math.max(...visiblePoints.map((point) => point.comment_count), 1);

  function xFor(index = 0) {
    return padding.left + (visiblePoints.length <= 1 ? chartWidth / 2 : (index / Math.max(visiblePoints.length - 1, 1)) * chartWidth);
  }

  function yFor(count: number) {
    return padding.top + chartHeight - (count / maxComment) * chartHeight;
  }

  const polyline = visiblePoints.map((point, index) => `${xFor(index)},${yFor(point.comment_count)}`).join(" ");

  if (!visiblePoints.length) {
    return (
      <div className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--theme-ink)]">评论波动时间</h3>
            <p className="mt-1 text-xs text-[var(--theme-muted)]">发布时间：{formatDate(publishedAt)}</p>
          </div>
        </div>
        <div className="flex h-36 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
          暂无评论时间线
        </div>
      </div>
    );
  }

  return (
    <section className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-[var(--theme-ink)]">评论波动时间</h3>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">发布时间：{formatDate(publishedAt)} · 发布后发酵节奏</p>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-[var(--theme-muted)]">
          <span className="inline-flex items-center gap-1"><i className="h-2 w-2 rounded-full bg-[var(--theme-primary)]" />评论数</span>
          <span className="inline-flex items-center gap-1"><i className="h-3 w-px bg-[var(--voc-chart-6)]" />发布时间</span>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-56 w-full overflow-visible rounded-2xl bg-[var(--theme-soft-panel)]">
        {[0, 1, 2, 3].map((tick) => {
          const y = padding.top + (tick / 3) * chartHeight;
          return <line key={tick} x1={padding.left} x2={width - padding.right} y1={y} y2={y} stroke="#e8ecf3" strokeWidth="1" />;
        })}
        {publishedAt ? (
          <g>
            <line x1={padding.left} x2={padding.left} y1={padding.top - 4} y2={padding.top + chartHeight + 8} stroke="#f59e0b" strokeWidth="2" strokeDasharray="5 5" />
            <text x={padding.left + 6} y={padding.top + 8} fill="#a16207" fontSize="11" fontWeight="600">发布时间</text>
          </g>
        ) : null}
        <polyline points={polyline} fill="none" stroke="var(--theme-primary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        {visiblePoints.map((point, index) => {
          const x = xFor(index);
          const y = yFor(point.comment_count);
          return (
            <circle key={`${point.time_bucket}-dot`} cx={x} cy={y} r="4" fill="var(--theme-primary)">
              <title>{`${point.relative_bucket || point.time_bucket} 评论 ${point.comment_count}`}</title>
            </circle>
          );
        })}
        {visiblePoints.map((point, index) => {
          if (index !== 0 && index !== visiblePoints.length - 1) return null;
          const x = xFor(index);
          const textAnchor = index === 0 ? "start" : index === visiblePoints.length - 1 ? "end" : "middle";
          return (
            <text key={`${point.time_bucket}-label`} x={x} y={height - 12} textAnchor={textAnchor} fill="#8b92a1" fontSize="11">
              {point.relative_bucket || point.time_bucket}
            </text>
          );
        })}
      </svg>
    </section>
  );
}

function CommentCard({ comment }: { comment: PostDetailComment }) {
  const isReply = Boolean(comment.parent_comment_id);
  const replyTargetName = comment.parent_comment_author_name || "未知用户";

  return (
    <article className={`rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4 ${isReply ? "ml-5 border-l-4 border-l-[var(--theme-selected-border)]" : ""}`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="truncate text-sm font-semibold text-[var(--theme-ink)]">{comment.comment_author_name || "未命名评论用户"}</span>
            {comment.location ? <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1 text-[11px] text-[var(--theme-muted)]">{comment.location}</span> : null}
            {isReply ? <span className="rounded-lg bg-[var(--theme-chip)] px-2 py-1 text-[11px] font-medium text-[var(--theme-primary)]">回复</span> : null}
          </div>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">{formatDate(comment.published_at)}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2 text-[11px] font-semibold text-[var(--theme-body)]">
          <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">互动 {formatNumber(comment.interaction_cnt)}</span>
          <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">赞 {formatNumber(comment.like_cnt)}</span>
          <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">回复 {formatNumber(comment.reply_cnt)}</span>
        </div>
      </div>

      {isReply ? (
        <div className="mt-3 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2 text-xs text-[var(--theme-muted)]">
          回复给 <span className="font-semibold text-[var(--theme-body)]">{replyTargetName}</span>
        </div>
      ) : null}

      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-[var(--theme-body)]">
        <CommentTextWithEmojis text={comment.comment_text} />
      </p>
    </article>
  );
}

export function PostDetailModal({ eventId, post, onClose }: PostDetailModalProps) {
  const [payload, setPayload] = useState<PostDetailPayload | null>(null);
  const [sort, setSort] = useState<PostDetailSort>("interaction");
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDetail = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(buildApiUrl(eventId, post.content_id, sort, pageSize, offset), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as PostDetailPayload);
    } catch {
      setPayload(null);
      setError("帖子详情加载失败，请检查后端服务或数据是否已落库。");
    } finally {
      setIsLoading(false);
    }
  }, [eventId, offset, pageSize, post.content_id, sort]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  const content = payload?.content;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--theme-ink)]/35 p-4 backdrop-blur-sm">
      <section className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-3xl border border-[var(--theme-border)] bg-[var(--theme-page)] shadow-[0_28px_80px_rgba(21,23,32,0.28)]">
        <header className="flex items-start justify-between gap-4 border-b border-[var(--theme-border)] bg-[var(--theme-white)] px-5 py-4">
          <div className="min-w-0">
            <p className="text-xs font-medium text-[var(--theme-muted)]">热门帖子下钻</p>
            <h2 className="mt-1 line-clamp-2 text-lg font-semibold text-[var(--theme-ink)]">{content?.title ?? post.title}</h2>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-[var(--theme-muted)]">
              <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">{content?.platform ?? "未知平台"}</span>
              <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">{content?.author_name ?? "未知作者"}</span>
              <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1">{formatDate(content?.published_at)}</span>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {content?.source_url ? (
              <a
                href={content.source_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex h-9 items-center gap-2 rounded-lg bg-[var(--theme-ink)] px-3 text-xs font-semibold text-white"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                打开原帖
              </a>
            ) : null}
            <button type="button" onClick={onClose} className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)]">
              <X className="h-4 w-4" />
            </button>
          </div>
        </header>

        <div className="overflow-y-auto p-5">
          {error ? <div className="mb-4 rounded-2xl border border-[var(--sales-chip-strong)] bg-[var(--sales-chip-strong)] p-4 text-sm text-[var(--sales-chip-strong-text)]">{error}</div> : null}

          <section className="grid gap-3 md:grid-cols-5">
            <MetricPill icon={<Repeat2 className="h-3.5 w-3.5 text-[var(--theme-primary)]" />} label="总互动" value={content?.engagement_total ?? post.total_engagement} />
            <MetricPill icon={<Heart className="h-3.5 w-3.5 text-[var(--voc-chart-6)]" />} label="点赞" value={content?.like_cnt} />
            <MetricPill icon={<MessageCircle className="h-3.5 w-3.5 text-[var(--voc-chart-3)]" />} label="评论" value={content?.comment_cnt} />
            <MetricPill icon={<Share2 className="h-3.5 w-3.5 text-[var(--voc-chart-5)]" />} label="分享" value={content?.share_cnt} />
            <MetricPill icon={<Star className="h-3.5 w-3.5 text-[var(--voc-chart-4)]" />} label="收藏" value={content?.favorite_cnt} />
          </section>

          {content?.content_text ? (
            <section className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
              <p className="text-xs font-semibold text-[var(--theme-muted)]">帖子正文</p>
              <p className="mt-2 line-clamp-5 whitespace-pre-wrap text-sm leading-6 text-[var(--theme-body)]">{content.content_text}</p>
            </section>
          ) : null}

          <CommentTimelineChart points={payload?.comment_timeline ?? []} publishedAt={content?.published_at} />

          <section className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-[var(--theme-ink)]">评论互动列表</h3>
                <p className="mt-1 text-xs text-[var(--theme-muted)]">展示评论互动量、发布时间和回复关系。</p>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={sort}
                  onChange={(event) => {
                    setSort(event.target.value as PostDetailSort);
                    setOffset(0);
                  }}
                  className="h-9 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-3 text-xs font-medium text-[var(--theme-body)] outline-none focus:border-[var(--theme-primary)]"
                >
                  <option value="interaction">按互动排序</option>
                  <option value="published_at">按发布时间排序</option>
                </select>
                <button
                  type="button"
                  onClick={loadDetail}
                  className="inline-flex h-9 items-center gap-2 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-xs font-medium text-[var(--theme-body)]"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
                  刷新
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {isLoading ? <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-6 text-center text-sm text-[var(--theme-muted)]">正在加载评论...</div> : null}
              {!isLoading && payload?.comments.length === 0 ? <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-6 text-center text-sm text-[var(--theme-muted)]">暂无评论明细</div> : null}
              {payload?.comments.map((comment) => (
                <CommentCard key={comment.comment_id} comment={comment} />
              ))}
            </div>

            <DataPagination total={payload?.total ?? 0} offset={offset} pageSize={pageSize} onOffsetChange={setOffset} onPageSizeChange={setPageSize} />
          </section>
        </div>
      </section>
    </div>
  );
}
