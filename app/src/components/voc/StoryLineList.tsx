import { motion, AnimatePresence } from 'framer-motion';
import { storyLinesData } from '../data/storyLinesData';
import StoryLineCard from './StoryLineCard';

interface StoryLineListProps {
  selectedIndex: number;
}

export default function StoryLineList({ selectedIndex }: StoryLineListProps) {
  const selectedDepartment = storyLinesData[selectedIndex];

  return (
    <div className="space-y-6">
      {/* 部门标题 */}
      <motion.div
        key={`title-${selectedIndex}`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="text-center"
      >
        <h2 className="text-2xl font-bold text-gray-900">{selectedDepartment.title}</h2>
      </motion.div>

      {/* 故事线列表 */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedIndex}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {selectedDepartment.stories.map((story, index) => (
            <StoryLineCard key={story.id} story={story} delay={index * 0.1} />
          ))}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
