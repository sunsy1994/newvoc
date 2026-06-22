"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Bot, CheckCircle2, FileText, KeyRound, RefreshCw, Save, Settings2 } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { AiConfigPayload, PromptListPayload, PromptTemplate } from "@/types/system";

type SystemSettingsMode = "parameters" | "prompts";
type LoadState = "idle" | "loading" | "error";

const defaultAiConfig: AiConfigPayload = {
  config_name: "default",
  base_url: "",
  model_name: "",
  timeout_seconds: 60,
  is_enabled: true,
  is_default: true,
  api_key_configured: false,
  api_key_masked: "",
};

const defaultPrompt: PromptTemplate = {
  prompt_name: "评论用户画像提示词",
  prompt_scene: "comment_user_profile",
  prompt_version: "comment_user_profile_v1",
  prompt_content: "",
  is_default: true,
  is_enabled: true,
};

const promptSceneOptions = [
  { value: "comment_user_profile", label: "评论用户画像", defaultName: "评论用户画像提示词", defaultVersion: "comment_user_profile_v1" },
  { value: "market_report_summary", label: "市场部事件总结", defaultName: "市场部事件总结提示词", defaultVersion: "market_report_summary_v1" },
];

function emptyPromptForScene(scene: string): PromptTemplate {
  const option = promptSceneOptions.find((item) => item.value === scene) ?? promptSceneOptions[0];
  return {
    ...defaultPrompt,
    prompt_name: option.defaultName,
    prompt_scene: option.value,
    prompt_version: option.defaultVersion,
  };
}

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="text-xs font-medium tracking-wide text-[var(--sys-body)]">{children}</label>;
}

function StatusMessage({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-4 py-3 text-xs leading-5 text-[var(--sys-body)]">
      {message}
    </div>
  );
}

function InfoCard({ mode }: { mode: SystemSettingsMode }) {
  const isPrompt = mode === "prompts";
  return (
    <section className="premium-card rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-6">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]">
        {isPrompt ? <FileText className="h-5 w-5" /> : <Settings2 className="h-5 w-5" />}
      </div>
      <h2 className="mt-4 text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">{isPrompt ? "提示词维护" : "参数维护"}</h2>
      <p className="mt-2 text-sm leading-6 text-[var(--sys-body)]">
        {isPrompt
          ? "维护用户画像 AI 打标使用的提示词正文。当前第一版只接入评论用户画像场景，保存为默认后，前端“去画像”会直接读取这里的模板。"
          : "维护 OpenAI 兼容接口参数。API Key 只在后端运行时读取，页面只展示脱敏状态，避免把密钥明文暴露在后台列表里。"}
      </p>
      <div className="mt-5 space-y-3 text-xs text-[var(--sys-body)]">
        <div className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 text-[var(--sys-icon-fill)]" />
          <span>当前接入流程：销售看板全部用户列表里的“去画像”。</span>
        </div>
        <div className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 text-[var(--sys-icon-fill)]" />
          <span>返回结果仍会进入评论用户画像原始表、结果表和标签分数表。</span>
        </div>
      </div>
    </section>
  );
}

