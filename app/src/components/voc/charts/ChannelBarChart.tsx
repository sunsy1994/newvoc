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
import type { ChartCard } from '../../data/chartsData';

interface ChannelBarChartProps {
  card: ChartCard;
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-lg font-semibold text-gray-900">
          {payload[0].value.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

export default function ChannelBarChart({ card }: ChannelBarChartProps) {
  const data = card.data as any[];
  const maxValue = Math.max(...data.map((d) => d.value));

  // 为每个柱子生成颜色
  const getBarColor = (index: number) => {
    const colors = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE'];
    return colors[index % colors.length];
  };

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

      {/* 图表 */}
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
                <Cell key={`cell-${index}`} fill={getBarColor(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 最高值指示 */}
      <div className="flex justify-center mt-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">最高值:</span>
          <span className="font-semibold text-gray-900">{maxValue.toLocaleString()}</span>
        </div>
      </div>
    </motion.div>
  );
}
