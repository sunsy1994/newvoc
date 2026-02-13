import { motion } from 'framer-motion';
import { storyLinesData } from '../data/storyLinesData';

interface DepartmentTabsProps {
  selectedIndex: number;
  onSelect: (index: number) => void;
}

export default function DepartmentTabs({ selectedIndex, onSelect }: DepartmentTabsProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="inline-flex bg-gray-100 rounded-full p-1">
        {storyLinesData.map((dept, index) => (
          <button
            key={dept.department}
            onClick={() => onSelect(index)}
            className="relative px-6 py-2.5 rounded-full text-sm font-medium transition-colors duration-200 min-w-[80px]"
          >
            {selectedIndex === index ? (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-white rounded-full shadow-sm"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
              />
            ) : null}
            <span className={`relative z-10 ${selectedIndex === index ? 'text-gray-900' : 'text-gray-500'}`}>
              {dept.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
