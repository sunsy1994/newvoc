import { motion } from 'framer-motion';
import type { KeywordData } from '../types';

interface SimpleWordCloudProps {
  data: KeywordData[];
  title: string;
  getTextColor: (sentiment: number) => string;
  insight?: React.ReactNode;
}

export default function SimpleWordCloud({ data, title, getTextColor, insight }: SimpleWordCloudProps) {
  // 按频率排序并取前15个
  const sortedData = [...data].sort((a, b) => b.frequency - a.frequency).slice(0, 15);
  const maxFreq = sortedData[0]?.frequency || 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <h3 className="text-base font-semibold text-gray-900 mb-4">{title}</h3>

      <div className="h-[200px] flex flex-wrap items-center justify-center gap-3 content-center p-4">
        {sortedData.map((item, index) => {
          const fontSize = 12 + (item.frequency / maxFreq) * 24;
          const color = getTextColor(item.sentiment);
          return (
            <motion.span
              key={item.text}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="font-medium hover:scale-110 transition-transform cursor-pointer"
              style={{
                fontSize: `${fontSize}px`,
                color,
              }}
            >
              {item.text}
            </motion.span>
          );
        })}
      </div>

      {insight && <div className="mt-4 pt-4 border-t border-gray-100">{insight}</div>}
    </motion.div>
  );
}
