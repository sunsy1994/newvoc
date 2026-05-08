import { Activity, Database } from 'lucide-react';
import type { JourneyStageSummaryItem } from '@/types/customerJourney';

const stageOrder = ['曝光认知', '兴趣咨询', '对比评估', '留资/外呼', '试驾/到店', '报价/权益', '下订/战败', '交付/售后', '复购/推荐'];

function formatPercent(value: number) {
  return `${((value || 0) * 100).toFixed(1)}%`;
}

export default function StageOverviewRail({ stages }: { stages: JourneyStageSummaryItem[] }) {
  const byStage = new Map(stages.map((item) => [item.stage, item]));

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-950">旅程阶段总览</h2>
          <p className="text-xs text-slate-500">来自 ads_journey_stage_summary</p>
        </div>
        <Database className="h-4 w-4 text-slate-400" />
      </div>

      {stages.length === 0 ? (
        <p className="text-sm text-slate-500">暂无真实数据，请先导入触点并运行用户旅程ETL。</p>
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3 xl:grid-cols-9">
          {stageOrder.map((stage) => {
            const item = byStage.get(stage);
            return (
              <div key={stage} className="min-h-[132px] rounded-xl border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold text-slate-900">{stage}</span>
                  <Activity className="h-3.5 w-3.5 text-blue-500" />
                </div>
                <p className="mt-3 text-2xl font-semibold text-slate-950">{item?.touchpointCount ?? 0}</p>
                <p className="mt-1 text-xs text-slate-500">渠道 {item?.channelCount ?? 0} 个</p>
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${Math.min((item?.negativeRatio ?? 0) * 100, 100)}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-slate-500">负向 {formatPercent(item?.negativeRatio ?? 0)}</p>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
