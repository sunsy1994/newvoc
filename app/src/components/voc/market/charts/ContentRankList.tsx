import { motion } from 'framer-motion';
import type { ContentRankData } from '../types';

interface ContentRankListProps {
  data: ContentRankData[];
}

const getRankIcon = (index: number) => {
  if (index === 0) return '🥇';
  if (index === 1) return '🥈';
  if (index === 2) return '🥉';
  return `${index + 1}`;
};

const getSentimentIcon = (ratio: number) => {
  if (ratio > 60) return '😊';
  if (ratio >= 40) return '😐';
  return '☹️';
};

const getSentimentClass = (ratio: number) => {
  if (ratio > 60) return 'bg-emerald-100 text-emerald-700';
  if (ratio >= 40) return 'bg-amber-100 text-amber-700';
  return 'bg-red-100 text-red-700';
};

export default function ContentRankList({ data }: ContentRankListProps) {
  const maxInteraction = Math.max(...data.map(d => d.avgInteraction));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">热门内容类型TOP5</h3>
      </div>

      <div className="space-y-3">
        {data.map((item, index) => (
          <motion.div
            key={item.type}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            {/* 排名 */}
            <div className="w-8 h-8 flex items-center justify-center">
              <span className="text-lg font-bold">{getRankIcon(index)}</span>
            </div>

            {/* 内容图标和名称 */}
            <div className="flex items-center gap-2 flex-1">
              <span className="text-xl">{item.icon}</span>
              <span className="text-sm font-medium text-gray-900">{item.type}</span>
            </div>

            {/* 互动量条 */}
            <div className="flex-1">
              <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.avgInteraction / maxInteraction) * 100}%` }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                />
              </div>
            </div>

            {/* 互动量数值 */}
            <div className="w-16 text-right">
              <span className="text-sm font-semibold text-gray-900">
                {item.avgInteraction >= 10000
                  ? `${(item.avgInteraction / 10000).toFixed(1)}万`
                  : item.avgInteraction.toLocaleString()}
              </span>
            </div>

            {/* 情感标识 */}
            <div className={`px-2 py-1 rounded-lg text-xs font-medium ${getSentimentClass(item.positiveRatio)}`}>
              {getSentimentIcon(item.positiveRatio)} {item.positiveRatio}%
            </div>

            {/* 发布数 */}
            <div className="w-12 text-center">
              <span className="text-xs text-gray-500">{item.count}篇</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
