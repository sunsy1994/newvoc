import { Suspense, lazy, useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import StatCard from './components/StatCard';
import TotalProfit from './components/TotalProfit';
import CustomerDistribution from './components/CustomerDistribution';
import MostDayActive from './components/MostDayActive';
import RepeatCustomerRate from './components/RepeatCustomerRate';
import BestSellingProducts from './components/BestSellingProducts';
import AIAssistant from './components/AIAssistant';

const VocViewPage = lazy(() => import('./components/voc/VocViewPage'));
const EventLibraryPage = lazy(() => import('./components/assets/EventLibraryPage'));
const ContentLibraryPage = lazy(() => import('./components/assets/ContentLibraryPage'));
const CommentLibraryPage = lazy(() => import('./components/assets/CommentLibraryPage'));
const KolLibraryPage = lazy(() => import('./components/assets/KolLibraryPage'));
const AuthorLibraryPage = lazy(() => import('./components/assets/AuthorLibraryPage'));

const statsData = [
  { title: '管理工作台', value: 44670, change: 24.4, comparison: '较上周期增长 8,760条', type: 'volume' as const, suffix: '' },
  { title: '供应商反馈', value: 2856, change: 15.8, comparison: '较上周期增长 390条', type: 'sentiment' as const, suffix: '' },
  { title: '事件传播分析', value: 156, change: -5.2, comparison: '较上周期减少 8个事件', type: 'spread' as const, suffix: '' },
  { title: 'KOL分析', value: 328, change: 12.3, comparison: '较上周期新增 36位KOL', type: 'kol' as const, suffix: '' },
];

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const handlePageChange = (page: string) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar currentPage={currentPage} onPageChange={handlePageChange} />

      {/* Main Content */}
      <div className="flex-1 ml-[260px]">
        {/* VOC View Page */}
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-sm text-gray-500">页面加载中...</div>}>
          {currentPage === 'voc' ? (
            <VocViewPage />
          ) : currentPage === 'event-library' ? (
            <EventLibraryPage />
          ) : currentPage === 'content-library' ? (
            <ContentLibraryPage onPageChange={handlePageChange} />
          ) : currentPage === 'comment-library' ? (
            <CommentLibraryPage onPageChange={handlePageChange} />
          ) : currentPage === 'kol-library' ? (
            <KolLibraryPage onPageChange={handlePageChange} />
          ) : currentPage === 'author-library' ? (
            <AuthorLibraryPage onPageChange={handlePageChange} />
          ) : (
            <>
              {/* Header */}
              <Header />

              {/* Dashboard Content */}
              <main className="p-6">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  {statsData.map((stat, index) => (
                    <StatCard
                      key={stat.title}
                      title={stat.title}
                      value={stat.value}
                      change={stat.change}
                      comparison={stat.comparison}
                      type={stat.type}
                      delay={index}
                      suffix={stat.suffix}
                    />
                  ))}
                </div>

                {/* Main Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                  {/* Left Column - 2/3 */}
                  <div className="lg:col-span-2 space-y-6">
                    <TotalProfit />
                    <CustomerDistribution />
                  </div>

                  {/* Right Column - 1/3 */}
                  <div className="space-y-6">
                    <MostDayActive />
                    <RepeatCustomerRate />
                  </div>
                </div>

                {/* Bottom Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left - Products Table */}
                  <div className="lg:col-span-2">
                    <BestSellingProducts />
                  </div>

                  {/* Right - AI Assistant */}
                  <div>
                    <AIAssistant />
                  </div>
                </div>
              </main>
            </>
          )}
        </Suspense>
      </div>
    </div>
  );
}

export default App;