export function SystemSettingsPage({ mode }: { mode: SystemSettingsMode }) {
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [aiConfig, setAiConfig] = useState<AiConfigPayload>(defaultAiConfig);
  const [apiKeyDraft, setApiKeyDraft] = useState("");
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [selectedPromptScene, setSelectedPromptScene] = useState("comment_user_profile");
  const [selectedPromptKey, setSelectedPromptKey] = useState("");
  const [promptDraft, setPromptDraft] = useState<PromptTemplate>(defaultPrompt);

  const selectedPrompt = useMemo(() => {
    return prompts.find((item) => `${item.prompt_scene}:${item.prompt_version}` === selectedPromptKey) ?? prompts[0];
  }, [prompts, selectedPromptKey]);

  const loadAiConfig = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await fetch(buildApiUrl("/system/ai-config"), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setAiConfig((await response.json()) as AiConfigPayload);
      setLoadState("idle");
    } catch {
      setLoadState("error");
      setMessage("AI 参数加载失败，请确认后端和 PostgreSQL 已启动。");
    }
  }, []);

  const loadPrompts = useCallback(async () => {
    setLoadState("loading");
    try {
      const params = new URLSearchParams({ scene: selectedPromptScene });
      const response = await fetch(buildApiUrl("/system/prompts", params), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as PromptListPayload;
      const nextPrompts = payload.prompts ?? [];
      setPrompts(nextPrompts);
      const nextSelected = nextPrompts.find((item) => item.is_default) ?? nextPrompts[0] ?? emptyPromptForScene(selectedPromptScene);
      setSelectedPromptKey(`${nextSelected.prompt_scene}:${nextSelected.prompt_version}`);
      setPromptDraft(nextSelected);
      setLoadState("idle");
    } catch {
      setLoadState("error");
      setMessage("提示词加载失败，请确认后端和 PostgreSQL 已启动。");
    }
  }, [selectedPromptScene]);

  useEffect(() => {
    if (mode === "parameters") {
      loadAiConfig();
    } else {
      loadPrompts();
    }
  }, [loadAiConfig, loadPrompts, mode]);

  useEffect(() => {
    if (selectedPrompt) setPromptDraft(selectedPrompt);
  }, [selectedPrompt]);

  async function saveAiConfig(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("正在保存 AI 参数...");
    try {
      const response = await fetch(buildApiUrl("/system/ai-config"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...aiConfig, api_key: apiKeyDraft || undefined }),
      });
      const payload = (await response.json()) as AiConfigPayload & { detail?: string };
      if (!response.ok) {
        setMessage(payload.detail ?? "AI 参数保存失败。");
        return;
      }
      setAiConfig(payload);
      setApiKeyDraft("");
      setMessage("AI 参数已保存。");
    } catch {
      setMessage("AI 参数保存失败，请确认后端服务状态。");
    }
  }

  async function savePrompt(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("正在保存提示词...");
    try {
      const response = await fetch(buildApiUrl("/system/prompts"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...promptDraft, prompt_scene: selectedPromptScene }),
      });
      const payload = (await response.json()) as PromptTemplate & { detail?: string };
      if (!response.ok) {
        setMessage(payload.detail ?? "提示词保存失败。");
        return;
      }
      setMessage("提示词已保存。");
      await loadPrompts();
    } catch {
      setMessage("提示词保存失败，请确认后端服务状态。");
    }
  }

  const isPromptMode = mode === "prompts";

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--sys-subtle)]">System Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--sys-title)]">
            {isPromptMode ? "提示词维护" : "参数维护"}
          </h1>
        </div>
        <button
          type="button"
          onClick={() => (isPromptMode ? loadPrompts() : loadAiConfig())}
          className="inline-flex h-10 items-center gap-2 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-4 text-sm font-semibold text-[var(--sys-body)] shadow-[var(--sys-card-shadow)]"
        >
          <RefreshCw className="h-4 w-4" />
          刷新
        </button>
      </header>

      <div className="grid gap-5 xl:grid-cols-[340px_1fr]">
        <InfoCard mode={mode} />

        <section className="premium-card rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-6">
          {isPromptMode ? (
            <form className="space-y-4" onSubmit={savePrompt}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">评论用户画像提示词</h2>
                  <p className="mt-1 text-xs text-[var(--sys-muted)]">场景固定为 comment_user_profile，后续 AI 流程会读取默认启用版本。</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    value={selectedPromptScene}
                    onChange={(event) => {
                      const nextScene = event.target.value;
                      setSelectedPromptScene(nextScene);
                      setPromptDraft(emptyPromptForScene(nextScene));
                      setSelectedPromptKey("");
                    }}
                    className="premium-input h-10 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-body)] outline-none focus:border-[var(--sys-icon-fill)]"
                  >
                    {promptSceneOptions.map((item) => (
                      <option key={item.value} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                  <select
                    value={selectedPromptKey}
                    onChange={(event) => setSelectedPromptKey(event.target.value)}
                    className="premium-input h-10 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-body)] outline-none focus:border-[var(--sys-icon-fill)]"
                  >
                    {prompts.map((item) => (
                      <option key={`${item.prompt_scene}:${item.prompt_version}`} value={`${item.prompt_scene}:${item.prompt_version}`}>
                        {item.prompt_version}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <div className="space-y-2">
                  <FieldLabel>提示词名称</FieldLabel>
                  <input
                    value={promptDraft.prompt_name}
                    onChange={(event) => setPromptDraft((prev) => ({ ...prev, prompt_name: event.target.value }))}
                    className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                  />
                </div>
                <div className="space-y-2">
                  <FieldLabel>版本</FieldLabel>
                  <input
                    value={promptDraft.prompt_version}
                    onChange={(event) => setPromptDraft((prev) => ({ ...prev, prompt_version: event.target.value }))}
                    className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <FieldLabel>提示词正文</FieldLabel>
                <textarea
                  value={promptDraft.prompt_content}
                  onChange={(event) => setPromptDraft((prev) => ({ ...prev, prompt_content: event.target.value }))}
                  className="premium-input min-h-[430px] w-full rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] p-4 font-mono text-xs leading-6 text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                />
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <label className="inline-flex items-center gap-2 text-sm text-[var(--sys-body)]">
                  <input
                    type="checkbox"
                    checked={promptDraft.is_default}
                    onChange={(event) => setPromptDraft((prev) => ({ ...prev, is_default: event.target.checked }))}
                    className="h-4 w-4 rounded accent-[var(--theme-primary)]"
                  />
                  设为默认提示词
                </label>
                <label className="inline-flex items-center gap-2 text-sm text-[var(--sys-body)]">
                  <input
                    type="checkbox"
                    checked={promptDraft.is_enabled}
                    onChange={(event) => setPromptDraft((prev) => ({ ...prev, is_enabled: event.target.checked }))}
                    className="h-4 w-4 rounded accent-[var(--theme-primary)]"
                  />
                  启用
                </label>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <StatusMessage message={message || (loadState === "loading" ? "正在加载..." : null)} />
                <button type="submit" className="premium-btn inline-flex h-11 items-center gap-2 rounded-[12px] bg-[var(--sys-icon-fill)] px-5 text-sm font-semibold text-white">
                  <Save className="h-4 w-4" />
                  保存提示词
                </button>
              </div>
            </form>
          ) : (
            <form className="space-y-4" onSubmit={saveAiConfig}>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">PROFILE_AI_API_KEY 与模型参数</h2>
                  <p className="mt-1 text-xs text-[var(--sys-muted)]">
                    当前密钥状态：{aiConfig.api_key_configured ? aiConfig.api_key_masked : "未配置"}
                  </p>
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <div className="space-y-2 md:col-span-2">
                  <FieldLabel>Base URL</FieldLabel>
                  <input
                    value={aiConfig.base_url}
                    onChange={(event) => setAiConfig((prev) => ({ ...prev, base_url: event.target.value }))}
                    className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                    placeholder="https://example.com/v1"
                  />
                </div>
                <div className="space-y-2">
                  <FieldLabel>Model</FieldLabel>
                  <input
                    value={aiConfig.model_name}
                    onChange={(event) => setAiConfig((prev) => ({ ...prev, model_name: event.target.value }))}
                    className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                  />
                </div>
                <div className="space-y-2">
                  <FieldLabel>Timeout Seconds</FieldLabel>
                  <input
                    type="number"
                    min={1}
                    value={aiConfig.timeout_seconds}
                    onChange={(event) => setAiConfig((prev) => ({ ...prev, timeout_seconds: Number(event.target.value || 60) }))}
                    className="premium-input h-11 w-full rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 text-sm text-[var(--sys-ink)] outline-none focus:border-[var(--sys-icon-fill)]"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <FieldLabel>API Key</FieldLabel>
                  <div className="premium-input flex h-11 items-center gap-2 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-input-bg)] px-3 focus-within:border-[var(--sys-icon-fill)]">
                    <KeyRound className="h-4 w-4 text-[var(--sys-muted)]" />
                    <input
                      value={apiKeyDraft}
                      onChange={(event) => setApiKeyDraft(event.target.value)}
                      className="min-w-0 flex-1 bg-transparent text-sm text-[var(--sys-ink)] outline-none"
                      placeholder="留空则保持当前密钥"
                    />
                  </div>
                </div>
              </div>

              <label className="inline-flex items-center gap-2 text-sm text-[var(--sys-body)]">
                <input
                  type="checkbox"
                  checked={aiConfig.is_enabled}
                  onChange={(event) => setAiConfig((prev) => ({ ...prev, is_enabled: event.target.checked }))}
                  className="h-4 w-4 rounded accent-[var(--theme-primary)]"
                />
                启用这套 AI 参数
              </label>

              <div className="flex flex-wrap items-center justify-between gap-3">
                <StatusMessage message={message || (loadState === "loading" ? "正在加载..." : null)} />
                <button type="submit" className="premium-btn inline-flex h-11 items-center gap-2 rounded-[12px] bg-[var(--sys-icon-fill)] px-5 text-sm font-semibold text-white">
                  <Save className="h-4 w-4" />
                  保存参数
                </button>
              </div>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
