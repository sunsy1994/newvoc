import { motion } from 'framer-motion';

interface DepartmentTabsProps {
  selectedIndex: number;
  onSelect: (index: number) => void;
}

const departmentOptions = ['市场部', '产品部', '销售部', '市场部', '公关部'];

export default function DepartmentTabs({ selectedIndex, onSelect }: DepartmentTabsProps) {
  return (
    <div className="mb-8 overflow-x-auto">
      <div className="inline-flex min-w-max rounded-full border border-gray-200 bg-white p-1 shadow-sm">
        {departmentOptions.map((label, index) => (
          <button
            key={`${label}-${index}`}
            onClick={() => onSelect(index)}
            className="relative rounded-full px-5 py-2.5 text-sm font-medium transition-colors duration-200 min-w-[88px]"
          >
            {selectedIndex === index ? (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 rounded-full bg-[#111827] shadow-sm"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
              />
            ) : null}
            <span className={`relative z-10 ${selectedIndex === index ? 'text-white' : 'text-gray-600'}`}>
              {label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
