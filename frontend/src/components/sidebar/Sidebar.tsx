import { PrimaryNav } from "@/components/sidebar/PrimaryNav";
import { SecondaryNav } from "@/components/sidebar/SecondaryNav";

export function Sidebar() {
  return (
    <aside className="w-[332px] shrink-0 rounded-[28px] border border-white/70 bg-zinc-100/80 p-3 shadow-soft backdrop-blur-xl">
      <div className="grid h-full grid-cols-[136px_1fr] gap-2">
        <section className="rounded-[22px] bg-white/45 p-3">
          <div className="mb-6 flex items-center gap-2 px-2">
            <div className="grid h-9 w-9 place-items-center rounded-2xl bg-zinc-950 text-sm font-semibold text-white">A</div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-zinc-950">AutoVOC</div>
              <div className="truncate text-[11px] text-zinc-500">SaaS Console</div>
            </div>
          </div>
          <PrimaryNav />
        </section>
        <section className="rounded-[22px] bg-white/35 p-3">
          <SecondaryNav />
        </section>
      </div>
    </aside>
  );
}
