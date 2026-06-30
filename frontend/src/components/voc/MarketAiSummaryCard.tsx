import { ReportAiSummaryCard } from "@/components/voc/ReportAiSummaryCard";

type MarketAiSummaryCardProps = {
  eventId: string;
};

export function MarketAiSummaryCard({ eventId }: MarketAiSummaryCardProps) {
  return (
    <section className="flex flex-col gap-4 rounded-[20px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-4 shadow-[0_12px_32px_rgba(31,43,39,0.045)] sm:flex-row sm:items-center sm:justify-between sm:p-5">
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--theme-primary)]">Market Intelligence</p>
        <h2 className="mt-1.5 text-lg font-semibold tracking-tight text-[var(--theme-ink)]">让 AI 把分散证据收束为一条市场故事线</h2>
        <p className="mt-1 text-sm text-[var(--theme-muted)]">读取当前事件的声量、渠道、区域和评论质量，生成可复用的市场总结。</p>
      </div>
      <ReportAiSummaryCard
        eventId={eventId}
        departmentName="市场部"
        agentLabel="Market Report Agent"
        reportTitle="AI 市场总结报告"
        emptyText="还没有生成过市场总结。点击右上角“生成报告”后，系统会调用模型并把结果保存下来；下次打开会直接展示最近一次结果。"
        latestPath="/voc/events/{eventId}/market/report-agent/latest"
        runPath="/voc/events/{eventId}/market/report-agent/run"
      />
    </section>
  );
}
