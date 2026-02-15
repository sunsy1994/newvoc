import { motion } from 'framer-motion';
import { Smile, Meh, Frown } from 'lucide-react';
import type { ChartCard } from '../../data/chartsData';

interface SentimentBarProps {
  card: ChartCard;
}

const getSentimentIcon = (label: string) => {
  switch (label) {
    case '正面评价':
      return Smile;
    case '负面评价':
      return Frown;
    default:
      return Meh;
  }
};

const getSentimentStyles = (label: string) => {
  switch (label) {
    case '正面评价':
      return {
        color: 'bg-blue-500',
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-600'
      };
    case '负面评价':
      return {
        color: 'bg-indigo-600',
        bgColor: 'bg-indigo-50',
        textColor: 'text-indigo-700'
      };
    default:
      return {
        color: 'bg-gray-400',
        bgColor: 'bg-gray-100',
        textColor: 'text-gray-600'
      };
  }
};

export default function SentimentBar({ card }: SentimentBarProps) {
  const data = card.data as Array<{ label: string; value: number; percentage: number; color: string }>;
  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      {/* 标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">{card.title}</h3>
          {card.subtitle && (
            <p className="text-xs text-gray-500">{card.subtitle}</p>
          )}
        </div>
      </div>

      {/* 情感条 */}
      <div className="space-y-4">
        {data.map((item, index) => {
          const Icon = getSentimentIcon(item.label);
          const styles = getSentimentStyles(item.label);

          return (
            <div key={item.label} className="flex items-center gap-4">
              <div className={`w-10 h-10 ${styles.bgColor} rounded-xl flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-5 h-5 ${styles.textColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-sm font-medium text-gray-700">{item.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-900">
                      {item.value.toLocaleString()}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({item.percentage}%)
                    </span>
                  </div>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(item.value / maxValue) * 100}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1 + 0.3, ease: 'easeOut' }}
                    className={`h-full ${item.color} rounded-full`}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
