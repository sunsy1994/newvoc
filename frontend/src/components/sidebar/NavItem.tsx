import Link from "next/link";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type NavItemProps = {
  label: string;
  href: string;
  icon: LucideIcon;
  active: boolean;
  variant: "primary" | "secondary";
  badge?: number;
};

export function NavItem({ label, href, icon: Icon, active, variant, badge }: NavItemProps) {
  const isPrimary = variant === "primary";

  return (
    <Link
      href={href}
      className={cn(
        "group flex h-9 items-center justify-between rounded-lg px-3 text-xs font-medium transition",
        isPrimary
          ? active
            ? "bg-[#5347CE] text-white shadow-[0_10px_18px_rgba(83,71,206,0.20)]"
            : "text-[#596070] hover:bg-[#f3f5fa] hover:text-[#151720]"
          : active
            ? "bg-white text-[#151720] shadow-[0_8px_18px_rgba(26,32,44,0.06)] ring-1 ring-[#e8ecf3]"
            : "text-[#707787] hover:bg-white hover:text-[#151720]",
      )}
    >
      <span className="flex min-w-0 items-center gap-2">
        <Icon className="h-4 w-4 shrink-0" />
        <span className="truncate">{label}</span>
      </span>
      {badge ? (
        <span className={cn("rounded-full px-1.5 text-[10px]", active ? "bg-white text-[#5347CE]" : "bg-[#eef1f6] text-[#596070]")}>
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
