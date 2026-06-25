import { ReportAiSummaryCard } from "@/components/voc/ReportAiSummaryCard";

type SalesAiSummaryCardProps = {
  eventId: string;
};

export function SalesAiSummaryCard({ eventId }: SalesAiSummaryCardProps) {
  return (
    <ReportAiSummaryCard
      eventId={eventId}
      departmentName="销售部"
      agentLabel="Sales Report Agent"
      reportTitle="销售部 AI 总结报告"
      emptyText="还没有生成过销售总结。点击右上角“生成报告”后，系统会基于线索质量、用户画像、渠道来源和高意向用户生成销售部视角报告。"
      latestPath="/voc/events/{eventId}/sales/report-agent/latest"
      runPath="/voc/events/{eventId}/sales/report-agent/run"
    />
  );
}
