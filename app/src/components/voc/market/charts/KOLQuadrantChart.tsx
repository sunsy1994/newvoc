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
  Label,
} from 'recharts';
import type { KOLInfluenceData } from '../types';

interface KOLQuadrantChartProps {
  data: KOLInfluenceData[];
}

const categoryColors: Record<string, string> = {
  pro: '#2563EB',
  tech: '#059669',
  fashion: '#EC4899',
  koc: '#F59E0B',
};

const categoryLabels: Record<string, string> = {
  pro: '专业车评',
  tech: '科技博主',
  fashion: '生活时尚',
  koc: '真实车主KOC',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.name}</p>
        <p className="text-xs text-gray-600 mt-1">
          类型: {categoryLabels[data.category]}
        </p>
        <p className="text-xs text-gray-600">
          互动率: {data.interactionRate}%
        </p>
        <p className="text-xs text-gray-600">
          信任度: {data.trustLevel}%
        </p>
        <p className="text-xs text-gray-600">
          粉丝: {(data.fans / 10000).toFixed(1)}万
        </p>
      </div>
    );
  }
  return null;
};

export default function KOLQuadrantChart({ data }: KOLQuadrantChartProps) {
  const trustThreshold = 60;
  const interactionThreshold = 4;

  // 计算气泡大小（基于粉丝数）
  const maxFans = Math.max(...data.map(d => d.fans));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL影响力矩阵</h3>
      </div>

      <div className="h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis
              type="number"
              dataKey="interactionRate"
              name="互动率"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            >
              <Label value="互动率 (%)" position="insideBottom" offset={-5} fontSize={11} fill="#9CA3AF" />
            </XAxis>
            <YAxis
              type="number"
              dataKey="trustLevel"
              name="信任度"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            >
              <Label value="信任度 (%)" angle={-90} position="insideLeft" offset={5} fontSize={11} fill="#9CA3AF" />
            </YAxis>
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

            {/* 象限分割线 */}
            <ReferenceLine segment={[{ x: interactionThreshold, y: 0 }, { x: interactionThreshold, y: 100 }]} stroke="#E5E7EB" strokeDasharray="3 3" />
            <ReferenceLine y={trustThreshold} stroke="#E5E7EB" strokeDasharray="3 3" />

            {/* 气泡 */}
            <Scatter data={data.map(d => ({ ...d, z: d.fans }))}>
              {data.map((entry, index) => (
                <circle
                  key={`circle-${index}`}
                  cx="0"
                  cy="0"
                  r={Math.sqrt((entry.fans / maxFans) * 500 + 50)}
                  fill={categoryColors[entry.category] || '#9CA3AF'}
                  fillOpacity={0.7}
                  stroke={categoryColors[entry.category] || '#9CA3AF'}
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* 图例和象限说明 */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        {/* 类型图例 */}
        <div className="flex flex-wrap gap-2 text-xs">
          {Object.entries(categoryLabels).map(([key, label]) => (
            <div key={key} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: categoryColors[key] }}></div>
              <span className="text-gray-600">{label}</span>
            </div>
          ))}
        </div>

        {/* 象限说明 */}
        <div className="flex items-center gap-3 text-xs text-gray-600">
          <span>右上: 核心合作</span>
          <span>左上: 专家型</span>
        </div>
      </div>
    </motion.div>
  );
}
