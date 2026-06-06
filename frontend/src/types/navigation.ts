import type { LucideIcon } from "lucide-react";

export type NavigationChildItem = {
  label: string;
  href: string;
  icon?: LucideIcon;
};

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
  children?: NavigationChildItem[];
};
