import { motion } from 'framer-motion';
import { Smile, Meh, Frown } from 'lucide-react';

interface SentimentType {
  icon: React.ElementType;
  label: string;
  value: number;
  color: string;
  bgColor: string;
  textColor: string;
}

const sentimentTypes: SentimentType[] = [
  { 
    icon: Smile, 
    label: '正面评价', 
    value: 28560, 
    color: 'bg-emerald-500', 
    bgColor: 'bg-emerald-50',
    textColor: 'text-emerald-600'
  },
  { 
    icon: Meh, 
    label: '中性评价', 
    value: 12580, 
    color: 'bg-gray-400', 
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600'
  },
  { 
    icon: Frown, 
    label: '负面评价', 
    value: 3530, 
    color: 'bg-red-500', 
    bgColor: 'bg-red-50',
    textColor: 'text-red-600'
  },
];

const maxValue = Math.max(...sentimentTypes.map((s) => s.value));

export default function CustomerDistribution() {
  const total = sentimentTypes.reduce((sum, s) => sum + s.value, 0);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">情感分析分布</h3>
        <button className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <div className="space-y-5">
        {sentimentTypes.map((type, index) => (
          <div key={type.label} className="flex items-center gap-4">
            <div className={`w-10 h-10 ${type.bgColor} rounded-xl flex items-center justify-center flex-shrink-0`}>
              <type.icon className={`w-5 h-5 ${type.textColor}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium text-gray-700">{type.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-900">
                    {type.value.toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({((type.value / total) * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(type.value / maxValue) * 100}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 + 0.5, ease: 'easeOut' }}
                  className={`h-full ${type.color} rounded-full`}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">情感指数</span>
          <span className="font-semibold text-emerald-600">+0.72</span>
        </div>
      </div>
    </motion.div>
  );
}
