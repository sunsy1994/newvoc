"use client";

import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
import { createContext, useContext, useState } from "react";

type DashboardTheme = "nexus" | "soft";

type VocDashboardThemeFrameProps = {
  children: ReactNode;
};

const themeOptions: Array<{ key: DashboardTheme; label: string; swatch: string }> = [
  { key: "soft", label: "奶茶", swatch: "#5D9691" },
  { key: "nexus", label: "经典", swatch: "#5B63B7" },
];

const VocDashboardThemeContext = createContext<{
  theme: DashboardTheme;
  setTheme: (theme: DashboardTheme) => void;
} | null>(null);

function useVocDashboardTheme() {
  const context = useContext(VocDashboardThemeContext);
  if (!context) {
    throw new Error("ThemeSelect must be used inside VocDashboardThemeFrame");
  }
  return context;
}

export function VocDashboardThemeFrame({ children }: VocDashboardThemeFrameProps) {
  const [theme, setTheme] = useState<DashboardTheme>("soft");

  return (
    <VocDashboardThemeContext.Provider value={{ theme, setTheme }}>
      <div data-voc-theme={theme} className="voc-theme-frame voc-dashboard-page-shell min-h-full rounded-[24px] border border-white/70 bg-[var(--theme-page)] p-3 shadow-[0_18px_55px_rgba(31,43,39,0.04)] transition-colors duration-300 sm:p-5">
        {children}
      </div>
    </VocDashboardThemeContext.Provider>
  );
}

export function ThemeSelect() {
  const { theme, setTheme } = useVocDashboardTheme();
  const [isOpen, setIsOpen] = useState(false);
  const activeTheme = themeOptions.find((option) => option.key === theme) ?? themeOptions[0];

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((value) => !value)}
        className="inline-flex h-10 min-w-[112px] items-center justify-between gap-3 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 text-sm font-semibold text-[var(--theme-ink)] shadow-[0_6px_16px_rgba(31,43,39,0.035)] outline-none transition hover:border-[var(--theme-selected-border)] hover:bg-[var(--theme-hover-bg)]"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: activeTheme.swatch }} />
          主题
        </span>
        <ChevronDown className={`h-4 w-4 text-[var(--theme-muted)] transition ${isOpen ? "rotate-180" : ""}`} />
      </button>
      {isOpen ? (
        <div className="absolute right-0 top-12 z-30 w-40 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-card)] p-1.5 shadow-[0_20px_50px_rgba(31,43,39,0.14)]" role="listbox">
          {themeOptions.map((option) => {
            const isActive = option.key === theme;
            return (
              <button
                key={option.key}
                type="button"
                onClick={() => {
                  setTheme(option.key);
                  setIsOpen(false);
                }}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-medium transition ${
                  isActive ? "bg-[var(--theme-selected-bg)] text-[var(--theme-selected-text)]" : "text-[var(--theme-body)] hover:bg-[var(--theme-hover-bg)] hover:text-[var(--theme-ink)]"
                }`}
                role="option"
                aria-selected={isActive}
              >
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: option.swatch }} />
                {option.label}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
