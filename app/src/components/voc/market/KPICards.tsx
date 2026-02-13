import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';
import { TrendingUp, TrendingDown, Volume2, Target, MessageCircle, Heart, Users, AlertCircle } from 'lucide-react';
import type { KPIData } from './types';

interface KPICardsProps {
  data: KPIData[];
}

const icons = {
  volume: Volume2,
  index: Target,
  interaction: MessageCircle,
  nps: Heart,
  kol: Users,
  negative: AlertCircle,
};

function AnimatedNumber({ value }: { value: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => {
    if (value >= 10000) {
      return (latest / 10000).toFixed(1) + '万';
    }
    return Math.round(latest).toLocaleString();
  });

  useEffect(() => {
    const controls = animate(count, value, {
      duration: 1,
      ease: 'easeOut',
    });
    return controls.stop;
  }, [count, value]);

  return <motion.span>{rounded}</motion.span>;
}

export default function KPICards({ data }: KPICardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {data.map((item, index) => {
        const Icon = icons[item.type];
        const isPositive = item.change >= 0;

        return (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            whileHover={{ y: -2, boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)' }}
            className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 transition-shadow duration-200"
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-xs font-medium text-gray-600">{item.title}</span>
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <Icon className="w-4 h-4 text-blue-600" />
              </div>
            </div>

            <div className="flex items-baseline gap-2 mb-2">
              <h3 className="text-2xl font-bold text-gray-900">
                <AnimatedNumber value={typeof item.value === 'number' ? item.value : 0} />
                {item.suffix && <span className="text-sm">{item.suffix}</span>}
              </h3>
              <div
                className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-xs font-medium ${
                  isPositive
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-2.5 h-2.5" />
                ) : (
                  <TrendingDown className="w-2.5 h-2.5" />
                )}
                <span>{isPositive ? '+' : ''}{item.change}%</span>
              </div>
            </div>

            <p className="text-xs text-gray-500">{item.comparison}</p>
          </motion.div>
        );
      })}
    </div>
  );
}
