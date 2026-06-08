import type { ChannelDistributionItem } from "@/types/vocMarket";

type ChannelStackedBarsProps = {
  data: ChannelDistributionItem[];
};

export function ChannelStackedBars({ data }: ChannelStackedBarsProps) {
  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少渠道字段，暂无法展示渠道分布
      </div>
    );
  }

  const max = Math.max(...data.map((item) => item.total_volume), 1);

  return (
    <div className="space-y-4 rounded-2xl bg-[#f7f9fc] p-4">
      {data.slice(0, 8).map((item) => {
        const contentWidth = `${(item.content_count / max) * 100}%`;
        const commentWidth = `${(item.comment_count / max) * 100}%`;
        return (
          <div key={item.channel}>
            <div className="mb-2 flex justify-between gap-3 text-xs text-[#6f7685]">
              <span className="truncate">{item.channel}</span>
              <span>{item.total_volume.toLocaleString("zh-CN")}</span>
            </div>
            <div className="flex h-3 overflow-hidden rounded-full bg-white">
              <div className="bg-[#4896FE]" style={{ width: contentWidth }} />
              <div className="bg-[#16C8C7]" style={{ width: commentWidth }} />
            </div>
          </div>
        );
      })}
      <div className="flex gap-4 text-xs text-[#6f7685]">
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#4896FE]" />主贴</span>
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#16C8C7]" />评论</span>
      </div>
    </div>
  );
}
