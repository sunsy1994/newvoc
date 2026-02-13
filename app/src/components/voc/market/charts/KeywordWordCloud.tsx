import type { KeywordData } from '../types';
import SimpleWordCloud from './SimpleWordCloud';

interface KeywordWordCloudProps {
  data: KeywordData[];
}

const getSentimentColor = (sentiment: number) => {
  if (sentiment > 0.2) {
    return '#10b981'; // 绿色
  } else if (sentiment < -0.2) {
    return '#ef4444'; // 红色
  }
  return '#9ca3af'; // 灰色
};

export default function KeywordWordCloud({ data }: KeywordWordCloudProps) {
  const insight = (
    <div className="grid grid-cols-3 gap-3 text-xs">
      <div className="bg-emerald-50 p-2 rounded-lg">
        <div className="text-emerald-700 font-medium">TOP3正面</div>
        <div className="text-gray-600 mt-1">科技感、智能、设计</div>
      </div>
      <div className="bg-red-50 p-2 rounded-lg">
        <div className="text-red-700 font-medium">TOP1负面</div>
        <div className="text-gray-600 mt-1">价格贵、卡顿</div>
      </div>
      <div className="bg-amber-50 p-2 rounded-lg">
        <div className="text-amber-700 font-medium">新晋关键词</div>
        <div className="text-gray-600 mt-1">噪音 (+2.1%)</div>
      </div>
    </div>
  );

  return (
    <SimpleWordCloud
      data={data}
      title="心智关键词词云"
      getTextColor={getSentimentColor}
      insight={insight}
    />
  );
}
