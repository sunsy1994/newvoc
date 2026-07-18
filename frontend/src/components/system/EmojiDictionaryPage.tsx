"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { RefreshCw, Save, SmilePlus } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import { DataPagination } from "@/components/shared/DataPagination";
import type { EmojiListPayload, EmojiMapping } from "@/types/system";

type LoadState = "idle" | "loading" | "error";

const defaultDraft: EmojiMapping = {
  emoji_code: "[666]",
  emoji_type: "emoji",
  emoji_value: "👍",
  display_name: "666",
  is_enabled: true,
};

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="text-xs font-medium tracking-wide text-[var(--sys-body)]">{children}</label>;
}

function EmojiPreview({ mapping }: { mapping: EmojiMapping }) {
  if (mapping.emoji_type === "image" && mapping.emoji_value) {
    return <img src={mapping.emoji_value} alt={mapping.display_name || mapping.emoji_code} className="h-7 w-7 rounded-md object-contain" />;
  }
  return <span className="text-2xl leading-none">{mapping.emoji_value || "🙂"}</span>;
}

export function EmojiDictionaryPage() {
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [emojis, setEmojis] = useState<EmojiMapping[]>([]);
  const [draft, setDraft] = useState<EmojiMapping>(defaultDraft);
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const filteredEmojis = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return emojis;
    return emojis.filter((item) => {
      return [item.emoji_code, item.display_name, item.emoji_value].some((value) => String(value ?? "").toLowerCase().includes(keyword));
    });
  }, [emojis, query]);
  const visibleEmojis = useMemo(() => filteredEmojis.slice(offset, offset + pageSize), [filteredEmojis, offset, pageSize]);

  const loadEmojis = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await fetch(buildApiUrl("/system/emojis"), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as EmojiListPayload;
      setEmojis(payload.emojis ?? []);
      setLoadState("idle");
    } catch {
      setLoadState("error");
      setMessage("表情包加载失败，请确认后端和 PostgreSQL 已启动。");
    }
  }, []);

  useEffect(() => {
    loadEmojis();
  }, [loadEmojis]);

  useEffect(() => {
    setOffset(0);
  }, [query]);

  useEffect(() => {
    if (offset < filteredEmojis.length || offset === 0) return;
    setOffset(Math.max(0, (Math.ceil(filteredEmojis.length / pageSize) - 1) * pageSize));
  }, [filteredEmojis.length, offset, pageSize]);

  async function saveEmoji(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("正在保存表情包...");
    try {
      const response = await fetch(buildApiUrl("/system/emojis"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft),
      });
      const payload = (await response.json()) as EmojiMapping & { detail?: string };
      if (!response.ok) {
        setMessage(payload.detail ?? "表情包保存失败。");
        return;
      }
      setDraft(payload);
      setMessage("表情包已保存。");
      await loadEmojis();
    } catch {
      setMessage("表情包保存失败，请确认后端服务状态。");
    }
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--sys-subtle)]">System Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--sys-title)]">表情包维护</h1>
          <p className="mt-2 text-sm text-[var(--sys-body)]">维护 [666]、[捂脸] 这类平台表情文本的展示映射。原始评论不改，只在页面展示时替换。</p>
        </div>
        <button
          type="button"
          onClick={loadEmojis}
          className="inline-flex h-10 items-center gap-2 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-4 text-sm font-semibold text-[var(--sys-body)] shadow-[var(--sys-card-shadow)]"
        >
          <RefreshCw className="h-4 w-4" />
          刷新
        </button>
      </header>

      <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
        <form className="premium-card rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-6" onSubmit={saveEmoji}>
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]">
              <SmilePlus className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">新增 / 编辑表情</h2>
              <p className="mt-1 text-xs text-[var(--sys-muted)]">同一个 emoji_code 会自动覆盖更新。</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <FieldLabel>emoji_code</FieldLabel>
              <input
                value={draft.emoji_code}
                onChange={(event) => setDraft((prev) => ({ ...prev, emoji_code: event.target.value }))}
                className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                placeholder="[666]"
              />
            </div>

            <div className="space-y-2">
              <FieldLabel>emoji_type</FieldLabel>
              <select
                value={draft.emoji_type}
                onChange={(event) => setDraft((prev) => ({ ...prev, emoji_type: event.target.value as EmojiMapping["emoji_type"] }))}
                className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
              >
                <option value="emoji">emoji 字符</option>
                <option value="image">图片地址</option>
              </select>
            </div>

            <div className="space-y-2">
              <FieldLabel>emoji_value</FieldLabel>
              <input
                value={draft.emoji_value}
                onChange={(event) => setDraft((prev) => ({ ...prev, emoji_value: event.target.value }))}
                className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                placeholder="👍 或 /static/emojis/666.png"
              />
            </div>

            <div className="space-y-2">
              <FieldLabel>display_name</FieldLabel>
              <input
                value={draft.display_name ?? ""}
                onChange={(event) => setDraft((prev) => ({ ...prev, display_name: event.target.value }))}
                className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                placeholder="666"
              />
            </div>

            <div className="flex items-center justify-between rounded-2xl bg-[var(--sys-panel-bg)] px-4 py-3">
              <span className="text-xs font-semibold text-[var(--sys-body)]">预览</span>
              <EmojiPreview mapping={draft} />
            </div>

            <label className="inline-flex items-center gap-2 text-sm text-[var(--sys-body)]">
              <input
                type="checkbox"
                checked={draft.is_enabled}
                onChange={(event) => setDraft((prev) => ({ ...prev, is_enabled: event.target.checked }))}
                className="h-4 w-4 rounded accent-[var(--theme-primary)]"
              />
              启用
            </label>

            {message ? <div className="rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-4 py-3 text-xs text-[var(--sys-body)]">{message}</div> : null}

            <button type="submit" className="premium-btn inline-flex h-11 w-full items-center justify-center gap-2 rounded-[12px] bg-[var(--sys-icon-fill)] px-5 text-sm font-semibold text-white">
              <Save className="h-4 w-4" />
              保存表情包
            </button>
          </div>
        </form>

        <section className="premium-card rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">表情包字典</h2>
              <p className="mt-1 text-xs text-[var(--sys-muted)]">共 {emojis.length} 条，启用后评论展示自动替换。</p>
            </div>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="premium-input h-10 w-56 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
              placeholder="搜索 [666]"
            />
          </div>

          <div className="overflow-hidden rounded-2xl border border-[var(--sys-input-border)]">
            <table className="w-full text-left text-sm">
              <thead className="bg-[var(--sys-panel-bg)] text-[11px] font-semibold uppercase tracking-[0.04em] text-[var(--sys-muted)]">
                <tr>
                  <th className="px-4 py-3">原始文本</th>
                  <th className="px-4 py-3">预览</th>
                  <th className="px-4 py-3">类型</th>
                  <th className="px-4 py-3">名称</th>
                  <th className="px-4 py-3">状态</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--sys-input-border)]">
                {visibleEmojis.map((item) => (
                  <tr key={item.emoji_code} className="cursor-pointer bg-[var(--sys-card)] transition-colors duration-150 hover:bg-[var(--sys-panel-bg)]" onClick={() => setDraft(item)}>
                    <td className="px-4 py-3 font-mono text-[var(--sys-ink)]">{item.emoji_code}</td>
                    <td className="px-4 py-3">
                      <EmojiPreview mapping={item} />
                    </td>
                    <td className="px-4 py-3 text-[var(--sys-body)]">{item.emoji_type}</td>
                    <td className="px-4 py-3 text-[var(--sys-body)]">{item.display_name || "-"}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-lg px-2 py-1 text-[11px] font-medium ${item.is_enabled ? "bg-[#EDF7E9] text-[#54853E]" : "bg-[var(--sys-panel-bg)] text-[var(--sys-muted)]"}`}>
                        {item.is_enabled ? "启用" : "停用"}
                      </span>
                    </td>
                  </tr>
                ))}
                {!filteredEmojis.length ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-sm text-[var(--sys-muted)]">
                      {loadState === "loading" ? "正在加载..." : "暂无表情包映射"}
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
          <DataPagination total={filteredEmojis.length} offset={offset} pageSize={pageSize} onOffsetChange={setOffset} onPageSizeChange={setPageSize} />
        </section>
      </div>
    </div>
  );
}
