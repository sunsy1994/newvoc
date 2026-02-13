import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const data = [
  { channel: '微博', value: 18500 },
  { channel: '抖音', value: 24600 },
  { channel: '小红书', value: 16200 },
  { channel: '知乎', value: 8900 },
  { channel: 'B站', value: 12400 },
  { channel: '汽车之家', value: 15800 },
  { channel: '懂车帝', value: 19300 },
];

const maxValue = Math.max(...data.map((d) => d.value));
const maxIndex = data.findIndex((d) => d.value === maxValue);

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-lg font-semibold text-gray-900">
          {payload[0].value.toLocaleString()} 条
        </p>
      </div>
    );
  }
  return null;
};

export default function MostDayActive() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">渠道声量分布</h3>
        <button className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <div className="h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 5, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="channel"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis hide />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
            <Bar dataKey="value" radius={[4, 4, 4, 4]} animationDuration={600} animationBegin={300}>
              {data.map((_entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={index === maxIndex ? '#2563EB' : '#E5E7EB'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Max value indicator */}
      <div className="flex justify-center mt-2">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">最高声量:</span>
          <span className="font-semibold text-gray-900">{maxValue.toLocaleString()}条</span>
          <span className="text-gray-500">来自 {data[maxIndex].channel}</span>
        </div>
      </div>
    </motion.div>
  );
}
