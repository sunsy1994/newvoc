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
import { TrendingUp, TrendingDown } from 'lucide-react';
import type { ChartCard } from '../../data/chartsData';

interface TrendChartProps {
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

export default function TrendChart({ card }: TrendChartProps) {
  const data = card.data as any[];
  const isProductCard = card.id.startsWith('product-');
  const firstValue = data[0]?.value || 0;
  const lastValue = data[data.length - 1]?.value || 0;
  const change = ((lastValue - firstValue) / firstValue) * 100;
  const isPositive = change >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      whileHover={isProductCard ? { y: -4, boxShadow: '0 18px 40px -24px rgba(37, 99, 235, 0.55)' } : undefined}
      className={`rounded-2xl p-6 border transition-all duration-300 ${
        isProductCard
          ? 'bg-gradient-to-br from-white to-blue-50/60 border-blue-100 shadow-[0_10px_30px_-22px_rgba(37,99,235,0.65)]'
          : 'bg-white shadow-sm border-gray-100'
      }`}
    >
      {/* 标题 */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className={`text-base font-semibold mb-1 ${isProductCard ? 'text-blue-950' : 'text-gray-900'}`}>{card.title}</h3>
          {card.subtitle && (
            <p className="text-xs text-gray-500">{card.subtitle}</p>
          )}
        </div>
        {change !== 0 && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
            isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
          }`}>
            {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            <span>{isPositive ? '+' : ''}{change.toFixed(1)}%</span>
          </div>
        )}
      </div>

      {/* 图表 */}
      <div className="h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={`trendGradient-${card.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isProductCard ? '#0ea5e9' : '#2563EB'} stopOpacity={0.35} />
                <stop offset="95%" stopColor={isProductCard ? '#0ea5e9' : '#2563EB'} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              interval={1}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke={isProductCard ? '#0284c7' : '#2563EB'}
              strokeWidth={isProductCard ? 2.5 : 2}
              fill={`url(#trendGradient-${card.id})`}
              animationDuration={1200}
              animationEasing="ease-out"
              activeDot={{ r: isProductCard ? 5 : 4, fill: isProductCard ? '#0369a1' : '#2563EB' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
