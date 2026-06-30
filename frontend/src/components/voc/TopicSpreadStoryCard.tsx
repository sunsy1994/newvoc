"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Hash, Megaphone, MousePointerClick, X } from "lucide-react";

import type { HotPostItem, TopicSpreadContentItem, TopicSpreadItem, TopicSpreadStory } from "@/types/vocMarket";

import { PostDetailModal } from "./PostDetailModal";

type TopicSpreadStoryCardProps = {
  story?: TopicSpreadStory;
  eventId: string;
};

type TopicContentDrawerProps = {
  topic: TopicSpreadItem | null;
  onClose: () => void;
  onSelectPost: (post: HotPostItem) => void;
};

const TOPICS_PER_PAGE = 5;

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function toHotPostItem(item: TopicSpreadContentItem): HotPostItem {
  return {
    content_id: item.content_id,
    title: item.title,
    total_engagement: item.total_engagement ?? 0,
  };
}

function TopicMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-3">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-2 block truncate text-lg font-semibold text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function TopicContentDrawer({ topic, onClose, onSelectPost }: TopicContentDrawerProps) {
  const isOpen = Boolean(topic);

  return (
    <div className={`fixed inset-0 z-50 transition ${isOpen ? "pointer-events-auto" : "pointer-events-none"}`}>
      <div className={`absolute inset-0 bg-black/20 transition-opacity ${isOpen ? "opacity-100" : "opacity-0"}`} onClick={onClose} />
      <aside
        className={`absolute right-0 top-0 flex h-full w-full max-w-[760px] flex-col border-l border-[var(--theme-border)] bg-[var(--theme-card)] p-6 shadow-[0_24px_80px_rgba(20,24,38,0.18)] transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium text-[var(--theme-muted)]">Topic Contents</p>
            <h3 className="mt-1 text-xl font-semibold text-[var(--theme-ink)]">#{topic?.topic ?? ""}</h3>
            <p className="mt-2 text-sm text-[var(--theme-muted)]">该话题覆盖的内容</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] transition hover:text-[var(--theme-ink)]"
            aria-label="关闭话题内容抽屉"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {topic ? (
          <>
            <div className="mb-5 grid gap-3 sm:grid-cols-3">
              <TopicMetric label="覆盖帖子" value={`${formatNumber(topic.content_count)} 条`} />
              <TopicMetric label="评论量" value={`${formatNumber(topic.comment_count)} 条`} />
              <TopicMetric label="总互动" value={formatNumber(topic.total_engagement)} />
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto pr-1">
              <div className="space-y-2">
                {topic.top_contents.map((content, index) => (
                  <button
                    key={`${topic.topic}-${content.content_id}`}
                    type="button"
                    onClick={() => onSelectPost(toHotPostItem(content))}
                    className="flex w-full items-center gap-3 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-3 text-left transition hover:border-[var(--theme-selected-border)] hover:bg-[var(--theme-selected-bg)]"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[var(--theme-soft-panel)] text-xs font-semibold text-[var(--theme-muted)]">
                      {index + 1}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold text-[var(--theme-ink)]">{content.title}</span>
                      <span className="mt-1 block text-xs text-[var(--theme-muted)]">
                        {content.platform ?? "未知平台"} · {formatNumber(content.comment_count)} 评论 · {formatNumber(content.total_engagement)} 互动
                      </span>
                    </span>
                    <span className="shrink-0 rounded-lg bg-[var(--theme-chip)] px-2.5 py-1 text-xs font-medium text-[var(--theme-primary)]">查看详情</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : null}
      </aside>
    </div>
  );
}

export function TopicSpreadStoryCard({ story, eventId }: TopicSpreadStoryCardProps) {
  const [topicOffset, setTopicOffset] = useState(0);
  const [selectedTopic, setSelectedTopic] = useState<TopicSpreadItem | null>(null);
  const [selectedPost, setSelectedPost] = useState<HotPostItem | null>(null);
  const topics = story?.topics ?? [];
  const visibleTopics = topics.slice(topicOffset, topicOffset + TOPICS_PER_PAGE);
  const currentPage = topics.length ? Math.floor(topicOffset / TOPICS_PER_PAGE) + 1 : 1;
  const pageCount = Math.max(1, Math.ceil(topics.length / TOPICS_PER_PAGE));
  const maxComments = Math.max(...visibleTopics.map((item) => item.comment_count), 1);
  const conclusion =
    story?.summary?.rule_based_conclusion ??
    "暂未从主贴标题或正文中解析到 #话题。补充带 # 的话题文本后，这里会展示话题传播效率。";

  function goToPage(nextPage: number) {
    const safePage = Math.min(Math.max(nextPage, 1), pageCount);
    setTopicOffset((safePage - 1) * TOPICS_PER_PAGE);
  }

  return (
    <article className="voc-story-card rounded-[20px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Topic Spread</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">话题传播效率</h2>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-muted)]">
          <Hash className="h-3.5 w-3.5" />
          #话题
        </span>
      </div>

      <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <TopicMetric label="最高效话题" value={`#${story?.summary?.top_topic ?? "暂无话题"}`} />
        <TopicMetric label="话题评论" value={formatNumber(story?.summary?.top_topic_comment_count)} />
        <TopicMetric label="购买信号率" value={formatPercent(story?.summary?.top_topic_purchase_signal_rate)} />
      </div>

      {topics.length ? (
        <>
          <div className="mt-5 space-y-2">
            {visibleTopics.map((item) => (
              <button
                key={item.topic}
                type="button"
                onClick={() => setSelectedTopic(item)}
                className="block w-full rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-3 text-left transition hover:border-[var(--theme-selected-border)] hover:bg-[var(--theme-selected-bg)]"
              >
                <div className="mb-2 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-[var(--theme-ink)]">#{item.topic}</p>
                    <p className="mt-0.5 text-[11px] text-[var(--theme-muted)]">
                      {formatNumber(item.content_count)} 条主贴 · {formatNumber(item.total_engagement)} 互动
                    </p>
                  </div>
                  <span className="shrink-0 rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs font-medium text-[var(--theme-muted)]">
                    {formatNumber(item.comment_count)} 评
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-[var(--theme-track)]">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.max(6, (item.comment_count / maxComments) * 100)}%`,
                      background: "linear-gradient(90deg, var(--theme-primary), var(--voc-chart-5))",
                    }}
                  />
                </div>
                <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap gap-1.5 text-[11px] text-[var(--theme-muted)]">
                    <span className="rounded-lg bg-[var(--theme-primary-soft)] px-2 py-1 text-[var(--theme-selected-text)]">有效 {formatPercent(item.effective_comment_rate)}</span>
                    <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1 text-[var(--theme-body)]">正向 {formatPercent(item.positive_rate)}</span>
                    <span className="rounded-lg bg-[var(--sales-chip-mid)] px-2 py-1 text-[var(--sales-chip-mid-text)]">中/强 {formatPercent(item.purchase_signal_rate)}</span>
                  </div>
                  <span className="shrink-0 text-[11px] font-medium text-[var(--theme-primary)]">查看相关内容</span>
                </div>
              </button>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between gap-3 text-xs text-[var(--theme-muted)]">
            <span>
              显示 {topicOffset + 1} - {Math.min(topicOffset + TOPICS_PER_PAGE, topics.length)} / {topics.length}
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={currentPage <= 1}
                onClick={() => goToPage(currentPage - 1)}
                className="inline-flex h-8 items-center gap-1 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 font-medium disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
                上一页
              </button>
              <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1 font-medium">
                {currentPage} / {pageCount}
              </span>
              <button
                type="button"
                disabled={currentPage >= pageCount}
                onClick={() => goToPage(currentPage + 1)}
                className="inline-flex h-8 items-center gap-1 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 font-medium disabled:cursor-not-allowed disabled:opacity-40"
              >
                下一页
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="mt-5 flex h-48 flex-col items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-center">
          <Megaphone className="mb-3 h-8 w-8 text-[var(--theme-icon)]" />
          <p className="text-sm font-medium text-[var(--theme-ink)]">未解析到 #话题</p>
          <p className="mt-1 max-w-sm text-xs leading-5 text-[var(--theme-muted)]">
            当前版本从主贴标题和正文解析 # 标签；如果原始视频话题能稳定导入，后续可扩展为独立字段。
          </p>
        </div>
      )}

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-[var(--theme-muted)]">
        <MousePointerClick className="h-3.5 w-3.5" />
        只展示底表可解析的 #话题，不做额外 AI 推断。
      </p>

      <TopicContentDrawer topic={selectedTopic} onClose={() => setSelectedTopic(null)} onSelectPost={setSelectedPost} />
      {selectedPost ? <PostDetailModal eventId={eventId} post={selectedPost} onClose={() => setSelectedPost(null)} /> : null}
    </article>
  );
}
