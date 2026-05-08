import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface AssetFilterFieldProps {
  label: string;
  children: ReactNode;
  className?: string;
}

export default function AssetFilterField({ label, children, className }: AssetFilterFieldProps) {
  return (
    <div className={cn('flex min-w-0 items-center gap-3 rounded-2xl border border-gray-200 bg-gray-50/80 px-3 py-2', className)}>
      <div className="w-20 shrink-0 text-sm font-medium text-gray-600">{label}</div>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
