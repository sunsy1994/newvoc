"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  BarChart3,
  Bot,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  FileSearch,
  FileText,
  Lightbulb,
  Maximize2,
  MessageCircle,
  MessagesSquare,
  Paperclip,
  RadioTower,
  Search,
  Send,
  Sparkles,
  UsersRound,
  X,
} from "lucide-react";

import type {
  AutoVocBusinessMetric,
  AutoVocCompetitorUpdate,
  AutoVocHomePayload,
  AutoVocHotTopic,
  AutoVocKeyEvent,
} from "@/types/autoVocHome";

type AutoVocHomePageProps = {
  payload: AutoVocHomePayload | null;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatDate = (value?: string | null) => (value ? value.slice(0, 10) : "未知时间");
const ALL_BRANDS = "全部品牌";

function toDateKey(value?: string | null) {
  return value ? value.slice(0, 10) : "";
}

function parseDateKey(value: string) {
  const [year, month, day] = value.split("-").map((part) => Number(part));
  return new Date(year, month - 1, day);
}

function toLocalDateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function monthLabel(date: Date) {
  return `${date.getFullYear()}年${date.getMonth() + 1}月`;
}

function getEventDateKey(event: AutoVocKeyEvent) {
  return toDateKey(event.start_time || event.end_time);
}

function getEventEndDateKey(event: AutoVocKeyEvent) {
  return toDateKey(event.end_time || event.start_time);
}

function isDateKeyInRange(dateKey: string, startKey: string, endKey: string) {
  return dateKey >= startKey && dateKey <= endKey;
}

function eventOverlapsMonth(event: AutoVocKeyEvent, month: Date) {
  const startKey = getEventDateKey(event);
  const endKey = getEventEndDateKey(event) || startKey;
  if (!startKey) return false;
  const monthStart = toLocalDateKey(new Date(month.getFullYear(), month.getMonth(), 1));
  const monthEnd = toLocalDateKey(new Date(month.getFullYear(), month.getMonth() + 1, 0));
  return startKey <= monthEnd && endKey >= monthStart;
}

function getEventDateRangeLabel(event: AutoVocKeyEvent) {
  const startKey = getEventDateKey(event);
  const endKey = getEventEndDateKey(event);
  if (!startKey && !endKey) return "未维护时间";
  if (!endKey || startKey === endKey) return startKey;
  return `${startKey} 至 ${endKey}`;
}

function MetricCard({
  label,
  value,
  helper,
  icon,
}: {
  label: string;
  value: number;
  helper: string;
  icon: React.ReactNode;
}) {
  return (
    <article className="group overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-5 shadow-[var(--sys-card-shadow)] transition hover:-translate-y-0.5 hover:shadow-[var(--sys-card-shadow-hover)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--sys-muted)]">{label}</p>
          <strong className="mt-3 block text-3xl font-semibold tracking-tight text-[var(--sys-ink)]">{formatNumber(value)}</strong>
        </div>
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)] transition group-hover:scale-105">
          {icon}
        </span>
      </div>
      <p className="mt-4 text-xs leading-5 text-[var(--sys-muted)]">{helper}</p>
    </article>
  );
}

const businessMetricIconMap: Record<AutoVocBusinessMetric["metric_key"], React.ReactNode> = {
  own_brand: <RadioTower className="h-5 w-5" />,
  competitor_brand: <BarChart3 className="h-5 w-5" />,
  top_pko_target: <MessagesSquare className="h-5 w-5" />,
  hottest_event: <Sparkles className="h-5 w-5" />,
};

const trendClassMap: Record<AutoVocBusinessMetric["trend"]["tone"], string> = {
  up: "bg-[var(--theme-status-bg)] text-[var(--theme-status-text)]",
  down: "bg-[rgba(193,95,95,0.12)] text-[var(--theme-negative)]",
  flat: "bg-[var(--theme-soft-panel)] text-[var(--sys-muted)]",
  new: "bg-[var(--theme-primary-soft)] text-[var(--theme-selected-text)]",
};

