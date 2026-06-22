import { Flame, TrendingUp } from "lucide-react";

export type EvidenceRankItem = {
  id: string;
  title: string;
  meta?: string;
  value: string;
  valueLabel?: string;
};

type EvidenceRankListProps = {
  items: EvidenceRankItem[];
  emptyText: string;
  onSelectItem?: (item: EvidenceRankItem) => void;
};

const MAX_EVIDENCE_RANK_ITEMS = 5;

function rankBadge(index: number) {
  if (index === 0) return "bg-[var(--theme-selected-bg)] text-[var(--theme-selected-border)]";
  if (index === 1) return "bg-[var(--theme-chip)] text-[var(--theme-primary)]";
  if (index === 2) return "bg-[var(--theme-soft-panel)] text-[var(--theme-muted)]";
  return "bg-[var(--theme-white)] text-[var(--theme-muted)]";
}

export function EvidenceRankList({ items, emptyText, onSelectItem }: EvidenceRankListProps) {
  const visibleItems = items.slice(0, MAX_EVIDENCE_RANK_ITEMS);

  if (!visibleItems.length) {
    return (
      <div className="flex h-52 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        {emptyText}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {visibleItems.map((item, index) => {
        const content = (
          <>
            <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-semibold ${rankBadge(index)}`}>
              {index < 3 ? <Flame className="h-3.5 w-3.5" /> : index + 1}
            </span>
            <span className="min-h-[44px] min-w-0 flex-1">
              <span className="block truncate text-sm font-semibold text-[var(--theme-title)]">{item.title}</span>
              <span className="mt-0.5 block truncate text-[11px] text-[var(--theme-muted)]">{item.meta ?? "\u00a0"}</span>
            </span>
            <span className="inline-flex shrink-0 items-center gap-1 rounded-lg bg-[var(--theme-white)] px-2 py-1 text-[11px] font-semibold text-[var(--theme-title)] shadow-[0_6px_14px_rgba(26,32,44,0.04)]">
              <TrendingUp className="h-3 w-3 text-[var(--voc-chart-4)]" />
              {item.valueLabel ? <span className="text-[var(--theme-muted)]">{item.valueLabel}</span> : null}
              {item.value}
            </span>
          </>
        );

        if (onSelectItem) {
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onSelectItem(item)}
              className="group flex w-full items-center gap-2 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2.5 text-left transition hover:bg-[var(--theme-hover-bg)]"
            >
              {content}
            </button>
          );
        }

        return (
          <div key={item.id} className="flex w-full items-center gap-2 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2.5">
            {content}
          </div>
        );
      })}
    </div>
  );
}
