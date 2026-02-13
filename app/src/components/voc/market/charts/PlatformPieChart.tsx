import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import type { PlatformData } from '../types';

interface PlatformPieChartProps {
  data: PlatformData[];
}

const COLORS = {
  '垂直平台': '#1E40AF',
  '泛类平台': '#60A5FA',
  '抖音': '#8B5CF6',
  '微博': '#F97316',
  '小红书': '#EC4899',
  '其他': '#9CA3AF',
  '汽车之家': '#2563EB',
  '懂车帝': '#059669',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.name}</p>
        <p className="text-xs text-gray-600 mt-1">
          {data.value.toLocaleString()}条 ({data.percent.toFixed(1)}%)
        </p>
      </div>
    );
  }
  return null;
};

export default function PlatformPieChart({ data }: PlatformPieChartProps) {
  // 计算破圈指数
  const totalVolume = data.reduce((sum, d) => sum + d.volume, 0);
  const generalVolume = data.filter(d => d.category === 'general').reduce((sum, d) => sum + d.volume, 0);
  const breakoutIndex = ((generalVolume / totalVolume) * 100).toFixed(0);

  // 准备饼图数据 - 先分两大类
  const categoryData = [
    { name: '垂直平台', value: data.filter(d => d.category === 'vertical').reduce((sum, d) => sum + d.volume, 0) },
    { name: '泛类平台', value: data.filter(d => d.category === 'general').reduce((sum, d) => sum + d.volume, 0) },
  ];

  // 泛类平台细分数据
  const generalPlatformData = data.filter(d => d.category === 'general').map(d => ({
    name: d.platform,
    value: d.volume,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">破圈指数与平台声量占比</h3>
      </div>

      <div className="flex items-center gap-6">
        {/* 饼图 */}
        <div className="flex-1">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={2}
                dataKey="value"
              >
                <Cell fill={COLORS['垂直平台']} />
                <Cell fill={COLORS['泛类平台']} />
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 中心数字 */}
        <div className="absolute left-[30%] top-[55%] transform -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="text-3xl font-bold text-blue-600">{breakoutIndex}%</div>
          <div className="text-xs text-gray-500">破圈指数</div>
        </div>

        {/* 图例和细分 */}
        <div className="flex-1 space-y-3">
          {/* 大类图例 */}
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#1E40AF]"></div>
            <span className="text-xs text-gray-600">垂直平台</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#60A5FA]"></div>
            <span className="text-xs text-gray-600">泛类平台</span>
          </div>

          {/* 泛类平台细分 */}
          <div className="border-t border-gray-100 pt-3 space-y-2">
            {generalPlatformData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[item.name as keyof typeof COLORS] || '#9CA3AF' }}></div>
                  <span className="text-xs text-gray-600">{item.name}</span>
                </div>
                <span className="text-xs font-medium text-gray-900">{((item.value / totalVolume) * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
