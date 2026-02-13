import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import ControlKnob from './ControlKnob';
import StoryLineList from './StoryLineList';
import DepartmentCharts from './DepartmentCharts';
import AIReportButton from './market/AIReportButton';
import AIReportModal from './market/AIReportModal';
import MarketDashboard from './market/MarketDashboard';
import { aiReportData } from './market/data/marketChartData';

export default function VocViewPage() {
  const [selectedDepartment, setSelectedDepartment] = useState(0);
  const [isAIReportOpen, setIsAIReportOpen] = useState(false);

  const isMarketDepartment = selectedDepartment === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white border-b border-gray-200"
      >
        <div className="px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">VOC看事件</h1>
              <p className="text-sm text-gray-500 mt-0.5">基于用户声音的业务洞察</p>
            </div>
          </div>
          {isMarketDepartment && (
            <AIReportButton onClick={() => setIsAIReportOpen(true)} />
          )}
        </div>
      </motion.div>

      <AIReportModal
        isOpen={isAIReportOpen}
        onClose={() => setIsAIReportOpen(false)}
        data={aiReportData}
      />

      <main className="p-6 max-w-7xl mx-auto">
        <ControlKnob
          selectedIndex={selectedDepartment}
          onSelect={setSelectedDepartment}
        />

        {isMarketDepartment ? (
          <>
            <StoryLineList selectedIndex={selectedDepartment} />
            <MarketDashboard />
          </>
        ) : (
          <>
            <StoryLineList selectedIndex={selectedDepartment} />
            <DepartmentCharts selectedIndex={selectedDepartment} />
          </>
        )}
      </main>
    </div>
  );
}
