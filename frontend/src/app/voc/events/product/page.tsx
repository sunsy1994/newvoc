import { PackageSearch } from "lucide-react";

import { ProductAiSummaryCard } from "@/components/voc/ProductAiSummaryCard";
import { ProductFocusStoryCard } from "@/components/voc/ProductFocusStoryCard";
import { ProductOpportunityStoryCard } from "@/components/voc/ProductOpportunityStoryCard";
import { ProductPkoStoryCard } from "@/components/voc/ProductPkoStoryCard";
import { VocDashboardHeader } from "@/components/voc/VocDashboardHeader";
import { VocDashboardThemeFrame } from "@/components/voc/VocDashboardThemeFrame";
import { serverApiBaseUrl } from "@/config/navigation";
import type { ProductDashboardPayload, VocEvent } from "@/types/vocMarket";

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

async function getProductDashboard(eventId: string): Promise<ProductDashboardPayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/product-dashboard`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as ProductDashboardPayload;
  } catch {
    return null;
  }
}

type PageProps = {
  searchParams?: {
    event_id?: string;
  };
};

export default async function ProductDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getProductDashboard(selectedEventId) : null;

  return (
    <VocDashboardThemeFrame>
      <div className="mx-auto max-w-[1560px] space-y-5">
        <VocDashboardHeader kind="product" events={events} selectedEventId={selectedEventId} event={dashboard?.event} />

        {dashboard ? (
          <>
            <ProductAiSummaryCard eventId={dashboard.event.event_id} />
            <ProductFocusStoryCard story={dashboard.product_focus_story} />
            <ProductOpportunityStoryCard opportunity={dashboard.product_opportunity_story} />
            <ProductPkoStoryCard pkoStory={dashboard.product_pko_story} />
          </>
        ) : (
          <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-card)] p-10 text-center text-sm text-[var(--theme-muted)]">
            <PackageSearch className="mx-auto mb-3 h-6 w-6 text-[var(--theme-primary)]" />
            暂无产品看板数据。请先导入事件、主贴、评论，并在 comment_label_json 中补充 mentioned_aspect。
          </div>
        )}
      </div>
    </VocDashboardThemeFrame>
  );
}
