import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp } from 'lucide-react';

const data = [
  { date: '1月1日', value: 12500 },
  { date: '1月4日', value: 15200 },
  { date: '1月7日', value: 13800 },
  { date: '1月10日', value: 18600 },
  { date: '1月13日', value: 22400 },
  { date: '1月16日', value: 25800 },
  { date: '1月19日', value: 31200 },
  { date: '1月22日', value: 28900 },
  { date: '1月25日', value: 35600 },
  { date: '1月28日', value: 41200 },
  { date: '1月29日', value: 44670 },
];

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

export default function TotalProfit() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">总声量趋势</h3>
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold text-gray-900">44.67万</span>
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-medium">
              <TrendingUp className="w-3 h-3" />
              <span>+24.4%</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-1">较上周期</p>
        </div>
      </div>

      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              interval={2}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              tickFormatter={(value) => `${(value / 10000).toFixed(0)}万`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#2563EB"
              strokeWidth={2}
              fill="url(#colorValue)"
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
