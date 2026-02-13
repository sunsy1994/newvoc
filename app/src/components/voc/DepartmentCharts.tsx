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

  return (
    <div className="mt-8">
      {/* 部门数据标题 */}
      <motion.div
        key={`chart-title-${selectedIndex}`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h2 className="text-xl font-bold text-gray-900 text-center">
          {currentDepartment.title} - 数据洞察
        </h2>
      </motion.div>

      {/* 2x2 网格布局 */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {currentDepartment.cards.map((card, index) => (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
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
