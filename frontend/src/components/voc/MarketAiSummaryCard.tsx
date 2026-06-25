import { ReportAiSummaryCard } from "@/components/voc/ReportAiSummaryCard";

type MarketAiSummaryCardProps = {
  eventId: string;
};

export function MarketAiSummaryCard({ eventId }: MarketAiSummaryCardProps) {
  return (
    <ReportAiSummaryCard
      eventId={eventId}
      departmentName="市场部"
      agentLabel="Market Report Agent"
      reportTitle="AI 市场总结报告"
      emptyText="还没有生成过市场总结。点击右上角“生成报告”后，系统会调用模型并把结果保存下来；下次打开会直接展示最近一次结果。"
      latestPath="/voc/events/{eventId}/market/report-agent/latest"
      runPath="/voc/events/{eventId}/market/report-agent/run"
    />
  );
}