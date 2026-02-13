import { motion } from 'framer-motion';
import KPICards from './KPICards';
import VolumeTrendChart from './charts/VolumeTrendChart';
import PlatformPieChart from './charts/PlatformPieChart';
import KeywordWordCloud from './charts/KeywordWordCloud';
import ChannelQuadrantChart from './charts/ChannelQuadrantChart';
import ContentRankList from './charts/ContentRankList';
import NegativeWordCloud from './charts/NegativeWordCloud';
import KOLQuadrantChart from './charts/KOLQuadrantChart';
import KOLRadarChart from './charts/KOLRadarChart';
import KOLTrendChart from './charts/KOLTrendChart';
import {
  marketKPIData,
  volumeTrendData,
  platformData,
  keywordData,
  channelQuadrantData,
  contentRankData,
  kolInfluenceData,
  radarData,
  kolTrendData,
} from './data/marketChartData';

export default function MarketDashboard() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* 核心指标卡片 */}
      <section>
        <KPICards data={marketKPIData} />
      </section>

      {/* 传播效果分析组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-blue-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">传播效果分析</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <VolumeTrendChart data={volumeTrendData} />
          </div>
          <div>
            <PlatformPieChart data={platformData} />
          </div>
        </div>
        <div className="mt-6">
          <KeywordWordCloud data={keywordData} />
        </div>
      </section>

      {/* 渠道效果分析组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-purple-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">渠道效果分析</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChannelQuadrantChart data={channelQuadrantData} />
          </div>
          <div>
            <ContentRankList data={contentRankData} />
          </div>
        </div>
        <div className="mt-6">
          <NegativeWordCloud data={keywordData} />
        </div>
      </section>

      {/* KOL效果评估组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-emerald-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">KOL效果评估</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <KOLQuadrantChart data={kolInfluenceData} />
          </div>
          <div>
            <KOLRadarChart data={radarData} />
          </div>
        </div>
        <div className="mt-6">
          <KOLTrendChart data={kolTrendData} />
        </div>
      </section>
    </motion.div>
  );
}
