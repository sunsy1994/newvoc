"use client";

import { useState } from "react";
import { Flame, TrendingUp } from "lucide-react";

import { PostDetailModal } from "@/components/voc/PostDetailModal";
import type { HotPostItem } from "@/types/vocMarket";

type HotPostListProps = {
  eventId: string;
  posts: HotPostItem[];
};

function hotBadge(index: number) {
  if (index === 0) return "bg-[#fff1ef] text-[#ef4444]";
  if (index === 1) return "bg-[#f3f1ff] text-[#887CFD]";
  if (index === 2) return "bg-[#eef6ff] text-[#4896FE]";
  return "bg-white text-[#8b92a1]";
}

export function HotPostList({ eventId, posts }: HotPostListProps) {
  const [selectedPost, setSelectedPost] = useState<HotPostItem | null>(null);

  if (!posts.length) {
    return (
      <div className="flex h-52 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少总互动量字段，暂无热门榜单
      </div>
    );
  }

  return (
    <>
      <div className="space-y-2">
        {posts.slice(0, 5).map((post, index) => (
          <button
            key={post.content_id}
            type="button"
            onClick={() => setSelectedPost(post)}
            className="group flex w-full items-center gap-2 rounded-xl bg-[#f7f9fc] px-3 py-2.5 text-left transition hover:bg-[#eef1f6]"
          >
            <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-semibold ${hotBadge(index)}`}>
              {index < 3 ? <Flame className="h-3.5 w-3.5" /> : index + 1}
            </span>
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-[#3a4050]">{post.title || "未命名帖子"}</span>
            <span className="inline-flex shrink-0 items-center gap-1 rounded-lg bg-white px-2 py-1 text-[11px] font-semibold text-[#151720] shadow-[0_6px_14px_rgba(26,32,44,0.04)]">
              <TrendingUp className="h-3 w-3 text-[#16C8C7]" />
              {post.total_engagement.toLocaleString("zh-CN")}
            </span>
          </button>
        ))}
      </div>

      {selectedPost ? <PostDetailModal eventId={eventId} post={selectedPost} onClose={() => setSelectedPost(null)} /> : null}
    </>
  );
}
