import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface AIReportButtonProps {
  onClick: () => void;
}

export default function AIReportButton({ onClick }: AIReportButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      animate={{
        scale: [1, 1.03, 1],
      }}
      transition={{
        duration: 2.8,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      whileHover={{ scale: 1.06, y: -1 }}
      whileTap={{ scale: 0.95 }}
      className="group relative flex items-center gap-2 overflow-hidden rounded-xl border border-white/30 bg-gradient-to-r from-[#1d4ed8] via-[#2563eb] to-[#4f46e5] px-4 py-2 text-white shadow-[0_10px_24px_-10px_rgba(79,70,229,0.85)] transition-all duration-300 hover:shadow-[0_14px_30px_-12px_rgba(79,70,229,0.95)]"
    >
      <motion.div
        animate={{
          opacity: [0.35, 0.7, 0.35],
          scale: [1, 1.12, 1],
        }}
        transition={{
          duration: 2.2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute -inset-1 -z-10 rounded-xl bg-gradient-to-r from-blue-500 via-blue-400 to-indigo-400 blur-md"
      />
      <motion.span
        animate={{ x: ['-120%', '130%'] }}
        transition={{ duration: 2.4, repeat: Infinity, ease: 'linear' }}
        className="pointer-events-none absolute inset-y-0 w-10 bg-white/30 blur-sm"
      />

      <div className="relative">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-0"
        >
          <div className="absolute -top-0.5 left-1/2 w-1 h-1 bg-white rounded-full"></div>
        </motion.div>
        <Sparkles className="w-4 h-4" />
      </div>

      <span className="text-sm font-semibold tracking-[0.01em]">AI摘要</span>
    </motion.button>
  );
}
