import { PrimaryNav } from "@/components/sidebar/PrimaryNav";
import { SecondaryNav } from "@/components/sidebar/SecondaryNav";

export function Sidebar() {
  return (
    <aside className="w-[330px] shrink-0 border-r border-[#e8ecf3] bg-white">
      <div className="grid h-full grid-cols-[136px_1fr]">
        <section className="border-r border-[#eef1f6] p-3">
          <div className="mb-7 flex items-center gap-2 px-2 pt-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-[#5347CE] text-sm font-semibold text-white shadow-[0_10px_18px_rgba(83,71,206,0.24)]">
              A
            </div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-[#151720]">AutoVOC</div>
              <div className="truncate text-[11px] text-[#8b92a1]">VOC Console</div>
            </div>
          </div>
          <PrimaryNav />
        </section>
        <section className="bg-[#fbfcfe] p-3">
          <SecondaryNav />
        </section>
      </div>
    </aside>
  );
}
