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
        scale: [1, 1.05, 1],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      className="relative flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg shadow-blue-500/30"
    >
      <motion.div
        animate={{
          opacity: [0.5, 1, 0.5],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute inset-0 bg-blue-400 rounded-xl blur-lg -z-10"
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

      <span className="text-sm font-medium">AI摘要</span>
    </motion.button>
  );
}
