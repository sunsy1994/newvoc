import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { KOLTrendData } from '../types';

interface KOLTrendChartProps {
  data: KOLTrendData[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-xs text-gray-600 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value > 0 ? '+' : ''}{(entry.value * 100).toFixed(0)}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const kolColors: Record<string, string> = {
  'XX车评': '#2563EB',
  '科技博主A': '#059669',
  '时尚达人B': '#EC4899',
};

export default function KOLTrendChart({ data }: KOLTrendChartProps) {
  const kolNames = Object.keys(data[0]).filter(key => key !== 'week');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL立场变化趋势</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="week"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              domain={[-1, 1]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              tickFormatter={(value) => {
                if (value > 0) return `+${(value * 100).toFixed(0)}%`;
                return `${(value * 100).toFixed(0)}%`;
              }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* 零线参考 */}
            <ReferenceLine y={0} stroke="#E5E7EB" strokeDasharray="3 3" />

            {kolNames.map((kolName) => (
              <Line
                key={kolName}
                type="monotone"
                dataKey={kolName}
                stroke={kolColors[kolName] || '#9CA3AF'}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                animationDuration={800}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 洞察 */}
      <div className="flex gap-3 mt-4 text-xs">
        <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-lg">
          <span className="text-emerald-700 font-medium">立场转暖</span>
          <span className="text-gray-600">XX车评 (W-1 → W0: +13%)</span>
        </div>
        <div className="flex items-center gap-2 bg-red-50 px-3 py-2 rounded-lg">
          <span className="text-red-700 font-medium">立场转冷</span>
          <span className="text-gray-600">时尚达人B (W0 → W+1: -13%)</span>
        </div>
      </div>
    </motion.div>
  );
}
