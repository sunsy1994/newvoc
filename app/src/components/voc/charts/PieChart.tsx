import { motion } from 'framer-motion';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { ChartCard } from '../../data/chartsData';

interface PieChartCardProps {
  card: ChartCard;
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

export default function PieChartCard({ card }: PieChartCardProps) {
  const data = card.data as Array<{ name: string; value: number; color: string }>;

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
          <RechartsPieChart margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={70}
              paddingAngle={2}
              dataKey="value"
              animationDuration={800}
              animationBegin={300}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value: string) => <span className="text-xs text-gray-600">{value}</span>}
            />
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
