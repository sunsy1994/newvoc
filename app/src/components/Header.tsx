import { motion } from 'framer-motion';
import {
  Search,
  Calendar,
  ChevronDown,
  Plus,
  Download,
  Sun,
  Bell,
  Maximize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function Header() {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-40"
    >
      {/* Left - Title */}
      <h1 className="text-2xl font-semibold text-gray-900">舆情分析工作台</h1>

      {/* Right - Actions */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索关键词、车型..."
            className="pl-10 pr-4 py-2 w-64 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">⌘K</span>
        </div>

        {/* Date Range */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-700">2025年1月1日 - 2月1日</span>
        </div>

        {/* Period Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-1">
              近30天
              <ChevronDown className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>近7天</DropdownMenuItem>
            <DropdownMenuItem>近30天</DropdownMenuItem>
            <DropdownMenuItem>近90天</DropdownMenuItem>
            <DropdownMenuItem>本年度</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Add Widget */}
        <Button variant="outline" size="sm" className="gap-2 hidden sm:flex">
          <Plus className="w-4 h-4" />
          添加组件
        </Button>

        {/* Export */}
        <Button size="sm" className="gap-2 bg-blue-600 hover:bg-blue-700">
          <Download className="w-4 h-4" />
          导出报告
        </Button>

        {/* Theme Toggle */}
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Sun className="w-5 h-5 text-gray-600" />
        </button>

        {/* Fullscreen */}
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors hidden md:flex">
          <Maximize2 className="w-5 h-5 text-gray-600" />
        </button>

        {/* Notifications */}
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User Avatar */}
        <Avatar className="w-9 h-9 cursor-pointer">
          <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face" />
          <AvatarFallback>管理员</AvatarFallback>
        </Avatar>
      </div>
    </motion.header>
  );
}
