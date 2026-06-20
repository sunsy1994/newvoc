import { PrimaryNav } from "@/components/sidebar/PrimaryNav";
import { SecondaryNav } from "@/components/sidebar/SecondaryNav";

export function Sidebar() {
  return (
    <aside className="w-[330px] shrink-0 border-r border-[var(--sys-border)] bg-[var(--sys-card)]">
      <div className="grid h-full grid-cols-[140px_1fr]">
        <section className="border-r border-[var(--sys-border)] p-4">
          <div className="mb-7 flex items-center gap-2 px-2 pt-2">
            <div className="grid h-9 w-9 place-items-center rounded-[11px] bg-[var(--sys-icon-fill)] text-sm font-semibold text-white shadow-[var(--sys-btn-shadow)]">
              A
            </div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-[var(--sys-ink)]">AutoVOC</div>
              <div className="truncate text-[11px] text-[var(--sys-muted)]">VOC Console</div>
            </div>
          </div>
          <PrimaryNav />
        </section>
        <section className="bg-[var(--sys-panel-bg)] p-4">
          <SecondaryNav />
        </section>
      </div>
    </aside>
  );
}
