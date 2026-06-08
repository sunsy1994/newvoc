import { CalendarDays, Download, Filter, Search } from "lucide-react";

import { ChannelStackedBars } from "@/components/voc/ChannelStackedBars";
import { HotPostList } from "@/components/voc/HotPostList";
import { KolTypeBars } from "@/components/voc/KolTypeBars";
import { MetricCard } from "@/components/voc/MetricCard";
import { VolumeTrendChart } from "@/components/voc/VolumeTrendChart";
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

function DashboardCard({
  title,
  subtitle,
  children,
  action,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <article className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-[#151720]">{title}</h2>
          {subtitle ? <p className="mt-1 text-xs text-[#8b92a1]">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </article>
  );
}

export default async function MarketDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getMarketDashboard(selectedEventId) : null;
  const metrics = dashboard?.overview_metrics;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">VOC Event Intelligence</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">市场看板</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="hidden h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs text-[#8b92a1] shadow-[0_8px_20px_rgba(26,32,44,0.03)] md:flex">
            <Search className="h-3.5 w-3.5" />
            Search
          </div>
          <button className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs font-medium text-[#596070]">
            <Filter className="h-3.5 w-3.5" />
            Filter
          </button>
          <button className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs font-medium text-[#596070]">
            <Download className="h-3.5 w-3.5" />
            Export
          </button>
        </div>
      </header>

      <section className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <form className="flex flex-wrap items-center gap-2">
            <select
              name="event_id"
              defaultValue={selectedEventId}
              className="h-10 min-w-72 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm font-medium text-[#151720] outline-none"
            >
              {events.map((event) => (
                <option key={event.event_id} value={event.event_id}>
                  {event.event_name}
                </option>
              ))}
            </select>
            <button className="h-10 rounded-lg bg-[#5347CE] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(83,71,206,0.22)]">
              查看
            </button>
          </form>
          {dashboard?.event ? (
            <div className="flex flex-wrap gap-2 text-xs text-[#6f7685]">
              <span className="inline-flex items-center gap-1 rounded-lg bg-[#f0efff] px-2.5 py-1 text-[#5347CE]">
                <CalendarDays className="h-3.5 w-3.5" />
                {dashboard.event.event_status ?? "未知状态"}
              </span>
              <span className="rounded-lg bg-[#f7f9fc] px-2.5 py-1">{dashboard.event.brand_name ?? "未填品牌"}</span>
              <span className="rounded-lg bg-[#f7f9fc] px-2.5 py-1">{dashboard.event.model_name ?? "未填车型"}</span>
              <span className="rounded-lg bg-[#f7f9fc] px-2.5 py-1">{dashboard.event.event_type ?? "未填类型"}</span>
            </div>
          ) : null}
        </div>
      </section>

      {metrics ? (
        <section className="grid gap-3 md:grid-cols-5">
          <MetricCard label="总声量" value={formatNumber(metrics.total_volume)} hint="主贴 + 评论" tone="purple" />
          <MetricCard label="主贴数" value={formatNumber(metrics.content_count)} tone="blue" />
          <MetricCard label="评论数" value={formatNumber(metrics.comment_count)} tone="teal" />
          <MetricCard label="KOL发声" value={`${formatNumber(metrics.kol_count)} 位`} hint={`贡献 ${formatNumber(metrics.kol_content_count)} 条主贴`} tone="violet" />
          <MetricCard label="总互动量" value={formatNumber(metrics.total_engagement)} tone="neutral" />
        </section>
      ) : (
        <div className="rounded-2xl border border-dashed border-[#d9deea] bg-white p-10 text-center text-sm text-[#8b92a1]">
          暂无事件数据，请先导入并运行ETL。
        </div>
      )}

      {dashboard ? (
        <>
          <section className="grid gap-4 lg:grid-cols-[1.18fr_0.82fr]">
            <DashboardCard title="声量趋势" subtitle="按发布时间聚合，展示事件爆发和回落节奏">
              <VolumeTrendChart data={dashboard.volume_trend} />
            </DashboardCard>
            <DashboardCard title="KOL类型分布" subtitle="来自KOL画像表，按参与KOL人数排序">
              <KolTypeBars data={dashboard.kol_type_distribution} userProfiles={dashboard.user_profile_distribution ?? []} />
            </DashboardCard>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.55fr_0.45fr]">
            <DashboardCard title="渠道分布" subtitle="主贴与评论堆积，评论渠道继承所属主贴">
              <ChannelStackedBars data={dashboard.channel_distribution} />
            </DashboardCard>
            <DashboardCard title="热门热搜" subtitle="按总互动量排序 Top 5">
              <HotPostList posts={dashboard.hot_posts} />
            </DashboardCard>
          </section>
        </>
      ) : null}
    </div>
  );
}
