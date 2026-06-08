import type { VolumeTrendPoint } from "@/types/vocMarket";

type VolumeTrendChartProps = {
  data: VolumeTrendPoint[];
};

type TrendKey = "content_count" | "comment_count" | "total_volume";

function buildPoints(data: VolumeTrendPoint[], key: TrendKey, max: number) {
  if (data.length === 1) {
    const y = 160 - ((data[0][key] || 0) / max) * 130;
    return `0,${y} 520,${y}`;
  }
  return data
    .map((item, index) => {
      const x = (index / Math.max(data.length - 1, 1)) * 520;
      const y = 160 - ((item[key] || 0) / max) * 130;
      return `${x},${y}`;
    })
    .join(" ");
}

export function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少发布时间，暂无法展示声量趋势
      </div>
    );
  }

  const max = Math.max(...data.map((item) => item.total_volume), 1);

  return (
    <div className="overflow-hidden rounded-2xl bg-[#f7f9fc] p-4">
      <svg viewBox="0 0 520 190" className="h-64 w-full" role="img" aria-label="声量趋势折线图">
        <line x1="0" y1="160" x2="520" y2="160" stroke="#e8ecf3" strokeWidth="1" />
        <line x1="0" y1="95" x2="520" y2="95" stroke="#eef1f6" strokeWidth="1" />
        <line x1="0" y1="30" x2="520" y2="30" stroke="#eef1f6" strokeWidth="1" />
        <polyline
          points={buildPoints(data, "total_volume", max)}
          fill="none"
          stroke="#5347CE"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="3"
        />
        <polyline
          points={buildPoints(data, "content_count", max)}
          fill="none"
          stroke="#4896FE"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
        />
        <polyline
          points={buildPoints(data, "comment_count", max)}
          fill="none"
          stroke="#16C8C7"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
        />
      </svg>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-[#6f7685]">
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#5347CE]" />总声量</span>
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#4896FE]" />主贴声量</span>
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#16C8C7]" />评论声量</span>
      </div>
    </div>
  );
}
