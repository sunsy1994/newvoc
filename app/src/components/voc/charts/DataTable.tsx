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
  return change > 0 ? 'text-blue-600' : 'text-indigo-600';
};

export default function DataTable({ card }: DataTableProps) {
  const data = card.data as Array<{ name: string; value: number | string; change?: number }>;
  const isProductCard = card.id.startsWith('product-');

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      whileHover={isProductCard ? { y: -4, boxShadow: '0 18px 40px -24px rgba(30, 64, 175, 0.45)' } : undefined}
      className={`rounded-2xl p-6 border transition-all duration-300 ${
        isProductCard
          ? 'border-blue-200/70 bg-gradient-to-br from-[#f6faff] via-[#f1f7ff] to-[#eaf4ff] shadow-[0_14px_36px_-24px_rgba(30,64,175,0.72)]'
          : 'bg-white shadow-sm border-gray-100'
      }`}
    >
      {/* 标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className={`text-base font-semibold mb-1 ${isProductCard ? 'text-blue-950' : 'text-gray-900'}`}>{card.title}</h3>
          {card.subtitle && (
            <p className="text-xs text-gray-500">{card.subtitle}</p>
          )}
        </div>
      </div>

      {/* 表格 */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
              <TableRow className={`hover:bg-transparent ${isProductCard ? 'border-blue-100 bg-blue-50/60' : 'border-gray-100'}`}>
              <TableHead className={`text-xs font-medium uppercase ${isProductCard ? 'text-blue-500' : 'text-gray-500'}`}>名称</TableHead>
              <TableHead className={`text-xs font-medium uppercase text-right ${isProductCard ? 'text-blue-500' : 'text-gray-500'}`}>数值</TableHead>
              <TableHead className={`text-xs font-medium uppercase text-right ${isProductCard ? 'text-blue-500' : 'text-gray-500'}`}>变化</TableHead>
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
                  className={`border-gray-50 transition-colors duration-150 ${
                    isProductCard ? 'hover:bg-blue-50/70' : 'hover:bg-gray-50'
                  }`}
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
                      <span className={`text-sm ${isProductCard ? 'text-blue-300' : 'text-gray-400'}`}>-</span>
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
