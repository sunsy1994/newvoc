"use client";

import { usePathname } from "next/navigation";

import { navigation } from "@/config/navigation";
import { NavItem } from "@/components/sidebar/NavItem";

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function PrimaryNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      <div className="mb-4 px-3 pt-2 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--sys-subtle)]">General</div>
      {navigation.map((item) => (
        <NavItem
          key={item.href}
          label={item.label}
          href={item.children?.[0]?.href ?? item.href}
          icon={item.icon}
          active={isActive(pathname, item.href)}
          variant="primary"
          badge={item.badge}
        />
      ))}
    </nav>
  );
}
