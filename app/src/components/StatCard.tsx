import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';
import { TrendingUp, TrendingDown, Volume2, MessageCircle, Share2, Users } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: number;
  change: number;
  comparison: string;
  type: 'volume' | 'sentiment' | 'spread' | 'kol';
  delay?: number;
  suffix?: string;
}

const icons = {
  volume: Volume2,
  sentiment: MessageCircle,
  spread: Share2,
  kol: Users,
};

function AnimatedNumber({ value, suffix = '' }: { value: number; suffix?: string }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest).toLocaleString());

  useEffect(() => {
    const controls = animate(count, value, {
      duration: 1,
      ease: 'easeOut',
    });
    return controls.stop;
  }, [count, value]);

  return (
    <span>
      <motion.span>{rounded}</motion.span>
      {suffix && <span className="text-xl">{suffix}</span>}
    </span>
  );
}

export default function StatCard({ title, value, change, comparison, type, delay = 0, suffix = '' }: StatCardProps) {
  const Icon = icons[type];
  const isPositive = change >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: delay * 0.05 + 0.2 }}
      whileHover={{ y: -2, boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)' }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 transition-shadow duration-200"
    >
      <div className="flex items-start justify-between mb-4">
        <span className="text-sm font-medium text-gray-600">{title}</span>
        <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
      </div>

      <div className="flex items-baseline gap-3 mb-2">
        <h3 className="text-3xl font-bold text-gray-900">
          <AnimatedNumber value={value} suffix={suffix} />
        </h3>
        <div
          className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
            isPositive
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {isPositive ? (
            <TrendingUp className="w-3 h-3" />
          ) : (
            <TrendingDown className="w-3 h-3" />
          )}
          <span>{isPositive ? '+' : ''}{change}%</span>
        </div>
      </div>

      <p className="text-xs text-gray-500">{comparison}</p>
    </motion.div>
  );
}
