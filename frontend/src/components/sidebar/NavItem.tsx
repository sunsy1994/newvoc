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
        "group flex h-9 items-center justify-between rounded-[10px] px-3 text-[13px] font-medium transition-all duration-200 ease-out",
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
        <span className="truncate">{label}</span>
      </span>
      {badge ? (
        <span className={cn("rounded-full px-1.5 text-[10px]", active ? "bg-white text-[var(--sys-icon-fill)]" : "bg-[var(--sys-panel-bg)] text-[var(--sys-body)]")}>
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
