import type { KeywordData } from '../types';
import SimpleWordCloud from './SimpleWordCloud';

interface NegativeWordCloudProps {
  data: KeywordData[];
}

const getNegativeColor = () => {
  return '#ef4444'; // 红色
};

export default function NegativeWordCloud({ data }: NegativeWordCloudProps) {
  // 只显示负面关键词
  const negativeData = data.filter(d => d.sentiment < 0);

  const insight = (
    <div className="bg-red-50 p-3 rounded-lg">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-red-600 font-semibold text-sm">TOP3反感词</span>
        <span className="text-xs text-red-500 bg-red-100 px-2 py-0.5 rounded-full">负向信号: 中等</span>
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-700">
        <span>1. 价格贵</span>
        <span className="text-gray-400">|</span>
        <span>2. 卡顿</span>
        <span className="text-gray-400">|</span>
        <span>3. 性价比低</span>
      </div>
      <div className="mt-2 text-xs text-gray-500">
        建议：增加价格价值沟通内容，优先解决车机流畅度问题
      </div>
    </div>
  );

  return (
    <SimpleWordCloud
      data={negativeData}
      title="用户反感内容词云"
      getTextColor={getNegativeColor}
      insight={insight}
    />
  );
}
