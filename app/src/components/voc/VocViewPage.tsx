import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, BookOpen, Search, Settings } from 'lucide-react';
import DepartmentTabs from './DepartmentTabs';
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
    <div className="min-h-screen bg-gradient-to-b from-[#f8f9fc] via-[#f4f6fb] to-[#eef2f7] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="rounded-3xl border border-gray-200/80 bg-white/90 p-4 shadow-sm backdrop-blur"
        >
          <div className="mb-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#1d4ed8]">
                <BookOpen className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900">VOC 看事件</p>
                <p className="text-xs text-gray-500">面向业务部门的用户声音 BI 看板</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="rounded-full p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-800">
                <Search className="h-4 w-4" />
              </button>
              <button className="rounded-full p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-800">
                <Settings className="h-4 w-4" />
              </button>
              <button className="rounded-full p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-800">
                <Bell className="h-4 w-4" />
              </button>
            </div>
          </div>

          <DepartmentTabs
            selectedIndex={selectedDepartment}
            onSelect={setSelectedDepartment}
          />

          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-gray-200 bg-gray-50/80 px-4 py-3">
            <div>
              <h1 className="text-3xl font-semibold text-gray-900">Good morning, BI Team</h1>
              <p className="mt-1 text-sm text-gray-500">VOC 事件洞察已按部门聚合，先完成市场部看板。</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Last month
              </button>
              <button className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Export report
              </button>
              {isMarketDepartment && (
                <AIReportButton onClick={() => setIsAIReportOpen(true)} />
              )}
            </div>
          </div>
        </motion.div>

        <AIReportModal
          isOpen={isAIReportOpen}
          onClose={() => setIsAIReportOpen(false)}
          data={aiReportData}
        />

        <main className="mx-auto max-w-7xl">
          {isMarketDepartment ? (
            <MarketDashboard />
          ) : (
            <div className="space-y-6">
              <StoryLineList selectedIndex={selectedDepartment} />
              <DepartmentCharts selectedIndex={selectedDepartment} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
