import type { ReactNode } from "react";

import { reportChartTheme } from "./chartTheme";
import type { ReportVisualChart } from "./types";

type ReportVisualShellProps = {
  chart: ReportVisualChart;
  children: ReactNode;
};

export function ReportVisualShell({ chart, children }: ReportVisualShellProps) {
  return (
    <section
      role="figure"
      aria-label={`${chart.title}。${chart.subtitle}`}
      className="rounded-2xl border p-5"
      style={{
        borderColor: reportChartTheme.border,
        background: reportChartTheme.white,
        color: "var(--theme-primary)",
      }}
    >
      <header>
        <h3 className="text-base font-semibold" style={{ color: reportChartTheme.ink }}>
          {chart.title}
        </h3>
        <p className="mt-1 text-sm" style={{ color: reportChartTheme.muted }}>
          {chart.subtitle}
        </p>
      </header>

      {chart.data.length === 0 ? (
        <div
          className="my-5 rounded-xl border border-dashed px-4 py-10 text-center text-sm"
          style={{
            borderColor: reportChartTheme.border,
            background: reportChartTheme.panel,
            color: reportChartTheme.muted,
          }}
        >
          {chart.meta.empty_reason || "暂无可用于此图表的数据"}
        </div>
      ) : (
        <div className="mt-4">{children}</div>
      )}

      <p className="mt-3 text-sm leading-6" style={{ color: reportChartTheme.body }}>
        {chart.insight}
      </p>
      <p className="mt-2 text-xs" style={{ color: reportChartTheme.muted }}>
        数据来源：{chart.source_label}
      </p>
    </section>
  );
}
