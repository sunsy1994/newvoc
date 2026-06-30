import { Sidebar } from "@/components/sidebar/Sidebar";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-[100dvh] bg-[var(--sys-page)] p-3 text-[var(--sys-ink)] sm:p-4">
      <div className="mx-auto flex min-h-[calc(100dvh-24px)] max-w-[1920px] overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-[var(--sys-card)] shadow-[var(--sys-shell-shadow)] sm:min-h-[calc(100dvh-32px)]">
        <Sidebar />
        <main className="min-w-0 flex-1 bg-[var(--sys-page)] p-4 sm:p-6 xl:p-8">{children}</main>
      </div>
    </div>
  );
}
