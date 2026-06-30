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
        "group flex min-h-10 items-center justify-between rounded-[11px] px-3 text-[13px] font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:shadow-[var(--sys-focus-ring)] max-lg:justify-center",
        isPrimary
          ? active
            ? "bg-[var(--sys-icon-fill)] text-white shadow-[var(--sys-btn-shadow)]"
            : "text-[var(--sys-body)] hover:bg-[var(--sys-panel-bg)] hover:text-[var(--sys-ink)]"
          : active
            ? "bg-[var(--sys-card)] text-[var(--sys-ink)] shadow-[var(--sys-card-shadow)] ring-1 ring-[var(--sys-border)]"
            : "text-[var(--sys-muted)] hover:bg-[var(--sys-card)] hover:text-[var(--sys-ink)]",
      )}
    >
      <span className="flex min-w-0 items-center gap-2">
        <Icon className="h-4 w-4 shrink-0" />
        <span className="truncate max-lg:hidden">{label}</span>
      </span>
      {badge ? (
        <span className={cn("rounded-full px-1.5 text-[10px] max-lg:hidden", active ? "bg-white text-[var(--sys-icon-fill)]" : "bg-[var(--sys-panel-bg)] text-[var(--sys-body)]")}>
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
