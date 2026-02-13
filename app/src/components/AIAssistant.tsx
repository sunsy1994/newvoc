import { motion } from 'framer-motion';
import { ExternalLink, Sparkles } from 'lucide-react';

export default function AIAssistant() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.45 }}
      whileHover={{ boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)' }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 h-full flex flex-col"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-base font-semibold text-gray-900">智能舆情助手</h3>
          <Sparkles className="w-4 h-4 text-amber-500" />
        </div>
        <button className="text-gray-400 hover:text-gray-600 transition-colors">
          <ExternalLink className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 flex items-center justify-center">
        <motion.div
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="relative"
        >
          {/* Blue sphere */}
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 shadow-lg shadow-blue-500/30">
            {/* Shine effect */}
            <div className="absolute top-3 left-4 w-8 h-4 bg-white/30 rounded-full transform -rotate-45 blur-sm"></div>
            {/* Inner glow */}
            <div className="absolute inset-2 rounded-full bg-gradient-to-tr from-blue-600/50 to-transparent"></div>
          </div>
          
          {/* Orbiting dots */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0"
          >
            <div className="absolute -top-1 left-1/2 w-2 h-2 bg-blue-400 rounded-full"></div>
          </motion.div>
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0"
          >
            <div className="absolute top-1/2 -right-2 w-1.5 h-1.5 bg-blue-300 rounded-full"></div>
          </motion.div>
        </motion.div>
      </div>

      <p className="text-sm text-gray-500 text-center mt-4">
        问我任何关于舆情分析的问题
      </p>
      
      <div className="mt-4 space-y-2">
        <button className="w-full text-left text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors">
          "本周负面舆情有哪些？"
        </button>
        <button className="w-full text-left text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors">
          "对比竞品口碑指数"
        </button>
      </div>
    </motion.div>
  );
}
