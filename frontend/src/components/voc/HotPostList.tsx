import type { HotPostItem } from "@/types/vocMarket";

type HotPostListProps = {
  posts: HotPostItem[];
};

export function HotPostList({ posts }: HotPostListProps) {
  if (!posts.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">
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
          className="flex items-center gap-3 rounded-2xl bg-zinc-50 px-4 py-3 transition hover:bg-zinc-100"
        >
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white text-xs font-semibold text-zinc-500">
            {index + 1}
          </span>
          <span className="min-w-0 flex-1 truncate text-sm font-medium text-zinc-700">{post.title || "未命名帖子"}</span>
          <span className="text-sm font-semibold text-zinc-950">{post.total_engagement.toLocaleString("zh-CN")}</span>
        </a>
      ))}
    </div>
  );
}
