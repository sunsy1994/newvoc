"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const pageSizeOptions = [10, 20, 50, 100];

type DataPaginationProps = {
  total: number;
  offset: number;
  pageSize: number;
  onOffsetChange: (offset: number) => void;
  onPageSizeChange: (pageSize: number) => void;
};

export function DataPagination({
  total,
  offset,
  pageSize,
  onOffsetChange,
  onPageSizeChange,
}: DataPaginationProps) {
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = total > 0 ? Math.floor(offset / pageSize) + 1 : 1;
  const startRow = total > 0 ? offset + 1 : 0;
  const endRow = Math.min(offset + pageSize, total);
  const [jumpValue, setJumpValue] = useState(String(currentPage));

  useEffect(() => {
    setJumpValue(String(currentPage));
  }, [currentPage]);

  const options = useMemo(() => {
    return pageSizeOptions.includes(pageSize) ? pageSizeOptions : [...pageSizeOptions, pageSize].sort((a, b) => a - b);
  }, [pageSize]);

  function goToPage(page: number) {
    const nextPage = Math.min(Math.max(page, 1), pageCount);
    onOffsetChange((nextPage - 1) * pageSize);
  }

  function submitJump(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsedPage = Number(jumpValue);
    if (!Number.isFinite(parsedPage)) return;
    goToPage(Math.trunc(parsedPage));
  }

  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-[#7b8190]">
      <span>
        显示 {startRow.toLocaleString("zh-CN")} - {endRow.toLocaleString("zh-CN")} / {total.toLocaleString("zh-CN")}
      </span>

      <div className="flex flex-wrap items-center gap-2">
        <label className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070]">
          每页
          <select
            value={pageSize}
            onChange={(event) => {
              onPageSizeChange(Number(event.target.value));
              onOffsetChange(0);
            }}
            className="bg-transparent text-xs font-semibold text-[#151720] outline-none"
          >
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          条
        </label>

        <button
          type="button"
          disabled={currentPage <= 1 || total === 0}
          onClick={() => goToPage(currentPage - 1)}
          className="inline-flex h-9 items-center gap-1 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronLeft className="h-4 w-4" />
          上一页
        </button>

        <form
          className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070]"
          onSubmit={submitJump}
        >
          <span>第</span>
          <input
            value={jumpValue}
            onChange={(event) => setJumpValue(event.target.value)}
            className="h-6 w-10 rounded-md bg-[#f7f9fc] text-center text-xs font-semibold text-[#151720] outline-none focus:ring-1 focus:ring-[#5347CE]"
            inputMode="numeric"
            aria-label="跳转页码"
          />
          <span>/ {pageCount.toLocaleString("zh-CN")} 页</span>
        </form>

        <button
          type="button"
          disabled={currentPage >= pageCount || total === 0}
          onClick={() => goToPage(currentPage + 1)}
          className="inline-flex h-9 items-center gap-1 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070] disabled:cursor-not-allowed disabled:opacity-40"
        >
          下一页
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
