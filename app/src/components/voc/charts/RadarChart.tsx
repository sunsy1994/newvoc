import { motion } from 'framer-motion';
import {
  RadarChart as RechartsRadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { ChartCard } from '../../data/chartsData';

interface RadarChartCardProps {
  card: ChartCard;
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm text-gray-600 mb-1">{payload[0].name}</p>
        <p className="text-lg font-semibold text-gray-900">
          {payload[0].value}分
        </p>
      </div>
    );
  }
  return null;
};

export default function RadarChartCard({ card }: RadarChartCardProps) {
  const data = card.data as Array<{ category: string; value: number }>;

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
      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsRadarChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <PolarGrid stroke="#E5E7EB" strokeWidth={1} />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <PolarRadiusAxis
              axisLine={false}
              tick={false}
              tickCount={5}
            />
            <Radar
              name="评分"
              dataKey="value"
              stroke="#2563EB"
              fill="#2563EB"
              fillOpacity={0.3}
              strokeWidth={2}
              animationDuration={800}
              animationBegin={300}
            />
            <Tooltip content={<CustomTooltip />} />
          </RechartsRadarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
