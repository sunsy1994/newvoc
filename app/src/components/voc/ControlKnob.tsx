import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { storyLinesData } from '../data/storyLinesData';

interface ControlKnobProps {
  selectedIndex: number;
  onSelect: (index: number) => void;
}

export default function ControlKnob({ selectedIndex, onSelect }: ControlKnobProps) {
  const handlePrevious = () => {
    const newIndex = selectedIndex === 0 ? storyLinesData.length - 1 : selectedIndex - 1;
    onSelect(newIndex);
  };

  const handleNext = () => {
    const newIndex = selectedIndex === storyLinesData.length - 1 ? 0 : selectedIndex + 1;
    onSelect(newIndex);
  };

  // 计算旋钮旋转角度（每个部门72度，共5个部门=360度）
  const rotationAngle = selectedIndex * 72;

  return (
    <div className="flex items-center justify-center gap-6 mb-8">
      {/* 左按钮 */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={handlePrevious}
        className="w-14 h-14 rounded-full bg-gray-800 text-white flex items-center justify-center shadow-lg hover:bg-gray-700 transition-colors"
        aria-label="上一个部门"
      >
        <ChevronLeft className="w-6 h-6" />
      </motion.button>

      {/* 旋钮主体 */}
      <div className="relative">
        {/* 外圈装饰 */}
        <div className="absolute inset-0 rounded-full border-4 border-gray-300"></div>

        {/* 旋钮 */}
        <motion.div
          animate={{ rotate: rotationAngle }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="relative w-32 h-32 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 shadow-2xl flex items-center justify-center border-4 border-gray-600"
        >
          {/* 旋钮纹理 */}
          <div className="absolute inset-2 rounded-full border border-gray-700 opacity-50"></div>
          <div className="absolute inset-4 rounded-full border border-dashed border-gray-600 opacity-30"></div>

          {/* 指示器 */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 w-1 h-4 bg-orange-500 rounded-full"></div>

          {/* 中心显示区域 */}
          <div className="relative z-10 text-center">
            <motion.div
              key={selectedIndex}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
              className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg"
            >
              <span className="text-white text-2xl font-bold">{selectedIndex + 1}</span>
            </motion.div>
            <motion.p
              key={`label-${selectedIndex}`}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
              className="text-gray-400 text-xs mt-2 font-medium"
            >
              {storyLinesData[selectedIndex].label}
            </motion.p>
          </div>
        </motion.div>

        {/* 底部刻度 */}
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex gap-1">
          {storyLinesData.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all ${
                index === selectedIndex ? 'bg-orange-500 scale-125' : 'bg-gray-400'
              }`}
            />
          ))}
        </div>
      </div>

      {/* 右按钮 */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleNext}
        className="w-14 h-14 rounded-full bg-gray-800 text-white flex items-center justify-center shadow-lg hover:bg-gray-700 transition-colors"
        aria-label="下一个部门"
      >
        <ChevronRight className="w-6 h-6" />
      </motion.button>
    </div>
  );
}
