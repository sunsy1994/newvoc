"use client";

import { useCallback, useEffect, useState } from "react";
import { ExternalLink, Heart, MessageCircle, RefreshCw, Repeat2, Share2, Star, X } from "lucide-react";

import { DataPagination } from "@/components/shared/DataPagination";
import { apiBaseUrl } from "@/config/navigation";
import type { HotPostItem, PostDetailComment, PostDetailPayload, PostDetailSort } from "@/types/vocMarket";

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
    <div className="rounded-2xl border border-[#e8ecf3] bg-[#f7f9fc] px-3 py-2">
      <div className="flex items-center gap-1.5 text-[11px] text-[#8b92a1]">
        {icon}
        {label}
      </div>
      <p className="mt-1 text-base font-semibold text-[#151720]">{formatNumber(value)}</p>
    </div>
  );
}

function CommentCard({ comment }: { comment: PostDetailComment }) {
  const isReply = Boolean(comment.parent_comment_id);
  const replyTargetName = comment.parent_comment_author_name || "未知用户";

  return (
    <article className={`rounded-2xl border border-[#e8ecf3] bg-white p-4 ${isReply ? "ml-5 border-l-4 border-l-[#887CFD]" : ""}`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="truncate text-sm font-semibold text-[#151720]">{comment.comment_author_name || "未命名评论用户"}</span>
            {comment.location ? <span className="rounded-lg bg-[#f7f9fc] px-2 py-1 text-[11px] text-[#8b92a1]">{comment.location}</span> : null}
            {isReply ? <span className="rounded-lg bg-[#f0efff] px-2 py-1 text-[11px] font-medium text-[#5347CE]">回复</span> : null}
          </div>
          <p className="mt-1 text-xs text-[#8b92a1]">{formatDate(comment.published_at)}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2 text-[11px] font-semibold text-[#596070]">
          <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">互动 {formatNumber(comment.interaction_cnt)}</span>
          <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">赞 {formatNumber(comment.like_cnt)}</span>
          <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">回复 {formatNumber(comment.reply_cnt)}</span>
        </div>
      </div>

      {isReply ? (
        <div className="mt-3 rounded-xl bg-[#f7f9fc] px-3 py-2 text-xs text-[#7b8190]">
          回复给 <span className="font-semibold text-[#596070]">{replyTargetName}</span>
        </div>
      ) : null}

      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-[#3a4050]">{comment.comment_text}</p>
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#151720]/35 p-4 backdrop-blur-sm">
      <section className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-3xl border border-[#e8ecf3] bg-[#f5f7fb] shadow-[0_28px_80px_rgba(21,23,32,0.28)]">
        <header className="flex items-start justify-between gap-4 border-b border-[#e8ecf3] bg-white px-5 py-4">
          <div className="min-w-0">
            <p className="text-xs font-medium text-[#8b92a1]">热门帖子下钻</p>
            <h2 className="mt-1 line-clamp-2 text-lg font-semibold text-[#151720]">{content?.title ?? post.title}</h2>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-[#7b8190]">
              <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">{content?.platform ?? "未知平台"}</span>
              <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">{content?.author_name ?? "未知作者"}</span>
              <span className="rounded-lg bg-[#f7f9fc] px-2 py-1">{formatDate(content?.published_at)}</span>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {content?.source_url ? (
              <a
                href={content.source_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex h-9 items-center gap-2 rounded-lg bg-[#151720] px-3 text-xs font-semibold text-white"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                打开原帖
              </a>
            ) : null}
            <button type="button" onClick={onClose} className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#e8ecf3] bg-white text-[#596070]">
              <X className="h-4 w-4" />
            </button>
          </div>
        </header>

        <div className="overflow-y-auto p-5">
          {error ? <div className="mb-4 rounded-2xl border border-[#ffd7d7] bg-[#fff7f7] p-4 text-sm text-[#b33a3a]">{error}</div> : null}

          <section className="grid gap-3 md:grid-cols-5">
            <MetricPill icon={<Repeat2 className="h-3.5 w-3.5 text-[#5347CE]" />} label="总互动" value={content?.engagement_total ?? post.total_engagement} />
            <MetricPill icon={<Heart className="h-3.5 w-3.5 text-[#ef4444]" />} label="点赞" value={content?.like_cnt} />
            <MetricPill icon={<MessageCircle className="h-3.5 w-3.5 text-[#16C8C7]" />} label="评论" value={content?.comment_cnt} />
            <MetricPill icon={<Share2 className="h-3.5 w-3.5 text-[#4896FE]" />} label="分享" value={content?.share_cnt} />
            <MetricPill icon={<Star className="h-3.5 w-3.5 text-[#887CFD]" />} label="收藏" value={content?.favorite_cnt} />
          </section>

          {content?.content_text ? (
            <section className="mt-4 rounded-2xl border border-[#e8ecf3] bg-white p-4">
              <p className="text-xs font-semibold text-[#8b92a1]">帖子正文</p>
              <p className="mt-2 line-clamp-5 whitespace-pre-wrap text-sm leading-6 text-[#3a4050]">{content.content_text}</p>
            </section>
          ) : null}

          <section className="mt-4 rounded-2xl border border-[#e8ecf3] bg-white p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-[#151720]">评论互动列表</h3>
                <p className="mt-1 text-xs text-[#8b92a1]">展示评论互动量、发布时间和回复关系。</p>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={sort}
                  onChange={(event) => {
                    setSort(event.target.value as PostDetailSort);
                    setOffset(0);
                  }}
                  className="h-9 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-xs font-medium text-[#596070] outline-none focus:border-[#5347CE]"
                >
                  <option value="interaction">按互动排序</option>
                  <option value="published_at">按发布时间排序</option>
                </select>
                <button
                  type="button"
                  onClick={loadDetail}
                  className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs font-medium text-[#596070]"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
                  刷新
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {isLoading ? <div className="rounded-2xl bg-[#f7f9fc] p-6 text-center text-sm text-[#8b92a1]">正在加载评论...</div> : null}
              {!isLoading && payload?.comments.length === 0 ? <div className="rounded-2xl bg-[#f7f9fc] p-6 text-center text-sm text-[#8b92a1]">暂无评论明细</div> : null}
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
