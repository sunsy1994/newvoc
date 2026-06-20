import { Sidebar } from "@/components/sidebar/Sidebar";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--sys-page)] p-4 text-[var(--sys-ink)]">
      <div className="flex min-h-[calc(100vh-32px)] overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-[var(--sys-card)] shadow-[var(--sys-shell-shadow)]">
        <Sidebar />
        <main className="min-w-0 flex-1 bg-[var(--sys-page)] p-8">{children}</main>
      </div>
    </div>
  );
}
