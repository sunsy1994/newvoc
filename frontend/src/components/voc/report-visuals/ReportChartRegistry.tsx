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
  L12TypeColonnade,
  L13HourglassStream,
  L14HundredField,
} from "./NarrativeCharts";
import type { ReportTemplateId, ReportVisualChart } from "./types";

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
  L12: L12TypeColonnade,
  L13: L13HourglassStream,
  L14: L14HundredField,
} satisfies Record<ReportTemplateId, ComponentType<ChartProps>>;

export function ReportChartRegistry({ chart }: ChartProps) {
  const Chart = REPORT_CHARTS[chart.template_id];
  return <Chart chart={chart} />;
}
