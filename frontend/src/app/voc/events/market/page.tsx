import { Activity, FileText, MessageCircle, Repeat2, Sparkles } from "lucide-react";

import { CommentQualityStoryCard } from "@/components/voc/CommentQualityStoryCard";
import { MarketAiSummaryCard } from "@/components/voc/MarketAiSummaryCard";
import { MetricCard } from "@/components/voc/MetricCard";
import { PlatformStoryCard } from "@/components/voc/PlatformStoryCard";
import { RegionalResponseStoryCard } from "@/components/voc/RegionalResponseStoryCard";
import { SubjectStoryCard } from "@/components/voc/SubjectStoryCard";
import { TopicSpreadStoryCard } from "@/components/voc/TopicSpreadStoryCard";
import { VocDashboardHeader } from "@/components/voc/VocDashboardHeader";
import { VocDashboardThemeFrame } from "@/components/voc/VocDashboardThemeFrame";
import { VolumeRhythmStoryCard } from "@/components/voc/VolumeRhythmStoryCard";
import { serverApiBaseUrl } from "@/config/navigation";
import type { MarketDashboardPayload, VocEvent } from "@/types/vocMarket";

async function getEvents(): Promise<VocEvent[]> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events`, { cache: "no-store" });
    if (!response.ok) return [];
    const payload = (await response.json()) as { events?: VocEvent[] };
    return payload.events ?? [];
  } catch {
    return [];
  }
}

async function getMarketDashboard(eventId: string): Promise<MarketDashboardPayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/market-dashboard`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as MarketDashboardPayload;
  } catch {
    return null;
  }
}

function formatNumber(value: number) {
  return value.toLocaleString("zh-CN");
}

type PageProps = {
  searchParams?: {
    event_id?: string;
  };
};

export default async function MarketDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getMarketDashboard(selectedEventId) : null;
  const metrics = dashboard?.overview_metrics;

  return (
    <VocDashboardThemeFrame>
      <div className="space-y-5">
        <VocDashboardHeader kind="market" events={events} selectedEventId={selectedEventId} event={dashboard?.event} />

        {metrics ? (
          <section className="grid gap-3 md:grid-cols-5">
            <MetricCard label="总声量" value={formatNumber(metrics.total_volume)} hint="主贴 + 评论" tone="purple" icon={<Activity className="h-4 w-4" />} />
            <MetricCard label="主贴数" value={formatNumber(metrics.content_count)} tone="blue" icon={<FileText className="h-4 w-4" />} />
            <MetricCard label="评论数" value={formatNumber(metrics.comment_count)} tone="teal" icon={<MessageCircle className="h-4 w-4" />} />
            <MetricCard label="KOL发声" value={`${formatNumber(metrics.kol_count)} 位`} hint={`贡献 ${formatNumber(metrics.kol_content_count)} 条主贴`} tone="violet" icon={<Sparkles className="h-4 w-4" />} />
            <MetricCard label="总互动量" value={formatNumber(metrics.total_engagement)} tone="neutral" icon={<Repeat2 className="h-4 w-4" />} />
          </section>
        ) : (
          <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-card)] p-10 text-center text-sm text-[var(--theme-muted)]">
            暂无事件数据，请先导入并运行 ETL。
          </div>
        )}

        {dashboard ? (
          <>
            <MarketAiSummaryCard eventId={dashboard.event.event_id} />

            <section className="grid gap-4 lg:grid-cols-[1.18fr_0.82fr]">
              <VolumeRhythmStoryCard trend={dashboard.volume_trend} rhythm={dashboard.volume_rhythm} />
              <SubjectStoryCard story={dashboard.subject_story} userProfiles={dashboard.user_profile_distribution ?? []} />
            </section>

            <PlatformStoryCard
              story={dashboard.platform_story}
              channels={dashboard.channel_distribution}
              eventId={dashboard.event.event_id}
              hotPosts={dashboard.hot_posts}
            />

            <section className="grid gap-4 xl:grid-cols-2">
              <RegionalResponseStoryCard story={dashboard.regional_response_story} eventId={dashboard.event.event_id} />
              <TopicSpreadStoryCard story={dashboard.topic_spread_story} eventId={dashboard.event.event_id} />
            </section>

            <CommentQualityStoryCard eventId={dashboard.event.event_id} quality={dashboard.comment_quality} />
          </>
        ) : null}
      </div>
    </VocDashboardThemeFrame>
  );
}
