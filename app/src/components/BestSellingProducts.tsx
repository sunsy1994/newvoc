import { motion } from 'framer-motion';
import { TrendingUp, MessageCircle, Share2 } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Topic {
  id: string;
  name: string;
  mentions: number;
  sentiment: string;
  sentimentScore: number;
  trend: string;
  icon: React.ElementType;
  iconBg: string;
}

const topics: Topic[] = [
  {
    id: '#T001',
    name: '新能源续航表现',
    mentions: 23100,
    sentiment: '正面',
    sentimentScore: 4.5,
    trend: '+15.2%',
    icon: TrendingUp,
    iconBg: 'bg-emerald-100',
  },
  {
    id: '#T002',
    name: '智能驾驶体验',
    mentions: 18500,
    sentiment: '中性',
    sentimentScore: 3.8,
    trend: '+8.7%',
    icon: MessageCircle,
    iconBg: 'bg-blue-100',
  },
  {
    id: '#T003',
    name: '车内空间设计',
    mentions: 15200,
    sentiment: '正面',
    sentimentScore: 4.2,
    trend: '+12.3%',
    icon: Share2,
    iconBg: 'bg-purple-100',
  },
];

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case '正面':
      return 'text-emerald-600 bg-emerald-50';
    case '负面':
      return 'text-red-600 bg-red-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

export default function BestSellingProducts() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">热门话题排行</h3>
        <button className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-gray-100 hover:bg-transparent">
              <TableHead className="text-xs font-medium text-gray-500 uppercase">话题ID</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase">话题名称</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase text-right">提及量</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase text-right">情感倾向</TableHead>
              <TableHead className="text-xs font-medium text-gray-500 uppercase text-right">趋势</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {topics.map((topic, index) => (
              <motion.tr
                key={topic.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 + 0.5 }}
                className="border-gray-50 hover:bg-gray-50 transition-colors duration-150"
              >
                <TableCell className="text-sm text-gray-600 py-4">{topic.id}</TableCell>
                <TableCell className="py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${topic.iconBg} rounded-lg flex items-center justify-center`}>
                      <topic.icon className="w-5 h-5 text-gray-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-900 hover:underline cursor-pointer">
                      {topic.name}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-sm text-gray-600 text-right py-4">
                  {topic.mentions.toLocaleString()}
                </TableCell>
                <TableCell className="text-right py-4">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(topic.sentiment)}`}>
                    {topic.sentiment}
                  </span>
                </TableCell>
                <TableCell className="text-right py-4">
                  <div className="flex items-center justify-end gap-1 text-emerald-600">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm font-medium">{topic.trend}</span>
                  </div>
                </TableCell>
              </motion.tr>
            ))}
          </TableBody>
        </Table>
      </div>
    </motion.div>
  );
}