function BusinessMetricCard({ metric }: { metric: AutoVocBusinessMetric }) {
  const content = (
    <article className="group flex min-h-[168px] flex-col overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-5 shadow-[var(--sys-card-shadow)] transition hover:-translate-y-0.5 hover:shadow-[var(--sys-card-shadow-hover)]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs font-semibold text-[var(--sys-muted)]">{metric.label}</p>
          <h3 className="mt-2 truncate text-sm font-semibold text-[var(--sys-ink)]" title={metric.title}>
            {metric.title}
          </h3>
        </div>
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)] transition group-hover:scale-105">
          {businessMetricIconMap[metric.metric_key]}
        </span>
      </div>
      <strong className="mt-4 block text-3xl font-semibold tracking-tight text-[var(--sys-ink)]">{metric.primary_text}</strong>
      <div className="mt-auto flex items-end justify-between gap-3 pt-4">
        <p className="min-w-0 truncate text-xs leading-5 text-[var(--sys-muted)]">{metric.secondary_text}</p>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-semibold ${trendClassMap[metric.trend.tone]}`}>
          {metric.trend.label}
        </span>
      </div>
    </article>
  );

  if (metric.metric_key === "hottest_event" && metric.event_id) {
    return (
      <Link href={`/voc/events/market?event_id=${encodeURIComponent(metric.event_id)}`} className="block">
        {content}
      </Link>
    );
  }

  return content;
}

function KeyEventCard({ event }: { event: AutoVocKeyEvent }) {
  return (
    <article className="rounded-[22px] border border-[var(--sys-border)] bg-white p-4 shadow-[0_10px_26px_rgba(18,24,38,0.04)]">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {event.event_status ? (
              <span className="rounded-full bg-[var(--theme-status-bg)] px-2.5 py-1 text-[11px] font-semibold text-[var(--theme-status-text)]">
                {event.event_status}
              </span>
            ) : null}
            {event.event_type ? <span className="rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-[11px] text-[var(--theme-muted)]">{event.event_type}</span> : null}
          </div>
          <h3 className="line-clamp-2 text-sm font-semibold leading-5 text-[var(--sys-ink)]">{event.event_name}</h3>
          <p className="mt-1 truncate text-xs text-[var(--sys-muted)]">
            {event.brand_name || "未填品牌"} · {event.model_name || "未填车型"}
          </p>
        </div>
        <Link
          href={`/voc/events/market?event_id=${encodeURIComponent(event.event_id)}`}
          className="shrink-0 rounded-xl border border-[var(--sys-border)] bg-[var(--sys-card)] p-2 text-[var(--sys-muted)] transition hover:border-[var(--sys-icon-fill)] hover:text-[var(--sys-icon-fill)]"
          aria-label="进入事件看板"
        >
          <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <span className="rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2">
          <b className="block text-sm text-[var(--sys-ink)]">{formatNumber(event.total_volume)}</b>
          声量
        </span>
        <span className="rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2">
          <b className="block text-sm text-[var(--sys-ink)]">{formatNumber(event.content_count)}</b>
          主贴
        </span>
        <span className="rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2">
          <b className="block text-sm text-[var(--sys-ink)]">{formatNumber(event.comment_count)}</b>
          评论
        </span>
      </div>
    </article>
  );
}

function TopicRow({ topic, index }: { topic: AutoVocHotTopic; index: number }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl bg-white px-3 py-2.5 shadow-[0_8px_20px_rgba(18,24,38,0.035)]">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[var(--theme-soft-panel)] text-xs font-semibold text-[var(--sys-muted)]">
        {index + 1}
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-[var(--sys-ink)]">#{topic.topic}</p>
        <p className="mt-0.5 text-xs text-[var(--sys-muted)]">
          {formatNumber(topic.content_count)} 条主贴 · {formatNumber(topic.comment_count)} 条评论
        </p>
      </div>
      <span className="rounded-xl bg-[var(--theme-primary-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--theme-selected-text)]">
        {formatNumber(topic.total_engagement)}
      </span>
    </div>
  );
}

function CompetitorRow({ item }: { item: AutoVocCompetitorUpdate }) {
  return (
    <a
      href={item.video_url || undefined}
      target={item.video_url ? "_blank" : undefined}
      rel="noreferrer"
      className="block rounded-2xl bg-white px-3 py-3 shadow-[0_8px_20px_rgba(18,24,38,0.035)] transition hover:-translate-y-0.5"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="line-clamp-2 text-sm font-semibold leading-5 text-[var(--sys-ink)]">{item.title || "未命名作品"}</p>
          <p className="mt-1 truncate text-xs text-[var(--sys-muted)]">
            {item.brand_name || "未知品牌"} · {item.author_name || "未知账号"} · {formatDate(item.published_at)}
          </p>
        </div>
        <span className="shrink-0 rounded-xl bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs font-semibold text-[var(--sys-body)]">
          {formatNumber(item.total_interaction)}
        </span>
      </div>
    </a>
  );
}

function EventCalendarCard({ events, periodDays }: { events: AutoVocKeyEvent[]; periodDays: number }) {
  const firstEventDate = events.map(getEventDateKey).find(Boolean);
  const initialDate = firstEventDate ? parseDateKey(firstEventDate) : new Date();
  const [calendarMonth, setCalendarMonth] = useState(() => new Date(initialDate.getFullYear(), initialDate.getMonth(), 1));
  const [selectedBrand, setSelectedBrand] = useState(ALL_BRANDS);
  const [selectedDate, setSelectedDate] = useState(() => firstEventDate || toLocalDateKey(new Date()));

  const brands = [ALL_BRANDS, ...Array.from(new Set(events.map((event) => event.brand_name || "未知品牌"))).filter(Boolean)];
  const filteredEvents = selectedBrand === ALL_BRANDS ? events : events.filter((event) => (event.brand_name || "未知品牌") === selectedBrand);
  const currentMonthEvents = filteredEvents.filter((event) => eventOverlapsMonth(event, calendarMonth));

  const firstDay = new Date(calendarMonth.getFullYear(), calendarMonth.getMonth(), 1);
  const daysInMonth = new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1, 0).getDate();
  const leadingBlanks = (firstDay.getDay() + 6) % 7;
  const monthStartKey = toLocalDateKey(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth(), 1));
  const monthEndKey = toLocalDateKey(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1, 0));
  const baseCells = [
    ...Array.from({ length: leadingBlanks }, (_, index) => ({ key: `blank-start-${index}`, dateKey: "", day: 0 })),
    ...Array.from({ length: daysInMonth }, (_, index) => {
      const date = new Date(calendarMonth.getFullYear(), calendarMonth.getMonth(), index + 1);
      return { key: toLocalDateKey(date), dateKey: toLocalDateKey(date), day: index + 1 };
    }),
  ];
  const trailingBlanks = (7 - (baseCells.length % 7)) % 7;
  const calendarCells = [
    ...baseCells,
    ...Array.from({ length: trailingBlanks }, (_, index) => ({ key: `blank-end-${index}`, dateKey: "", day: 0 })),
  ];
  const weeks = Array.from({ length: Math.ceil(calendarCells.length / 7) }, (_, index) => calendarCells.slice(index * 7, index * 7 + 7));
  const eventsByDate = calendarCells.reduce<Record<string, AutoVocKeyEvent[]>>((bucket, cell) => {
    if (!cell.dateKey) return bucket;
    const activeEvents = currentMonthEvents.filter((event) => {
      const startKey = getEventDateKey(event);
      const endKey = getEventEndDateKey(event) || startKey;
      return Boolean(startKey && endKey && isDateKeyInRange(cell.dateKey, startKey, endKey));
    });
    if (activeEvents.length) bucket[cell.dateKey] = activeEvents;
    return bucket;
  }, {});
  const selectedEvents = eventsByDate[selectedDate] || [];
  const fallbackEvents = selectedEvents.length ? selectedEvents : currentMonthEvents.slice(0, 4);
  const featuredEvent = fallbackEvents[0] || currentMonthEvents[0];

  function goMonth(offset: number) {
    setCalendarMonth((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1));
  }

  function getWeekSegments(week: typeof calendarCells) {
    const weekDateKeys = week.map((cell) => cell.dateKey).filter(Boolean);
    if (!weekDateKeys.length) return [];
    const weekStartKey = weekDateKeys[0];
    const weekEndKey = weekDateKeys[weekDateKeys.length - 1];
    return currentMonthEvents
      .map((event) => {
        const eventStartKey = getEventDateKey(event);
        const eventEndKey = getEventEndDateKey(event) || eventStartKey;
        if (!eventStartKey || !eventEndKey) return null;
        const segmentStartKey = [eventStartKey, weekStartKey, monthStartKey].sort()[2];
        const segmentEndKey = [eventEndKey, weekEndKey, monthEndKey].sort()[0];
        if (segmentStartKey > segmentEndKey) return null;
        const startIndex = week.findIndex((cell) => Boolean(cell.dateKey && cell.dateKey >= segmentStartKey));
        const endIndexFromRight = [...week].reverse().findIndex((cell) => Boolean(cell.dateKey && cell.dateKey <= segmentEndKey));
        const endIndex = endIndexFromRight === -1 ? -1 : week.length - 1 - endIndexFromRight;
        if (startIndex === -1 || endIndex === -1 || startIndex > endIndex) return null;
        return {
          event,
          startIndex,
          endIndex,
          isStart: segmentStartKey === eventStartKey,
          isEnd: segmentEndKey === eventEndKey,
          segmentStartKey,
        };
      })
      .filter((segment): segment is NonNullable<typeof segment> => Boolean(segment))
      .sort((a, b) => b.event.total_volume - a.event.total_volume)
      .slice(0, 3)
      .map((segment, lane) => ({ ...segment, lane }));
  }

  return (
    <section className="overflow-hidden rounded-[30px] border border-[var(--sys-border)] bg-[var(--sys-card)] shadow-[var(--sys-card-shadow)]">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--sys-border)] px-5 py-4">
        <div>
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sys-muted)]">
            <CalendarDays className="h-4 w-4 text-[var(--sys-icon-fill)]" />
            Event Calendar
          </p>
          <h2 className="mt-1.5 text-xl font-semibold tracking-tight text-[var(--sys-ink)]">事件 VOC 日历</h2>
          <p className="mt-1.5 text-sm leading-6 text-[var(--sys-body)]">
            按月查看近 {periodDays} 天事件周期，筛选品牌后快速定位事件发酵窗口。
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedBrand}
            onChange={(event) => setSelectedBrand(event.target.value)}
            className="h-10 rounded-2xl border border-[var(--sys-border)] bg-white px-3 text-sm font-medium text-[var(--sys-ink)] outline-none transition focus:border-[var(--sys-icon-fill)]"
            aria-label="筛选品牌"
          >
            {brands.map((brand) => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
          <div className="flex items-center rounded-2xl border border-[var(--sys-border)] bg-white p-1">
            <button type="button" onClick={() => goMonth(-1)} className="flex h-8 w-8 items-center justify-center rounded-xl text-[var(--sys-muted)] transition hover:bg-[var(--theme-hover-bg)] hover:text-[var(--sys-ink)]" aria-label="上个月">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="min-w-24 px-2 text-center text-sm font-semibold text-[var(--sys-ink)]">{monthLabel(calendarMonth)}</span>
            <button type="button" onClick={() => goMonth(1)} className="flex h-8 w-8 items-center justify-center rounded-xl text-[var(--sys-muted)] transition hover:bg-[var(--theme-hover-bg)] hover:text-[var(--sys-ink)]" aria-label="下个月">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-0 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="p-4">
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-semibold text-[var(--sys-muted)]">
            {["一", "二", "三", "四", "五", "六", "日"].map((day) => <span key={day}>{day}</span>)}
          </div>
          <div className="mt-2.5 space-y-1.5">
            {weeks.map((week, weekIndex) => {
              const segments = getWeekSegments(week);
              return (
                <div key={weekIndex} className="relative grid min-h-[88px] grid-cols-7 gap-2">
                  {week.map((cell) => {
                    const dayEvents = cell.dateKey ? eventsByDate[cell.dateKey] || [] : [];
                    const hasEvents = dayEvents.length > 0;
                    const isSelected = cell.dateKey && cell.dateKey === selectedDate;
                    return (
                      <button
                        key={cell.key}
                        type="button"
                        disabled={!cell.dateKey}
                        onClick={() => cell.dateKey && setSelectedDate(cell.dateKey)}
                        className={`relative rounded-[16px] border p-2 text-left transition ${
                          isSelected
                            ? "border-[var(--sys-icon-fill)] bg-[var(--theme-primary-soft)] shadow-[0_12px_28px_rgba(18,24,38,0.08)]"
                            : hasEvents
                              ? "border-[var(--sys-border)] bg-white hover:-translate-y-0.5 hover:border-[var(--sys-icon-fill)]"
                              : "border-transparent bg-[var(--theme-soft-panel)] text-[var(--sys-subtle)]"
                        }`}
                      >
                        {cell.dateKey ? (
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-semibold text-[var(--sys-ink)]">{cell.day}</span>
                            {hasEvents ? <span className="rounded-full bg-[var(--theme-status-bg)] px-2 py-0.5 text-[10px] font-semibold text-[var(--theme-status-text)]">{dayEvents.length}</span> : null}
                          </div>
                        ) : null}
                      </button>
                    );
                  })}
                  <div className="pointer-events-none absolute inset-x-0 top-[3.35rem] grid grid-cols-7 gap-2">
                    {segments.map((segment) => (
                      <button
                        key={`${segment.event.event_id}-${segment.segmentStartKey}`}
                        type="button"
                        onClick={() => setSelectedDate(segment.segmentStartKey)}
                        className={`pointer-events-auto h-[18px] truncate border border-white/70 bg-[linear-gradient(90deg,var(--theme-primary-soft),rgba(255,255,255,0.72))] px-2 text-left text-[9px] font-semibold leading-[16px] text-[var(--theme-selected-text)] shadow-[0_8px_18px_rgba(18,24,38,0.08)] transition hover:-translate-y-0.5 hover:border-[var(--sys-icon-fill)] ${
                          segment.isStart && segment.isEnd
                            ? "rounded-full"
                            : segment.isStart
                              ? "rounded-l-full rounded-r-md"
                              : segment.isEnd
                                ? "rounded-l-md rounded-r-full"
                                : "rounded-md"
                        }`}
                        style={{ gridColumn: `${segment.startIndex + 1} / ${segment.endIndex + 2}`, gridRow: segment.lane + 1 }}
                        title={`${segment.event.event_name}：${getEventDateRangeLabel(segment.event)}`}
                      >
                        {segment.isStart || segment.startIndex === 0 ? segment.event.event_name : ""}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <aside className="border-t border-[var(--sys-border)] bg-white/55 p-5 xl:border-l xl:border-t-0">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-medium text-[var(--sys-muted)]">Selected Event</p>
              <h3 className="mt-1 text-base font-semibold text-[var(--sys-ink)]">{selectedDate || monthLabel(calendarMonth)}</h3>
            </div>
              <span className="rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs font-semibold text-[var(--sys-muted)]">{fallbackEvents.length} 个</span>
          </div>
          <div className="mt-4">
            {featuredEvent ? (
              <article className="rounded-[22px] border border-[var(--sys-border)] bg-white p-4 shadow-[0_10px_26px_rgba(18,24,38,0.04)]">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="line-clamp-2 text-base font-semibold leading-6 text-[var(--sys-ink)]">{featuredEvent.event_name}</p>
                    <p className="mt-1 truncate text-xs text-[var(--sys-muted)]">{featuredEvent.brand_name || "未知品牌"} · {featuredEvent.model_name || "未知车型"}</p>
                    <p className="mt-2 rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs font-medium text-[var(--sys-muted)]">{getEventDateRangeLabel(featuredEvent)}</p>
                  </div>
                  <Link href={`/voc/events/market?event_id=${encodeURIComponent(featuredEvent.event_id)}`} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[var(--sys-border)] text-[var(--sys-muted)] transition hover:border-[var(--sys-icon-fill)] hover:text-[var(--sys-icon-fill)]" aria-label="进入事件看板">
                    <ArrowUpRight className="h-4 w-4" />
                  </Link>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
                  <span className="rounded-xl bg-[var(--theme-soft-panel)] px-2.5 py-2"><b className="block text-base text-[var(--sys-ink)]">{formatNumber(featuredEvent.total_volume)}</b>声量</span>
                  <span className="rounded-xl bg-[var(--theme-soft-panel)] px-2.5 py-2"><b className="block text-base text-[var(--sys-ink)]">{formatNumber(featuredEvent.content_count)}</b>主贴</span>
                  <span className="rounded-xl bg-[var(--theme-soft-panel)] px-2.5 py-2"><b className="block text-base text-[var(--sys-ink)]">{formatNumber(featuredEvent.comment_count)}</b>评论</span>
                </div>
              </article>
            ) : (
              <EmptyCard title="暂无事件" text="导入并运行 ETL 后，这里会展示当前日期或当前月份的事件。" />
            )}
            {fallbackEvents.length > 1 ? (
              <div className="mt-3 space-y-2">
                {fallbackEvents.slice(1, 4).map((event) => (
                  <button
                    key={event.event_id}
                    type="button"
                    onClick={() => setSelectedDate(getEventDateKey(event))}
                    className="flex w-full items-center justify-between gap-3 rounded-2xl border border-[var(--sys-border)] bg-white px-3 py-2.5 text-left transition hover:border-[var(--sys-icon-fill)] hover:bg-[var(--theme-hover-bg)]"
                  >
                    <span className="min-w-0 truncate text-xs font-semibold text-[var(--sys-ink)]">{event.event_name}</span>
                    <span className="shrink-0 text-xs text-[var(--sys-muted)]">{formatNumber(event.total_volume)}</span>
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        </aside>
      </div>
    </section>
  );
}

function AiOrb() {
  return (
    <div className="auto-voc-ai-orb mx-auto" aria-hidden="true">
      <svg className="auto-voc-ai-orb-filter" focusable="false">
        <filter id="auto-voc-ai-orb-liquid">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.018" numOctaves="2" seed="7">
            <animate
              attributeName="baseFrequency"
              values="0.011 0.017;0.015 0.021;0.011 0.017"
              dur="18s"
              repeatCount="indefinite"
            />
          </feTurbulence>
          <feDisplacementMap in="SourceGraphic" scale="3" />
        </filter>
      </svg>
      <div className="auto-voc-ai-orb-halo" />
      <div className="auto-voc-ai-orb-core">
        <div className="auto-voc-ai-orb-ribbon-wrap">
          <div className="auto-voc-ai-orb-ribbon-body" />
          <div className="auto-voc-ai-orb-ribbon auto-voc-ai-orb-ribbon-main" />
        </div>
        <div className="auto-voc-ai-orb-shine" />
        <div className="auto-voc-ai-orb-glass" />
      </div>
    </div>
  );
}

const aiCapabilities = [
  {
    title: "问数",
    description: "查询事件、帖子、评论、作者等核心指标",
    icon: BarChart3,
  },
  {
    title: "问答",
    description: "解释异常变化，回答业务部门的追问",
    icon: MessagesSquare,
  },
  {
    title: "报告",
    description: "生成市场、产品、销售视角的分析摘要",
    icon: FileSearch,
  },
  {
    title: "洞察",
    description: "发现值得关注的事件、话题和用户信号",
    icon: Lightbulb,
  },
];

function ExpandedAiWorkspace({ prompts, onClose }: { prompts: string[]; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center bg-[rgba(248,250,252,0.88)] p-6 backdrop-blur-xl">
      <section className="relative flex h-full max-h-[760px] w-full max-w-5xl flex-col rounded-[34px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-8 shadow-[0_32px_90px_rgba(20,24,38,0.18)]">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded-full border border-[var(--sys-border)] bg-white text-[var(--sys-muted)] transition hover:text-[var(--sys-ink)]"
          aria-label="关闭 AI 工作台"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="mx-auto w-full max-w-3xl pt-10">
          <div className="mb-8 flex items-center gap-4">
            <div className="scale-75">
              <AiOrb />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--sys-muted)]">AUTO VOC Copilot</p>
              <h2 className="mt-2 text-4xl font-semibold leading-[0.98] tracking-tight text-[var(--sys-ink)]">
                Hi there,
                <span className="block bg-[linear-gradient(90deg,var(--theme-primary),var(--voc-chart-5),var(--voc-chart-3))] bg-clip-text text-transparent">
                  What would you like to know?
                </span>
              </h2>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--sys-muted)]">
                选择一个方向开始，或直接输入你的业务问题。后续这里会接入 CopilotKit。
              </p>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            {aiCapabilities.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.title}
                  type="button"
                  className="group flex min-h-[116px] flex-col justify-between rounded-[18px] border border-[var(--sys-border)] bg-white p-4 text-left shadow-[0_10px_26px_rgba(20,24,38,0.04)] transition hover:-translate-y-0.5 hover:border-[var(--sys-icon-fill)]"
                >
                  <div>
                    <p className="text-sm font-semibold text-[var(--sys-ink)]">{item.title}</p>
                    <p className="mt-2 text-xs leading-5 text-[var(--sys-muted)]">{item.description}</p>
                  </div>
                  <Icon className="mt-4 h-4 w-4 text-[var(--sys-icon-fill)]" />
                </button>
              );
            })}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-2">
            {prompts.slice(0, 4).map((prompt) => (
              <button key={prompt} className="rounded-full border border-[var(--sys-border)] bg-white px-3 py-1.5 text-xs font-medium text-[var(--sys-body)] transition hover:border-[var(--sys-icon-fill)] hover:text-[var(--sys-icon-fill)]">
                {prompt}
              </button>
            ))}
          </div>

          <div className="mt-8 overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-white shadow-[0_18px_42px_rgba(20,24,38,0.07)]">
            <textarea
              className="h-32 w-full resize-none bg-transparent px-5 py-4 text-sm font-medium text-[var(--sys-ink)] outline-none placeholder:text-[var(--sys-muted)]"
              placeholder="Ask whatever you want..."
            />
            <div className="flex items-center justify-between border-t border-[var(--sys-border)] px-4 py-3">
              <div className="flex items-center gap-3 text-xs font-medium text-[var(--sys-muted)]">
                <button className="inline-flex items-center gap-1.5 transition hover:text-[var(--sys-icon-fill)]">
                  <Paperclip className="h-4 w-4" />
                  添加附件
                </button>
                <button className="inline-flex items-center gap-1.5 transition hover:text-[var(--sys-icon-fill)]">
                  <Bot className="h-4 w-4" />
                  使用看板上下文
                </button>
              </div>
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-[var(--theme-soft-panel)] px-3 py-1.5 text-xs font-medium text-[var(--sys-muted)]">AUTO VOC</span>
                <button className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--sys-icon-fill)] text-white shadow-[0_12px_26px_rgba(93,150,145,0.22)]">
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function AiCopilotPanel({ prompts }: { prompts: string[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <aside className="flex h-full min-h-[860px] flex-col rounded-[30px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-5 shadow-[var(--sys-card-shadow)] xl:sticky xl:top-8">
      {isExpanded ? <ExpandedAiWorkspace prompts={prompts} onClose={() => setIsExpanded(false)} /> : null}

      <div className="relative rounded-[26px] bg-[linear-gradient(145deg,var(--theme-soft-panel),var(--theme-card))] px-5 py-6 text-center">
        <button
          type="button"
          onClick={() => setIsExpanded(true)}
          className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full border border-[var(--sys-border)] bg-white/80 text-[var(--sys-muted)] shadow-[0_8px_18px_rgba(20,24,38,0.05)] transition hover:text-[var(--sys-icon-fill)]"
          aria-label="展开 AI 工作台"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </button>
        <AiOrb />
        <p className="mt-5 text-xs font-medium text-[var(--sys-muted)]">AUTO VOC Copilot</p>
        <h2 className="mt-1 text-xl font-semibold text-[var(--sys-ink)]">VOC 智能分析中枢</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--sys-body)]">
          我可以帮你总结事件、解释异常、生成部门视角结论，并把问题带到对应看板继续下钻。
        </p>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sys-muted)]">Skills</p>
          <span className="text-[11px] font-medium text-[var(--sys-muted)]">选择能力开始</span>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2.5">
          {aiCapabilities.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.title}
                type="button"
                className="group min-h-[104px] rounded-[22px] border border-[var(--sys-border)] bg-white p-3.5 text-left transition hover:-translate-y-0.5 hover:border-[var(--sys-icon-fill)] hover:bg-[var(--theme-hover-bg)] hover:shadow-[0_14px_30px_rgba(20,24,38,0.07)]"
              >
                <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-[var(--sys-icon-fill)] transition group-hover:scale-105">
                  <Icon className="h-4 w-4" />
                </span>
                <p className="mt-3 text-sm font-semibold text-[var(--sys-ink)]">{item.title}</p>
                <p className="mt-1 line-clamp-2 text-xs leading-5 text-[var(--sys-muted)]">{item.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sys-muted)]">Prompts</p>
          <span className="text-[11px] font-medium text-[var(--sys-muted)]">你可以这样问</span>
        </div>
        <div className="mt-3 space-y-2">
          {prompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="flex w-full items-center justify-between gap-3 rounded-2xl border border-[var(--sys-border)] bg-white px-3.5 py-3 text-left text-sm font-medium text-[var(--sys-ink)] transition hover:border-[var(--sys-icon-fill)] hover:bg-[var(--theme-hover-bg)]"
            >
              <span>{prompt}</span>
              <Sparkles className="h-4 w-4 shrink-0 text-[var(--sys-icon-fill)]" />
            </button>
          ))}
        </div>
      </div>

      <div className="mt-auto pt-5">
        <div className="flex items-center gap-2 rounded-2xl border border-[var(--sys-border)] bg-white px-3 py-2">
          <input className="min-w-0 flex-1 bg-transparent text-sm text-[var(--sys-ink)] outline-none placeholder:text-[var(--sys-muted)]" placeholder="问 AUTO VOC..." />
          <button className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--sys-icon-fill)] text-white">
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

function EmptyCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center rounded-[24px] border border-dashed border-[var(--sys-border)] bg-[var(--theme-soft-panel)] p-6 text-center">
      <p className="text-sm font-semibold text-[var(--sys-ink)]">{title}</p>
      <p className="mt-2 max-w-sm text-xs leading-5 text-[var(--sys-muted)]">{text}</p>
    </div>
  );
}

export function AutoVocHomePage({ payload }: AutoVocHomePageProps) {
  if (!payload) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <EmptyCard title="首页数据暂时不可用" text="请确认后端服务和 PostgreSQL 已启动，稍后刷新即可恢复 AUTO VOC 首页。" />
      </div>
    );
  }

  const { overview } = payload;
  const hasBusinessMetrics = Array.isArray(payload.business_metrics) && payload.business_metrics.length > 0;

  return (
    <div className="grid items-stretch gap-6 xl:grid-cols-[minmax(0,1fr)_360px] 2xl:grid-cols-[minmax(0,1fr)_390px]">
      <main className="min-w-0 space-y-6">
        <section className="overflow-hidden rounded-[32px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-6 shadow-[var(--sys-card-shadow)]">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sys-muted)]">AUTO VOC</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--sys-ink)]">欢迎来到 AUTO VOC</h1>
              <p className="mt-2 text-sm leading-6 text-[var(--sys-body)]">
                近 {payload.period_days} 天 VOC 业务态势已为你整理完成。重点事件、话题发酵和竞品动态会在这里集中呈现。
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="rounded-full bg-[var(--theme-status-bg)] px-3 py-1.5 font-semibold text-[var(--theme-status-text)]">数据已连接</span>
              <span className="rounded-full bg-[var(--theme-primary-soft)] px-3 py-1.5 font-semibold text-[var(--theme-selected-text)]">AI 助理待命</span>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
          {hasBusinessMetrics ? (
            payload.business_metrics.map((metric) => <BusinessMetricCard key={metric.metric_key} metric={metric} />)
          ) : (
            <>
              <MetricCard label={`近${payload.period_days}天事件`} value={overview.event_count} helper={`全库累计 ${formatNumber(overview.total_event_count)} 个事件`} icon={<RadioTower className="h-5 w-5" />} />
              <MetricCard label={`近${payload.period_days}天帖子`} value={overview.content_count} helper={`全库累计 ${formatNumber(overview.total_content_count)} 条内容`} icon={<FileText className="h-5 w-5" />} />
              <MetricCard label={`近${payload.period_days}天评论`} value={overview.comment_count} helper={`全库累计 ${formatNumber(overview.total_comment_count)} 条评论`} icon={<MessageCircle className="h-5 w-5" />} />
              <MetricCard label={`近${payload.period_days}天作者`} value={overview.author_count} helper={`全库累计 ${formatNumber(overview.total_author_count)} 位作者`} icon={<UsersRound className="h-5 w-5" />} />
            </>
          )}
        </section>

        <EventCalendarCard events={payload.key_events} periodDays={payload.period_days} />

        <section className="grid gap-5 xl:grid-cols-2">
          <article className="rounded-[28px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-5 shadow-[var(--sys-card-shadow)]">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-medium text-[var(--sys-muted)]">Competitor Updates</p>
                <h2 className="mt-1 text-lg font-semibold text-[var(--sys-ink)]">竞品动态</h2>
              </div>
              <Link href="/competitors/works" className="rounded-xl border border-[var(--sys-border)] bg-white px-3 py-2 text-xs font-semibold text-[var(--sys-body)] hover:text-[var(--sys-icon-fill)]">
                作品库
              </Link>
            </div>
            {payload.competitor_updates.length ? (
              <div className="space-y-2.5">
                {payload.competitor_updates.slice(0, 4).map((item) => <CompetitorRow key={item.work_id} item={item} />)}
              </div>
            ) : (
              <EmptyCard title="暂无近期竞品动态" text="导入竞品作品底表后，这里会展示近 30 天高互动竞品内容。" />
            )}
          </article>

          <article className="rounded-[28px] border border-[var(--sys-border)] bg-[var(--sys-card)] p-5 shadow-[var(--sys-card-shadow)]">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-medium text-[var(--sys-muted)]">Hot Search / Topics</p>
                <h2 className="mt-1 text-lg font-semibold text-[var(--sys-ink)]">热搜与话题</h2>
              </div>
              <span className="inline-flex items-center gap-2 rounded-2xl bg-[var(--theme-soft-panel)] px-3 py-2 text-xs font-medium text-[var(--sys-muted)]">
                <Search className="h-3.5 w-3.5" />
                外部情报
              </span>
            </div>
            {payload.hot_topics.length ? (
              <div className="space-y-2.5">
                {payload.hot_topics.slice(0, 4).map((topic, index) => <TopicRow key={topic.topic} topic={topic} index={index} />)}
              </div>
            ) : (
              <EmptyCard title="暂无热搜/话题数据" text="后续接入汽车热搜，或从内容 #话题 中自动聚合后展示。" />
            )}
          </article>
        </section>
      </main>

      <AiCopilotPanel prompts={payload.ai_prompts} />
    </div>
  );
}
