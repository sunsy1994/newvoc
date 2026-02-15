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
      <div className="rounded-lg border border-blue-100 bg-white p-3 shadow-lg">
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
          ? 'border-blue-200/70 bg-gradient-to-br from-[#f6faff] via-[#f2f8ff] to-[#eaf4ff] shadow-[0_14px_36px_-24px_rgba(37,99,235,0.75)]'
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
            isPositive ? 'bg-blue-100 text-blue-700' : 'bg-indigo-100 text-indigo-700'
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
                <stop offset="5%" stopColor={isProductCard ? '#3b82f6' : '#2563EB'} stopOpacity={0.4} />
                <stop offset="55%" stopColor={isProductCard ? '#38bdf8' : '#2563EB'} stopOpacity={0.24} />
                <stop offset="95%" stopColor={isProductCard ? '#38bdf8' : '#2563EB'} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isProductCard ? '#dbeafe' : '#F3F4F6'} vertical={false} />
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
              stroke={isProductCard ? '#2563eb' : '#2563EB'}
              strokeWidth={isProductCard ? 2.5 : 2}
              fill={`url(#trendGradient-${card.id})`}
              animationDuration={1200}
              animationEasing="ease-out"
              activeDot={{ r: isProductCard ? 5 : 4, fill: isProductCard ? '#1d4ed8' : '#2563EB' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
