import { motion } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { ChannelQuadrantData } from '../types';

interface ChannelQuadrantChartProps {
  data: ChannelQuadrantData[];
}

const channelColors: Record<string, string> = {
  douyin: '#8B5CF6',
  qichezhijia: '#2563EB',
  dongchidi: '#059669',
  xiaohongshu: '#EC4899',
  weibo: '#F97316',
  other: '#9CA3AF',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.channel}</p>
        <p className="text-xs text-gray-600 mt-1">
          声量占比: {data.volumeShare}%
        </p>
        <p className="text-xs text-gray-600">
          互动率: {data.interactionRate}%
        </p>
        <p className="text-xs text-gray-600">
          正面占比: {data.positiveRatio}%
        </p>
      </div>
    );
  }
  return null;
};

export default function ChannelQuadrantChart({ data }: ChannelQuadrantChartProps) {
  const medianVolumeShare = 5;
  const medianInteractionRate = 4;

  // 计算气泡大小（基于正面占比）
  const maxPositiveRatio = Math.max(...data.map(d => d.positiveRatio));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">渠道效果四象限</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis
              type="number"
              dataKey="volumeShare"
              name="声量占比"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              label={{ value: '声量占比 (%)', position: 'insideBottom', offset: -5, fontSize: 11, fill: '#9CA3AF' }}
            />
            <YAxis
              type="number"
              dataKey="interactionRate"
              name="互动率"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              label={{ value: '互动率 (%)', angle: -90, position: 'insideLeft', offset: 5, fontSize: 11, fill: '#9CA3AF' }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

            {/* 象限分割线 */}
            <ReferenceLine segment={[{ x: medianVolumeShare, y: 0 }, { x: medianVolumeShare, y: 100 }]} stroke="#E5E7EB" strokeDasharray="3 3" />
            <ReferenceLine y={medianInteractionRate} stroke="#E5E7EB" strokeDasharray="3 3" />

            {/* 气泡 */}
            <Scatter data={data.map((d) => ({
              ...d,
              z: (d.positiveRatio / maxPositiveRatio) * 300 + 100,
            }))}>
              {data.map((entry, index) => (
                <circle
                  key={`circle-${index}`}
                  cx="0"
                  cy="0"
                  r={Math.sqrt((entry.positiveRatio / maxPositiveRatio) * 400 + 50)}
                  fill={channelColors[entry.category] || '#9CA3AF'}
                  fillOpacity={0.7}
                  stroke={channelColors[entry.category] || '#9CA3AF'}
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* 象限说明 */}
      <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          <span className="text-gray-600">核心渠道（高声量+高互动）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span className="text-gray-600">潜力渠道（低声量+高互动）</span>
        </div>
      </div>
    </motion.div>
  );
}
