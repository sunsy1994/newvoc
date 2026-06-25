import { BriefcaseBusiness } from "lucide-react";

import { SalesAiSummaryCard } from "@/components/voc/SalesAiSummaryCard";
import { SalesLeadQualityStoryCard } from "@/components/voc/SalesLeadQualityStoryCard";
import { SalesLeadSourceEfficiencyPanel } from "@/components/voc/SalesLeadSourceEfficiencyPanel";
import { VocDashboardHeader } from "@/components/voc/VocDashboardHeader";
import { VocDashboardThemeFrame } from "@/components/voc/VocDashboardThemeFrame";
import { serverApiBaseUrl } from "@/config/navigation";
import type { SalesDashboardPayload, VocEvent } from "@/types/vocMarket";

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

async function getSalesDashboard(eventId: string): Promise<SalesDashboardPayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/sales-dashboard`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as SalesDashboardPayload;
  } catch {
    return null;
  }
}

type PageProps = {
  searchParams?: {
    event_id?: string;
  };
};

export default async function SalesDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getSalesDashboard(selectedEventId) : null;

  return (
    <VocDashboardThemeFrame>
      <div className="space-y-5">
        <VocDashboardHeader kind="sales" events={events} selectedEventId={selectedEventId} event={dashboard?.event} />

        {dashboard ? (
          <>
            <SalesAiSummaryCard eventId={dashboard.event.event_id} />
            <SalesLeadQualityStoryCard quality={dashboard.sales_lead_quality} eventId={dashboard.event?.event_id ?? selectedEventId} />
            <SalesLeadSourceEfficiencyPanel
              sourceEfficiency={dashboard.sales_lead_source_efficiency}
              eventId={dashboard.event?.event_id ?? selectedEventId}
            />
          </>
        ) : (
          <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-card)] p-10 text-center text-sm text-[var(--theme-muted)]">
            <BriefcaseBusiness className="mx-auto mb-3 h-6 w-6 text-[var(--theme-primary)]" />
            暂无销售看板数据。请先导入事件、主贴、评论，并在 comment_label_json 中补充 purchase_signal 和 comment_intent。
          </div>
        )}
      </div>
    </VocDashboardThemeFrame>
  );
}
