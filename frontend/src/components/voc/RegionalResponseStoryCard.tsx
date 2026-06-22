"use client";

import { useState } from "react";
import { MapPin, MessageCircleMore, RadioTower } from "lucide-react";

import type { HotPostItem, RegionalResponseStory, RegionalTopContentItem } from "@/types/vocMarket";

import { PostDetailModal } from "./PostDetailModal";

type RegionalResponseStoryCardProps = {
  story?: RegionalResponseStory;
  eventId: string;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function toHotPostItem(item: RegionalTopContentItem): HotPostItem {
  return {
    content_id: item.content_id,
    title: item.title,
    total_engagement: 0,
  };
}

export function RegionalResponseStoryCard({ story, eventId }: RegionalResponseStoryCardProps) {
  const [selectedPost, setSelectedPost] = useState<HotPostItem | null>(null);
  const locations = story?.locations ?? [];
  const topContents = story?.top_contents ?? [];
  const maxComments = Math.max(...locations.map((item) => item.comment_count), 1);
  const conclusion =
    story?.summary?.rule_based_conclusion ??
    "暂无评论位置数据。地区响应只基于评论位置统计，不代表主贴发布地区。";

  return (
    <article className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-5 shadow-[0_12px_32px_rgba(20,24,38,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Regional Response</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">地区响应与区域讨论</h2>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-muted)]">
          <MapPin className="h-3.5 w-3.5" />
          评论位置
        </span>
      </div>

      <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-[var(--theme-border)] bg-white p-3">
          <p className="text-[11px] font-medium text-[var(--theme-muted)]">响应最高地区</p>
          <strong className="mt-2 block truncate text-lg font-semibold text-[var(--theme-ink)]">
            {story?.summary?.top_location ?? "暂无"}
          </strong>
        </div>
        <div className="rounded-2xl border border-[var(--theme-border)] bg-white p-3">
          <p className="text-[11px] font-medium text-[var(--theme-muted)]">地区声量占比</p>
          <strong className="mt-2 block text-lg font-semibold text-[var(--theme-primary)]">
            {formatPercent(story?.summary?.top_location_comment_rate)}
          </strong>
        </div>
        <div className="rounded-2xl border border-[var(--theme-border)] bg-white p-3">
          <p className="text-[11px] font-medium text-[var(--theme-muted)]">有效评论率</p>
          <strong className="mt-2 block text-lg font-semibold text-[var(--voc-chart-1)]">
            {formatPercent(story?.summary?.top_location_effective_comment_rate)}
          </strong>
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {locations.slice(0, 8).map((item) => (
          <div key={item.location} title={`${item.location}: ${formatNumber(item.comment_count)}条评论`}>
            <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
              <span className="truncate font-medium text-[var(--theme-ink)]">{item.location}</span>
              <span className="shrink-0 text-[var(--theme-muted)]">
                {formatNumber(item.comment_count)} 条 · {formatPercent(item.comment_rate)}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[var(--theme-track)]">
              <div
                className="h-full rounded-full bg-[var(--theme-primary)]"
                style={{ width: `${Math.max(6, (item.comment_count / maxComments) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {topContents.length ? (
        <div className="mt-5 rounded-2xl border border-[var(--theme-border)] bg-white p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <RadioTower className="h-4 w-4 text-[var(--theme-icon)]" />
            地区热门内容
          </div>
          <div className="space-y-2">
            {topContents.slice(0, 4).map((item) => (
              <button
                type="button"
                key={`${item.location}-${item.content_id}`}
                onClick={() => setSelectedPost(toHotPostItem(item))}
                className="flex w-full items-center justify-between gap-3 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2 text-left text-xs transition hover:bg-[var(--theme-selected-bg)]"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-[var(--theme-ink)]">{item.title}</p>
                  <p className="mt-0.5 text-[var(--theme-muted)]">
                    {item.location} · {item.platform ?? "未知平台"}
                  </p>
                </div>
                <span className="shrink-0 rounded-lg bg-white px-2 py-1 text-[var(--theme-muted)]">
                  {formatNumber(item.comment_count)} 评
                </span>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-[var(--theme-muted)]">
        <MessageCircleMore className="h-3.5 w-3.5" />
        基于评论用户位置统计，不代表内容发布地。
      </p>

      {selectedPost ? <PostDetailModal eventId={eventId} post={selectedPost} onClose={() => setSelectedPost(null)} /> : null}
    </article>
  );
}
