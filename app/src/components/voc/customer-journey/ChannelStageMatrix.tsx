import { Grid3X3 } from 'lucide-react';
import type { JourneyMatrixCell } from '@/types/customerJourney';

const stages = ['曝光认知', '兴趣咨询', '对比评估', '留资/外呼', '试驾/到店', '报价/权益', '下订/战败', '交付/售后', '复购/推荐'];
const channels = ['public_social', '400', 'wecom', 'dcc', 'dianping'];

const channelLabel: Record<string, string> = {
  public_social: '抖快小',
  '400': '400',
  wecom: '企业微信',
  dcc: 'DCC',
  dianping: '大众点评',
};

export default function ChannelStageMatrix({ cells }: { cells: JourneyMatrixCell[] }) {
  const byKey = new Map(cells.map((item) => [`${item.sourceChannel}:${item.journeyStage}`, item]));
  const maxCount = Math.max(...cells.map((item) => item.touchpointCount), 1);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-950">渠道 × 阶段矩阵</h2>
          <p className="text-xs text-slate-500">看每类渠道天然落在哪些旅程阶段</p>
        </div>
        <Grid3X3 className="h-4 w-4 text-slate-400" />
      </div>

      {cells.length === 0 ? (
        <p className="text-sm text-slate-500">暂无真实数据，请先导入触点并运行用户旅程ETL。</p>
      ) : (
        <div className="overflow-x-auto">
          <div className="min-w-[920px]">
            <div className="grid grid-cols-[104px_repeat(9,minmax(84px,1fr))] gap-2 text-xs text-slate-500">
              <div />
              {stages.map((stage) => (
                <div key={stage} className="text-center font-medium">{stage}</div>
              ))}
            </div>
            <div className="mt-2 space-y-2">
              {channels.map((channel) => (
                <div key={channel} className="grid grid-cols-[104px_repeat(9,minmax(84px,1fr))] gap-2">
                  <div className="flex items-center rounded-lg bg-slate-100 px-3 text-sm font-medium text-slate-700">
                    {channelLabel[channel] ?? channel}
                  </div>
                  {stages.map((stage) => {
                    const cell = byKey.get(`${channel}:${stage}`);
                    const intensity = cell ? Math.max(14, Math.round((cell.touchpointCount / maxCount) * 88)) : 0;
                    return (
                      <div
                        key={`${channel}-${stage}`}
                        className="h-16 rounded-lg border border-slate-200 p-2 text-center"
                        style={{ backgroundColor: cell ? `rgba(37, 99, 235, ${intensity / 100})` : '#f8fafc' }}
                      >
                        <p className={`text-lg font-semibold ${cell ? 'text-white' : 'text-slate-300'}`}>
                          {cell?.touchpointCount ?? 0}
                        </p>
                        <p className={`text-[11px] ${cell ? 'text-blue-50' : 'text-slate-300'}`}>
                          负向 {(((cell?.negativeRatio ?? 0) * 100).toFixed(0))}%
                        </p>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
