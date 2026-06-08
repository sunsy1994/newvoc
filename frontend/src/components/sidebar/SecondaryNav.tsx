"use client";

import { FolderClosed } from "lucide-react";
import { usePathname } from "next/navigation";

import { navigation } from "@/config/navigation";
import { NavItem } from "@/components/sidebar/NavItem";

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function SecondaryNav() {
  const pathname = usePathname();
  const activePrimary = navigation.find((item) => isActive(pathname, item.href)) ?? navigation[0];
  const children = activePrimary.children ?? [];

  return (
    <nav className="flex flex-col gap-1">
      <div className="mb-3 flex items-center justify-between px-3 pt-2 text-[10px] font-semibold uppercase tracking-wide text-[#a1a7b3]">
        <span>{activePrimary.label}</span>
        <FolderClosed className="h-3.5 w-3.5" />
      </div>
      {children.map((item) => (
        <NavItem
          key={item.href}
          label={item.label}
          href={item.href}
          icon={item.icon ?? FolderClosed}
          active={isActive(pathname, item.href)}
          variant="secondary"
        />
      ))}
    </nav>
  );
}
