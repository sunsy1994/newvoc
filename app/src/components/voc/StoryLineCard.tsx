import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, BarChart3, Lightbulb, AlertTriangle, CheckCircle, ChevronDown } from 'lucide-react';
import type { StoryLine } from '../data/storyLinesData';

interface StoryLineCardProps {
  story: StoryLine;
  delay?: number;
}

export default function StoryLineCard({ story, delay = 0 }: StoryLineCardProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300"
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{story.title}</h3>
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* 现象 */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Eye className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-blue-900">现象</h4>
          </div>
          <p className="text-sm text-blue-800 leading-relaxed">{story.phenomenon}</p>
        </div>

        {/* 数据支撑 */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-5 h-5 text-gray-600" />
            <h4 className="font-semibold text-gray-900">数据支撑</h4>
          </div>
          <ul className="space-y-2">
            {story.dataSupport.map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 mt-1.5 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* 业务解读 */}
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-green-900">业务解读</h4>
          </div>
          <p className="text-sm text-green-800 leading-relaxed">{story.interpretation}</p>
        </div>

        {/* 风险提示 */}
        <div className="bg-amber-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h4 className="font-semibold text-amber-900">风险提示</h4>
          </div>
          <p className="text-sm text-amber-800 leading-relaxed">{story.risk}</p>
        </div>

        {/* 行动建议 */}
        <div className="bg-gray-50 rounded-lg overflow-hidden">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <h4 className="font-semibold text-gray-900">行动建议</h4>
              <span className="text-xs text-gray-500">({story.actions.length}条)</span>
            </div>
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </motion.div>
          </button>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <ul className="px-4 pb-4 space-y-2">
                  {story.actions.map((action, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                        {index + 1}
                      </span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
