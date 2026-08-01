import type { ProductStorylineMetric, ProductStorylineView } from "./productStorylineData";
import type { ReportVisualChart } from "../report-visuals/types";

const CHAPTER_IDS = ["rhythm", "topics", "subjects", "channels"] as const;

const text = (value: unknown) => typeof value === "string" && value.trim() ? value.trim() : undefined;
const num = (value: unknown) => typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : undefined;
const compact = (value: number) => new Intl.NumberFormat("zh-CN", { notation: "compact", maximumFractionDigits: 1 }).format(value);
const rows = (charts: ReportVisualChart[], id: string) => charts.find((chart) => chart.chart_id === id)?.data ?? [];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function unique(items: ProductStorylineMetric[]) {
  const seen = new Set<string>();
  return items.filter((item) => { const key = `${item.label}:${item.value}`; if (seen.has(key)) return false; seen.add(key); return true; });
}

function rhythmMetrics(charts: ReportVisualChart[]) {
  const trend = rows(charts, "market-volume-rhythm");
  const total = trend.reduce((sum, row) => sum + (num(row.total_volume) ?? (num(row.content_count) ?? 0) + (num(row.comment_count) ?? 0)), 0);
  const peak = trend.reduce<Record<string, unknown> | undefined>((best, row) => !best || (num(row.total_volume) ?? 0) > (num(best.total_volume) ?? 0) ? row : best, undefined);
  return [
    ...(total ? [{ label: "总声量", value: compact(total) }] : []),
    ...(peak && text(peak.date) ? [{ label: "峰值日期", value: text(peak.date)! }] : []),
    ...(peak && num(peak.total_volume) !== undefined ? [{ label: "峰值声量", value: compact(num(peak.total_volume)!) }] : []),
  ];
}

function topicMetrics(charts: ReportVisualChart[]) {
  return [...rows(charts, "market-topic-drivers")].sort((a, b) => (num(b.comment_count) ?? 0) - (num(a.comment_count) ?? 0)).flatMap((row) => text(row.topic) && num(row.comment_count) !== undefined ? [{ label: text(row.topic)!, value: `${compact(num(row.comment_count)!)} 评论` }] : []).slice(0, 3);
}

function subjectMetrics(charts: ReportVisualChart[]) {
  return [...rows(charts, "market-subject-contribution")].sort((a, b) => (num(b.total_engagement) ?? 0) - (num(a.total_engagement) ?? 0)).flatMap((row) => text(row.author_name) && num(row.total_engagement) !== undefined ? [{ label: text(row.author_name)!, value: `${compact(num(row.total_engagement)!)} 互动` }] : []).slice(0, 3);
}

function channelMetrics(charts: ReportVisualChart[]) {
  return [...rows(charts, "market-channel-efficiency")].sort((a, b) => (num(b.total_volume) ?? 0) - (num(a.total_volume) ?? 0)).flatMap((row) => text(row.platform) && num(row.total_volume) !== undefined ? [{ label: text(row.platform)!, value: `${compact(num(row.total_volume)!)} 声量` }] : []).slice(0, 3);
}

const resolvers: Record<string, (charts: ReportVisualChart[]) => ProductStorylineMetric[]> = {
  scale: rhythmMetrics,
  rhythm: rhythmMetrics,
  volume_trend: rhythmMetrics,
  "hot_topics.summary": topicMetrics,
  "hot_topics.topics": topicMetrics,
  "kol_and_authors.summary": subjectMetrics,
  "kol_and_authors.top_authors": subjectMetrics,
  "kol_and_authors.kol_type_distribution": subjectMetrics,
  "platform.summary": channelMetrics,
  "platform.platform_efficiency": channelMetrics,
};

export function isMarketStoryline(value: unknown) {
  return isRecord(value) && Boolean(text(value.headline)) && Boolean(text(value.lead)) && Array.isArray(value.chapters) && value.chapters.length === 4 && value.chapters.every((chapter, index) => isRecord(chapter) && chapter.chapter_id === CHAPTER_IDS[index] && Boolean(text(chapter.title)) && Boolean(text(chapter.conclusion)) && typeof chapter.body === "string" && Array.isArray(chapter.metric_refs));
}

export function buildMarketStorylineView(value: unknown, charts: ReportVisualChart[], eventName?: string): ProductStorylineView | null {
  if (!isMarketStoryline(value)) return null;
  const storyline = value as { headline: string; lead: string; chapters: Array<{ chapter_id: typeof CHAPTER_IDS[number]; title: string; conclusion: string; body: string; metric_refs: string[] }> };
  const chapters = storyline.chapters.map((chapter) => ({ chapterId: chapter.chapter_id, title: chapter.title, conclusion: chapter.conclusion, body: chapter.body, metrics: unique(chapter.metric_refs.flatMap((ref) => resolvers[ref]?.(charts) ?? [])).slice(0, 3), evidence: [] }));
  if (!chapters.some((chapter) => chapter.metrics.length)) return null;
  const hero = unique([...rhythmMetrics(charts).slice(0, 2), ...channelMetrics(charts).slice(0, 1)]);
  return { ...(text(eventName) ? { eventName: text(eventName) } : {}), headline: storyline.headline, lead: storyline.lead, heroMetrics: hero, chapters };
}

export function formatMarketStorylineCopyText(storyline: ProductStorylineView) {
  return [storyline.eventName ? `${storyline.eventName} · 事件传播复盘` : "事件传播复盘", storyline.headline, storyline.lead, ...storyline.chapters.map((chapter, index) => [`${String(index + 1).padStart(2, "0")} ${chapter.title}`, `结论：${chapter.conclusion}`, chapter.body, ...chapter.metrics.map((metric) => `- ${metric.label}：${metric.value}`)].filter(Boolean).join("\n"))].filter(Boolean).join("\n\n");
}
