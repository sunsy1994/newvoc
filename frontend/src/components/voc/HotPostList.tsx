import type { HotPostItem } from "@/types/vocMarket";

type HotPostListProps = {
  posts: HotPostItem[];
};

export function HotPostList({ posts }: HotPostListProps) {
  if (!posts.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少总互动量字段，暂无法展示热门榜单
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {posts.slice(0, 10).map((post, index) => (
        <a
          key={post.content_id}
          href={`#post-${encodeURIComponent(post.content_id)}`}
          className="flex items-center gap-3 rounded-xl bg-[#f7f9fc] px-4 py-3 transition hover:bg-[#eef1f6]"
        >
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white text-xs font-semibold text-[#5347CE] shadow-[0_6px_14px_rgba(26,32,44,0.05)]">
            {index + 1}
          </span>
          <span className="min-w-0 flex-1 truncate text-sm font-medium text-[#3a4050]">{post.title || "未命名帖子"}</span>
          <span className="text-sm font-semibold text-[#151720]">{post.total_engagement.toLocaleString("zh-CN")}</span>
        </a>
      ))}
    </div>
  );
}
