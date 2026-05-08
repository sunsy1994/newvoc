import { useState, type ElementType } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  Database,
  Users,
  TrendingUp,
  Megaphone,
  Share2,
  Star,
  FileText,
  Settings,
  HelpCircle,
  ChevronDown,
  Crown,
  Car,
  BookOpen,
  UserRound,
  CarFront,
  FolderOpenDot,
  Workflow
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { AssetPage, AssetPageChangeHandler } from './assets/assetNavigation';

interface MenuItem {
  icon: ElementType;
  label: string;
  badge?: number;
  page?: AssetPage;
}

interface SubMenuItem {
  label: string;
  icon: ElementType;
  page?: AssetPage;
}

const mainMenuItems: MenuItem[] = [
  { icon: LayoutDashboard, label: '管理工作台', page: 'dashboard' },
  { icon: BookOpen, label: 'VOC看事件', page: 'voc' },
  { icon: MessageSquare, label: '供应商反馈', badge: 46 },
  { icon: Megaphone, label: '事件传播分析' },
  { icon: Users, label: 'KOL分析' },
];

const analysisSubItems: SubMenuItem[] = [
  { label: '事件库', icon: TrendingUp, page: 'event-library' },
  { label: '内容库', icon: BarChart3, page: 'content-library' },
  { label: '评论库', icon: FileText, page: 'comment-library' },
  { label: 'KOL库', icon: Users, page: 'kol-library' },
  { label: '作者库', icon: UserRound, page: 'author-library' },
  { label: '竞品资产库', icon: CarFront, page: 'competitor-library' },
];

const otherMenuItems: MenuItem[] = [
  { icon: Share2, label: '数据接入', page: 'data-access' },
  { icon: Star, label: '品牌口碑' },
];

const dataAccessSubItems: SubMenuItem[] = [
  { label: '数据导入', icon: FolderOpenDot, page: 'data-import' },
  { label: '数据计算', icon: Workflow, page: 'data-calc' },
];

const bottomMenuItems: MenuItem[] = [
  { icon: Settings, label: '系统设置' },
  { icon: HelpCircle, label: '帮助支持' },
];

interface SidebarProps {
  currentPage: string;
  onPageChange: AssetPageChangeHandler;
}

export default function Sidebar({ currentPage, onPageChange }: SidebarProps) {
  const [analysisOpen, setAnalysisOpen] = useState(true);
  const [dataAccessOpen, setDataAccessOpen] = useState(true);

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-[260px] h-screen bg-white border-r border-gray-200 flex flex-col fixed left-0 top-0 z-50"
    >
      {/* Logo */}
      <div className="h-[60px] flex items-center px-6 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Car className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-semibold text-gray-900">AutoVOC</span>
        </div>
      </div>

      {/* Main Menu */}
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="px-3 space-y-1">
          {mainMenuItems.map((item, index) => (
            <motion.button
              key={item.label}
              onClick={() => item.page && onPageChange(item.page)}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 + 0.2 }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                currentPage === item.page
                  ? 'bg-blue-50 text-blue-600 border-l-[3px] border-blue-600'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 text-xs">
                  {item.badge}
                </Badge>
              )}
            </motion.button>
          ))}
        </nav>

        {/* 数据资产 Section */}
        <div className="mt-4 px-3">
          <button
            onClick={() => setAnalysisOpen(!analysisOpen)}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors duration-150"
          >
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5" />
              <span>数据资产</span>
            </div>
            <motion.div
              animate={{ rotate: analysisOpen ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-4 h-4" />
            </motion.div>
          </button>

          <AnimatePresence>
            {analysisOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="overflow-hidden"
              >
                <div className="ml-8 mt-1 space-y-1">
                  {analysisSubItems.map((item, index) => (
                    <motion.button
                      key={item.label}
                      onClick={() => item.page && onPageChange(item.page)}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors duration-150 ${
                        currentPage === item.page
                          ? 'bg-blue-50 text-blue-600'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <item.icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Other Menu Items */}
        <nav className="mt-4 px-3 space-y-1">
          {otherMenuItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (index + mainMenuItems.length) * 0.05 + 0.3 }}
              className="space-y-1"
            >
              {item.page === 'data-access' ? (
                <>
                  <button
                    onClick={() => {
                      onPageChange('data-access');
                      setDataAccessOpen((prev) => !prev);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                      currentPage === item.page || currentPage === 'data-import' || currentPage === 'data-calc'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </div>
                    <motion.div animate={{ rotate: dataAccessOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                      <ChevronDown className="w-4 h-4" />
                    </motion.div>
                  </button>

                  <AnimatePresence>
                    {dataAccessOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25 }}
                        className="overflow-hidden"
                      >
                        <div className="ml-8 space-y-1">
                          {dataAccessSubItems.map((subItem) => (
                            <button
                              key={subItem.label}
                              onClick={() => subItem.page && onPageChange(subItem.page)}
                              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors duration-150 ${
                                currentPage === subItem.page
                                  ? 'bg-blue-50 text-blue-600'
                                  : 'text-gray-600 hover:bg-gray-100'
                              }`}
                            >
                              <subItem.icon className="w-4 h-4" />
                              <span>{subItem.label}</span>
                            </button>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </>
              ) : (
                <a
                  href="#"
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors duration-150"
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </a>
              )}
            </motion.div>
          ))}
        </nav>

        {/* Bottom Menu */}
        <nav className="mt-8 px-3 space-y-1">
          {bottomMenuItems.map((item, index) => (
            <motion.a
              key={item.label}
              href="#"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: (index + mainMenuItems.length + otherMenuItems.length) * 0.05 + 0.4 }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors duration-150"
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </motion.a>
          ))}
        </nav>
      </div>

      {/* Upgrade Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="p-4 mx-4 mb-4"
      >
        <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-4 text-white">
          <div className="flex items-center gap-2 mb-2">
            <Crown className="w-5 h-5" />
          </div>
          <h4 className="font-semibold text-sm mb-1">升级专业版！</h4>
          <p className="text-xs text-blue-100 mb-3">解锁更多高级分析功能和数据源。</p>
          <Button 
            variant="secondary" 
            size="sm" 
            className="w-full bg-white text-blue-600 hover:bg-blue-50 text-xs font-medium"
          >
            立即升级
          </Button>
        </div>
      </motion.div>
    </motion.aside>
  );
}
