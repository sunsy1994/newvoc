import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { ChartCard } from '../../data/chartsData';

interface DataTableProps {
  card: ChartCard;
}

const getChangeIcon = (change?: number) => {
  if (!change) return Minus;
  return change > 0 ? TrendingUp : TrendingDown;
};

const getChangeColor = (change?: number) => {
  if (!change) return 'text-gray-600';
  return change > 0 ? 'text-emerald-600' : 'text-red-600';
};

export default function DataTable({ card }: DataTableProps) {
  const data = card.data as Array<{ name: string; value: number | string; change?: number }>;

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

      {/* 表格 */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-gray-100 hover:bg-transparent">
              <TableHead className="text-xs font-medium text-gray-500 uppercase">名称</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase text-right">数值</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase text-right">变化</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item, index) => {
              const ChangeIcon = getChangeIcon(item.change);

              return (
                <motion.tr
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 + 0.3 }}
                  className="border-gray-50 hover:bg-gray-50 transition-colors duration-150"
                >
                  <TableCell className="text-sm text-gray-900 py-3 font-medium">
                    {item.name}
                  </TableCell>
                  <TableCell className="text-sm text-gray-600 text-right py-3">
                    {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
                  </TableCell>
                  <TableCell className="text-right py-3">
                    {item.change !== undefined ? (
                      <div className={`flex items-center justify-end gap-1 ${getChangeColor(item.change)}`}>
                        <ChangeIcon className="w-4 h-4" />
                        <span className="text-sm font-medium">
                          {item.change > 0 ? '+' : ''}{item.change}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">-</span>
                    )}
                  </TableCell>
                </motion.tr>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </motion.div>
  );
}
