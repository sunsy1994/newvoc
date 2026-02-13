import { motion } from 'framer-motion';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';
import type { VolumeTrendData } from '../types';

interface VolumeTrendChartProps {
  data: VolumeTrendData[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-xs text-gray-600 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  const milestoneData = data.filter(d => d.milestone);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">声量趋势与竞品对比</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              yAxisId="left"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="circle"
            />

            {/* 营销节点参考线 */}
            {milestoneData.map((d, i) => (
              <ReferenceLine
                key={i}
                x={d.date}
                yAxisId="left"
                stroke="#F59E0B"
                strokeDasharray="3 3"
                label={{
                  value: d.milestone || '',
                  position: 'top',
                  fontSize: 11,
                  fill: '#F59E0B',
                }}
              />
            ))}

            <Bar yAxisId="left" dataKey="myVolume" name="我方声量" fill="#2563EB" radius={[4, 4, 0, 0]} animationDuration={800}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.milestone ? '#3B82F6' : '#2563EB'} />
              ))}
            </Bar>
            <Line yAxisId="right" type="monotone" dataKey="interaction" name="互动量" stroke="#1E40AF" strokeWidth={2} dot={{ r: 3 }} animationDuration={800} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
