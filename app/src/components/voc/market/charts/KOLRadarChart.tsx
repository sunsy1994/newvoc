import { motion } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { RadarData } from '../types';

interface KOLRadarChartProps {
  data: RadarData[];
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{payload[0].payload.dimension}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-xs text-gray-600" style={{ color: entry.color }}>
            {entry.name}: {entry.value}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function KOLRadarChart({ data }: KOLRadarChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL vs 真实车主口碑对比</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
            <PolarGrid stroke="#E5E7EB" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fill: '#6B7280', fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="circle"
            />
            <Radar
              name="KOL"
              dataKey="kolRatio"
              stroke="#2563EB"
              fill="#2563EB"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Radar
              name="车主"
              dataKey="ownerRatio"
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 洞察 */}
      <div className="bg-blue-50 p-3 rounded-lg">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-blue-700 font-semibold text-sm">最大差异</span>
        </div>
        <div className="text-xs text-gray-700">
          <span className="font-medium">智能维度:</span> KOL 92% vs 车主 65% (差距27分)
          <span className="text-gray-500 mx-2">|</span>
          <span className="text-red-600">KOL存在过度渲染</span>
        </div>
      </div>
    </motion.div>
  );
}
