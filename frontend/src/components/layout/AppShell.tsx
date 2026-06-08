import { Sidebar } from "@/components/sidebar/Sidebar";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#f5f7fb] p-3 text-[#151720]">
      <div className="flex min-h-[calc(100vh-24px)] overflow-hidden rounded-[22px] border border-[#e8ecf3] bg-white shadow-[0_18px_60px_rgba(26,32,44,0.08)]">
        <Sidebar />
        <main className="min-w-0 flex-1 bg-[#f7f9fc] p-6">{children}</main>
      </div>
    </div>
  );
}
