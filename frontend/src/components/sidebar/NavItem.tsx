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
        "group flex h-9 items-center justify-between rounded-full px-3 text-xs transition",
        isPrimary
          ? active
            ? "bg-zinc-950 text-white shadow-sm"
            : "text-zinc-600 hover:bg-white/70 hover:text-zinc-950"
          : active
            ? "bg-white text-zinc-950 shadow-sm"
            : "text-zinc-500 hover:bg-white/70 hover:text-zinc-950",
      )}
    >
      <span className="flex min-w-0 items-center gap-2">
        <Icon className="h-4 w-4 shrink-0" />
        <span className="truncate">{label}</span>
      </span>
      {badge ? (
        <span className={cn("rounded-full px-1.5 text-[10px]", active ? "bg-white text-zinc-950" : "bg-zinc-950 text-white")}>
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
