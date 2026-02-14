import { useState } from 'react';
import { motion } from 'framer-motion';
import VolumeTrendChart from './charts/VolumeTrendChart';
import PlatformPieChart from './charts/PlatformPieChart';
import KeywordWordCloud from './charts/KeywordWordCloud';
import ChannelQuadrantChart from './charts/ChannelQuadrantChart';
import ContentRankList from './charts/ContentRankList';
import NegativeWordCloud from './charts/NegativeWordCloud';
import KOLQuadrantChart from './charts/KOLQuadrantChart';
import {
  marketKPIData,
  volumeTrendData,
  platformData,
  keywordData,
  channelQuadrantData,
  contentRankData,
  kolInfluenceData,
} from './data/marketChartData';

type InsightMode = 'keyword' | 'channel' | 'kol';

function formatWan(value: number) {
  return value >= 10000 ? `${(value / 10000).toFixed(1)}万` : value.toLocaleString();
}

export default function MarketDashboard() {
  const [insightMode, setInsightMode] = useState<InsightMode>('keyword');

  const totalVolume = Number(marketKPIData.find((item) => item.type === 'volume')?.value ?? 0);
  const interaction = Number(marketKPIData.find((item) => item.type === 'interaction')?.value ?? 0);
  const breakout = Number(marketKPIData.find((item) => item.type === 'index')?.value ?? 0);
  const nps = Number(marketKPIData.find((item) => item.type === 'nps')?.value ?? 0);
  const negativeRatio = Number(marketKPIData.find((item) => item.type === 'negative')?.value ?? 0);
  const sortedPlatforms = [...platformData].sort((a, b) => b.volume - a.volume);
  const positiveRatio = Math.max(0, 100 - negativeRatio);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm xl:col-span-5">
          <p className="text-sm text-gray-500">市场传播总览</p>
          <h2 className="mt-2 text-4xl font-semibold tracking-tight text-gray-900">{formatWan(totalVolume)} 条</h2>
          <p className="mt-1 text-sm font-medium text-emerald-600">+34% vs 上次上市</p>

          <div className="mt-5 grid grid-cols-3 gap-3">
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">总互动量</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{formatWan(interaction * 1000)}</p>
            </div>
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">破圈指数</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{breakout}%</p>
            </div>
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">NPS估算</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{nps}%</p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm xl:col-span-4">
          <h3 className="text-lg font-semibold text-gray-900">传播健康度</h3>
          <p className="mt-1 text-xs text-gray-500">按情感与互动质量衡量当前传播状态</p>
          <div className="mt-5 space-y-4">
            <div>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-gray-500">正向情感占比</span>
                <span className="font-medium text-emerald-600">{positiveRatio.toFixed(1)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                <div className="h-full rounded-full bg-emerald-500" style={{ width: `${positiveRatio}%` }} />
              </div>
            </div>

            <div>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-gray-500">负向情感占比</span>
                <span className="font-medium text-red-500">{negativeRatio}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                <div className="h-full rounded-full bg-red-400" style={{ width: `${Math.min(100, negativeRatio * 2)}%` }} />
              </div>
            </div>

            <div>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-gray-500">互动活跃度</span>
                <span className="font-medium text-blue-600">66.7%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                <div className="h-full rounded-full bg-blue-500" style={{ width: '66.7%' }} />
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm xl:col-span-3">
          <h3 className="text-lg font-semibold text-gray-900">渠道声量占比</h3>
          <p className="mt-1 text-xs text-gray-500">TOP5 平台实时贡献</p>
          <div className="mt-4 space-y-3">
            {sortedPlatforms.slice(0, 5).map((platform) => {
              const percent = totalVolume ? (platform.volume / totalVolume) * 100 : 0;
              return (
                <div key={platform.platform}>
                  <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
                    <span>{platform.platform}</span>
                    <span>{percent.toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-gray-100">
                    <div className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-blue-500" style={{ width: `${percent}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="xl:col-span-8">
          <VolumeTrendChart data={volumeTrendData} />
        </div>
        <div className="xl:col-span-4">
          <ContentRankList data={contentRankData} />
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm xl:col-span-8">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h3 className="text-base font-semibold text-gray-900">核心分析视图</h3>
            <div className="inline-flex rounded-full border border-gray-200 bg-gray-50 p-1">
              <button
                onClick={() => setInsightMode('keyword')}
                className={`rounded-full px-3 py-1.5 text-xs ${insightMode === 'keyword' ? 'bg-gray-900 text-white' : 'text-gray-600'}`}
              >
                关键词
              </button>
              <button
                onClick={() => setInsightMode('channel')}
                className={`rounded-full px-3 py-1.5 text-xs ${insightMode === 'channel' ? 'bg-gray-900 text-white' : 'text-gray-600'}`}
              >
                渠道
              </button>
              <button
                onClick={() => setInsightMode('kol')}
                className={`rounded-full px-3 py-1.5 text-xs ${insightMode === 'kol' ? 'bg-gray-900 text-white' : 'text-gray-600'}`}
              >
                KOL
              </button>
            </div>
          </div>

          {insightMode === 'keyword' && <KeywordWordCloud data={keywordData} />}
          {insightMode === 'channel' && <ChannelQuadrantChart data={channelQuadrantData} />}
          {insightMode === 'kol' && <KOLQuadrantChart data={kolInfluenceData} />}
        </div>

        <div className="space-y-6 xl:col-span-4">
          <PlatformPieChart data={platformData} />
          <NegativeWordCloud data={keywordData} />
        </div>
      </section>
    </motion.div>
  );
}
