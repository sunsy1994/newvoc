import { ClipboardList } from 'lucide-react';
import type { JourneyPainpointItem } from '@/types/customerJourney';

export default function ActionSuggestions({ items }: { items: JourneyPainpointItem[] }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-950">阶段痛点与动作建议</h2>
          <p className="text-xs text-slate-500">由 ads_journey_painpoint_summary 和规则生成</p>
        </div>
        <ClipboardList className="h-4 w-4 text-slate-400" />
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-slate-500">暂无真实数据，请先导入触点并运行用户旅程ETL。</p>
      ) : (
        <div className="space-y-3">
          {items.slice(0, 8).map((item) => (
            <div key={`${item.journeyStage}-${item.issueTag}`} className="rounded-xl border border-slate-200 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{item.journeyStage} · {item.issueTag}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {item.touchpointCount} 条触点，负向 {((item.negativeRatio || 0) * 100).toFixed(1)}%
                  </p>
                </div>
                <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                  {item.suggestedOwner}
                </span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-700">{item.suggestedAction}</p>
              {item.sampleTexts[0]?.text ? (
                <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-5 text-slate-500">
                  证据：{item.sampleTexts[0].text}
                </p>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
