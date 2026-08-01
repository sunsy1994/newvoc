import type { ReactNode } from "react";

import { reportChartTheme } from "./chartTheme";
import type { ReportVisualChart } from "./types";

type ReportVisualShellProps = {
  chart: ReportVisualChart;
  children: ReactNode;
  hasData?: boolean;
};

export function ReportVisualShell({ chart, children, hasData = chart.data.length > 0 }: ReportVisualShellProps) {
  const isProductChart = typeof chart.chart_id === "string" && chart.chart_id.startsWith("product-");
  const emptyReason =
    typeof chart.meta?.empty_reason === "string" && chart.meta.empty_reason.trim()
      ? chart.meta.empty_reason
      : "暂无可用于此图表的数据";
  return (
    <section
      role="figure"
      aria-label={`${chart.title}。${chart.subtitle}`}
      data-product-report-shell={isProductChart || undefined}
      className={isProductChart
        ? "flex h-full flex-col rounded-2xl border p-5"
        : "h-full rounded-2xl border p-5"}
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
        {hasData && isProductChart ? (
          <div
            data-product-insight
            className="mt-3 min-h-[72px] rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2.5"
          >
            <p className="text-sm leading-6" style={{ color: reportChartTheme.body }}>
              {chart.insight || "当前图表暂无可用判断。"}
            </p>
          </div>
        ) : hasData && chart.insight ? (
          <p className="mt-3 text-sm leading-6" style={{ color: reportChartTheme.body }}>
            {chart.insight}
          </p>
        ) : null}
      </header>

      {!hasData ? (
        <div
          className={`${isProductChart ? "flex-1" : ""} my-5 rounded-xl border border-dashed px-4 py-10 text-center text-sm`}
          style={{
            borderColor: reportChartTheme.border,
            background: reportChartTheme.panel,
            color: reportChartTheme.muted,
          }}
        >
          {emptyReason}
        </div>
      ) : (
        <div className={isProductChart ? "mt-4 flex-1" : "mt-4"}>{children}</div>
      )}

      <p
        className={isProductChart ? "mt-auto pt-3 text-xs" : "mt-2 text-xs"}
        style={{ color: reportChartTheme.muted }}
      >
        数据来源：{chart.source_label}
      </p>
    </section>
  );
}
