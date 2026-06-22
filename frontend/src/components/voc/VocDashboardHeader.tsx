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
    <header className="voc-dashboard-header flex flex-wrap items-start justify-between gap-4">
      <div>
        <p className="text-xs font-medium text-[var(--theme-subtle)]">{meta.eyebrow}</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--theme-ink)]">{meta.title}</h1>
      </div>

      <div className="voc-dashboard-controls flex max-w-full flex-col items-end gap-2">
        <form className="voc-dashboard-filter-form flex flex-wrap items-center justify-end gap-2">
          <select
            name="event_id"
            defaultValue={selectedEventId}
            className="h-10 min-w-72 rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-sm font-medium text-[var(--theme-ink)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] outline-none focus:border-[var(--theme-primary)]"
          >
            {events.map((item) => (
              <option key={item.event_id} value={item.event_id}>
                {item.event_name}
              </option>
            ))}
          </select>
          <button className="h-10 rounded-lg bg-[var(--theme-primary)] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(93,150,145,0.16)] hover:bg-[var(--theme-primary-hover)]">
            查看
          </button>
          <ThemeSelect />
        </form>

        {event ? (
          <div className="flex max-w-3xl flex-wrap justify-end gap-2 text-xs text-[var(--theme-body)]">
            <span className="inline-flex items-center gap-1 rounded-lg border border-transparent bg-[var(--theme-status-bg)] px-2.5 py-1 text-[var(--theme-status-text)]">
              <CalendarDays className="h-3.5 w-3.5" />
              {event.event_status ?? "未知状态"}
            </span>
            <span className="rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1 text-[var(--theme-body)] shadow-[0_8px_20px_rgba(26,32,44,0.03)]">{event.brand_name ?? "未填品牌"}</span>
            <span className="rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1 text-[var(--theme-body)] shadow-[0_8px_20px_rgba(26,32,44,0.03)]">{event.model_name ?? "未填车型"}</span>
            <span className="rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1 text-[var(--theme-body)] shadow-[0_8px_20px_rgba(26,32,44,0.03)]">{event.event_type ?? "未填类型"}</span>
          </div>
        ) : null}
      </div>
    </header>
  );
}
