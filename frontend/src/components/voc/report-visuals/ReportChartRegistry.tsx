import type { ComponentType } from "react";

import {
  F3HairlineArea,
  F4TickDonut,
  F5TickRows,
  F6PairedRungs,
  F7StackedRungs,
  F8PlumbScatter,
} from "./BasicsCharts";
import {
  L6ClusterField,
  L12TypeColonnade,
  L13HourglassStream,
  L14HundredField,
} from "./NarrativeCharts";
import { L15BallotTally } from "./SmallDataCharts";
import {
  P1ProductFocusBars,
  P2SentimentStack,
  P3OpportunityLanes,
  P4PkoMatrix,
} from "./ProductCharts";
import type { ReportTemplateId, ReportVisualChart } from "./types";
import { M1VolumeRhythm, M2TopicDrivers, M3SubjectContribution, M4ChannelEfficiency } from "./MarketCharts";
import { S1LeadOutputFunnel, S2UserNeeds, S3ContentSources, S4FollowUpPool } from "./SalesCharts";

type ChartProps = {
  chart: ReportVisualChart;
};

const REPORT_CHARTS = {
  F3: F3HairlineArea,
  F4: F4TickDonut,
  F5: F5TickRows,
  F6: F6PairedRungs,
  F7: F7StackedRungs,
  F8: F8PlumbScatter,
  L6: L6ClusterField,
  L12: L12TypeColonnade,
  L13: L13HourglassStream,
  L14: L14HundredField,
  L15: L15BallotTally,
  P1: P1ProductFocusBars,
  P2: P2SentimentStack,
  P3: P3OpportunityLanes,
  P4: P4PkoMatrix,
  M1: M1VolumeRhythm,
  M2: M2TopicDrivers,
  M3: M3SubjectContribution,
  M4: M4ChannelEfficiency,
  S1: S1LeadOutputFunnel,
  S2: S2UserNeeds,
  S3: S3ContentSources,
  S4: S4FollowUpPool,
} satisfies Record<ReportTemplateId, ComponentType<ChartProps>>;

export function isReportTemplateId(value: unknown): value is ReportTemplateId {
  return typeof value === "string" && Object.prototype.hasOwnProperty.call(REPORT_CHARTS, value);
}

export function ReportChartRegistry({ chart }: ChartProps) {
  const templateId = (chart as { template_id?: unknown } | null)?.template_id;
  if (!isReportTemplateId(templateId)) {
    return (
      <section
        role="status"
        className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-8 text-center text-sm text-[var(--theme-muted)]"
      >
        暂不支持该图表模板
      </section>
    );
  }

  const Chart = REPORT_CHARTS[templateId];
  return <Chart chart={chart} />;
}
