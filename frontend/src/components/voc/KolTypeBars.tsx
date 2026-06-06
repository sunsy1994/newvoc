import type { KolTypeDistributionItem } from "@/types/vocMarket";

type KolTypeBarsProps = {
  data: KolTypeDistributionItem[];
};

export function KolTypeBars({ data }: KolTypeBarsProps) {
  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-3xl bg-zinc-50 text-sm text-zinc-400">
        尚未维护KOL画像
      </div>
    );
  }

  const max = Math.max(...data.map((item) => item.kol_count), 1);

  return (
    <div className="space-y-4 rounded-3xl bg-zinc-50 p-4">
      {data.slice(0, 8).map((item) => (
        <div key={item.kol_main_type}>
          <div className="mb-2 flex justify-between gap-3 text-xs text-zinc-500">
            <span className="truncate">{item.kol_main_type}</span>
            <span>{item.kol_count}位</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-white">
            <div className="h-full rounded-full bg-zinc-900" style={{ width: `${(item.kol_count / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
