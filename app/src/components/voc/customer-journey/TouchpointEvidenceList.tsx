import { MessageSquareText } from 'lucide-react';
import type { JourneyTouchpointItem } from '@/types/customerJourney';

export default function TouchpointEvidenceList({ total, items }: { total: number; items: JourneyTouchpointItem[] }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-950">触点证据</h2>
          <p className="text-xs text-slate-500">共 {total} 条，展示最近触点原文</p>
        </div>
        <MessageSquareText className="h-4 w-4 text-slate-400" />
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-slate-500">暂无真实数据，请先导入触点并运行用户旅程ETL。</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <article key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="rounded-full bg-white px-2 py-1 text-slate-700">{item.sourceChannel}</span>
                <span>{item.journeyStage}</span>
                <span>{item.touchpointTime}</span>
                {item.userDisplayName ? <span>{item.userDisplayName}</span> : null}
              </div>
              <p className="text-sm leading-6 text-slate-800">{item.text}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {item.intentTag ? <span className="rounded-full bg-blue-50 px-2 py-1 text-blue-700">{item.intentTag}</span> : null}
                {item.issueTag ? <span className="rounded-full bg-amber-50 px-2 py-1 text-amber-700">{item.issueTag}</span> : null}
                {item.sentimentTag ? <span className="rounded-full bg-slate-100 px-2 py-1 text-slate-600">{item.sentimentTag}</span> : null}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
