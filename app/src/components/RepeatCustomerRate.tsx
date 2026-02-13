import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from 'recharts';

const data = [
  { name: 'Completed', value: 78 },
  { name: 'Remaining', value: 22 },
];

const COLORS = ['#2563EB', '#E5E7EB'];

function AnimatedPercentage({ value }: { value: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, {
      duration: 0.8,
      ease: 'easeOut',
      delay: 0.5,
    });
    return controls.stop;
  }, [count, value]);

  return (
    <span className="text-4xl font-bold text-gray-900">
      <motion.span>{rounded}</motion.span>
      <span className="text-2xl">%</span>
    </span>
  );
}

export default function RepeatCustomerRate() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">品牌口碑指数</h3>
        <button className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <div className="relative h-[160px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={70}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              stroke="none"
              animationBegin={300}
              animationDuration={800}
            >
              {data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <AnimatedPercentage value={78} />
        </div>
      </div>

      <div className="text-center mt-2">
        <p className="text-sm text-gray-500">行业平均: 65%</p>
        <button className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2">
          查看详情
        </button>
      </div>
    </motion.div>
  );
}
