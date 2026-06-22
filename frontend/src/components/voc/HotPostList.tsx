"use client";

import { useState } from "react";

import { EvidenceRankList, type EvidenceRankItem } from "@/components/voc/EvidenceRankList";
import { PostDetailModal } from "@/components/voc/PostDetailModal";
import type { HotPostItem } from "@/types/vocMarket";

type HotPostListProps = {
  eventId: string;
  posts: HotPostItem[];
};

export function HotPostList({ eventId, posts }: HotPostListProps) {
  const [selectedPost, setSelectedPost] = useState<HotPostItem | null>(null);
  const postMap = new Map(posts.map((post) => [post.content_id, post]));
  const items: EvidenceRankItem[] = posts.map((post) => ({
    id: post.content_id,
    title: post.title || "未命名帖子",
    meta: post.comment_peak_bucket ? `评论集中在 ${post.comment_peak_bucket} 爆发` : "暂无评论节奏",
    value: post.total_engagement.toLocaleString("zh-CN"),
    valueLabel: "互动",
  }));

  function onSelectItem(item: EvidenceRankItem) {
    const post = postMap.get(item.id);
    if (post) setSelectedPost(post);
  }

  return (
    <>
      <EvidenceRankList items={items} emptyText="缺少总互动量字段，暂无热门榜单" onSelectItem={onSelectItem} />
      {selectedPost ? <PostDetailModal eventId={eventId} post={selectedPost} onClose={() => setSelectedPost(null)} /> : null}
    </>
  );
}
