import { motion, AnimatePresence } from 'framer-motion';
import { departmentChartsData } from '../data/chartsData';
import TrendChart from './charts/TrendChart';
import ChannelBarChart from './charts/ChannelBarChart';
import SentimentBar from './charts/SentimentBar';
import DataTable from './charts/DataTable';
import PieChartCard from './charts/PieChart';
import RadarChartCard from './charts/RadarChart';

interface DepartmentChartsProps {
  selectedIndex: number;
}

export default function DepartmentCharts({ selectedIndex }: DepartmentChartsProps) {
  const currentDepartment = departmentChartsData[selectedIndex];
  const isProductDepartment = currentDepartment.department === 'product';

  return (
    <div className="mt-8">
      {/* 部门数据标题 */}
      <motion.div
        key={`chart-title-${selectedIndex}`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h2
          className={`text-center text-xl font-bold ${
            isProductDepartment
              ? 'bg-gradient-to-r from-blue-950 via-blue-700 to-cyan-500 bg-clip-text text-transparent'
              : 'text-gray-900'
          }`}
        >
          {currentDepartment.title} - 数据洞察
        </h2>
        {isProductDepartment && (
          <p className="mt-2 text-center text-xs text-blue-600">
            产品部主题：Blue Tech Insight · Futuristic BI
          </p>
        )}
      </motion.div>

      {/* 2x2 网格布局 */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className={`grid grid-cols-1 lg:grid-cols-2 gap-6 ${isProductDepartment ? 'relative' : ''}`}
        >
          {isProductDepartment && (
            <>
              <div className="pointer-events-none absolute -inset-2 -z-10 rounded-3xl border border-blue-200/70 bg-gradient-to-br from-[#f0f7ff]/90 via-[#f8fbff]/90 to-white" />
              <div className="pointer-events-none absolute -top-3 left-10 h-24 w-24 rounded-full bg-blue-300/30 blur-2xl" />
              <div className="pointer-events-none absolute -bottom-3 right-12 h-24 w-24 rounded-full bg-cyan-300/25 blur-2xl" />
            </>
          )}
          {currentDepartment.cards.map((card, index) => (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.08, duration: 0.35 }}
              whileHover={isProductDepartment ? { y: -6 } : undefined}
            >
              {card.type === 'trend' && <TrendChart card={card} />}
              {card.type === 'bar' && <ChannelBarChart card={card} />}
              {card.type === 'sentiment' && <SentimentBar card={card} />}
              {card.type === 'table' && <DataTable card={card} />}
              {card.type === 'pie' && <PieChartCard card={card} />}
              {card.type === 'radar' && <RadarChartCard card={card} />}
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
