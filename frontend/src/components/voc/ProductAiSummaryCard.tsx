import { ReportAiSummaryCard } from "@/components/voc/ReportAiSummaryCard";

type ProductAiSummaryCardProps = {
  eventId: string;
};

export function ProductAiSummaryCard({ eventId }: ProductAiSummaryCardProps) {
  return (
    <ReportAiSummaryCard
      eventId={eventId}
      departmentName="产品部"
      agentLabel="Product Report Agent"
      reportTitle="产品部 AI 总结报告"
      emptyText="还没有生成过产品总结。点击右上角“生成报告”后，系统会基于用户关注点、PKO 对比和代表性原声生成产品部视角报告。"
      latestPath="/voc/events/{eventId}/product/report-agent/latest"
      runPath="/voc/events/{eventId}/product/report-agent/run"
    />
  );
}