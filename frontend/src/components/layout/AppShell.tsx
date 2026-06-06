import { Sidebar } from "@/components/sidebar/Sidebar";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#ffffff_0,#f4f4f2_34%,#e9edf1_100%)] p-4 text-zinc-950">
      <div className="flex min-h-[calc(100vh-32px)] gap-4">
        <Sidebar />
        <main className="min-w-0 flex-1 rounded-[28px] border border-white/70 bg-white/82 p-8 shadow-soft backdrop-blur">
          {children}
        </main>
      </div>
    </div>
  );
}
