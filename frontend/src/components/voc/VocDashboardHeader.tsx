import { CalendarDays } from "lucide-react";

import type { VocEvent } from "@/types/vocMarket";
import { ThemeSelect } from "@/components/voc/VocDashboardThemeFrame";

type DashboardKind = "market" | "product" | "sales";

type VocDashboardHeaderProps = {
  kind: DashboardKind;
  events: VocEvent[];
  selectedEventId?: string;
  event?: VocEvent | null;
};

const dashboardMeta: Record<DashboardKind, { eyebrow: string; title: string }> = {
  market: { eyebrow: "VOC Event Intelligence", title: "市场看板" },
  product: { eyebrow: "VOC Product Intelligence", title: "产品看板" },
  sales: { eyebrow: "VOC Sales Intelligence", title: "销售看板" },
};

export function VocDashboardHeader({ kind, events, selectedEventId, event }: VocDashboardHeaderProps) {
  const meta = dashboardMeta[kind];

  return (
    <header className="voc-dashboard-header rounded-[20px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-4 shadow-[0_12px_32px_rgba(31,43,39,0.045)] sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--theme-subtle)]">{meta.eyebrow}</p>
          <h1 className="mt-1.5 text-[26px] font-semibold tracking-[-0.03em] text-[var(--theme-ink)]">{meta.title}</h1>
          <p className="mt-1.5 text-sm text-[var(--theme-muted)]">从声量节奏、讨论主体与传播质量中提炼可行动的市场判断。</p>
        </div>

        <div className="voc-dashboard-controls flex w-full flex-col items-stretch gap-2 lg:w-auto lg:items-end">
          <form className="voc-dashboard-filter-form flex w-full flex-wrap items-center gap-2 lg:w-auto lg:justify-end">
            <select
              name="event_id"
              defaultValue={selectedEventId}
              className="h-10 min-w-0 flex-1 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-sm font-medium text-[var(--theme-ink)] shadow-[0_6px_16px_rgba(31,43,39,0.03)] outline-none transition hover:border-[var(--theme-selected-border)] sm:min-w-72"
            >
              {events.map((item) => (
                <option key={item.event_id} value={item.event_id}>
                  {item.event_name}
                </option>
              ))}
            </select>
            <button className="h-10 rounded-xl bg-[var(--theme-primary)] px-4 text-sm font-semibold text-white shadow-[0_10px_22px_rgba(82,127,121,0.2)] transition hover:bg-[var(--theme-primary-hover)]">
              查看
            </button>
            <ThemeSelect />
          </form>
        </div>
      </div>

      {event ? (
          <div className="mt-4 flex max-w-full flex-wrap gap-2 border-t border-[var(--theme-border)] pt-3 text-xs text-[var(--theme-body)]">
            <span className="inline-flex items-center gap-1 rounded-lg bg-[var(--theme-status-bg)] px-2.5 py-1 text-[var(--theme-status-text)]">
              <CalendarDays className="h-3.5 w-3.5" />
              {event.event_status ?? "未知状态"}
            </span>
            <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">{event.brand_name ?? "未填品牌"}</span>
            <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">{event.model_name ?? "未填车型"}</span>
            <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">{event.event_type ?? "未填类型"}</span>
          </div>
      ) : null}
    </header>
  );
}
