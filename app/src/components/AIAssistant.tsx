import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { useEffect, useMemo, useRef, useState } from 'react';

type ModeKey = 'data' | 'qa' | 'report';
type Message = { id: string; role: 'user' | 'assistant'; content: string };

const modeConfig: Record<
  ModeKey,
  { label: string; helper: string; placeholder: string; responsePrefix: string; glow: string }
> = {
  data: {
    label: '问数',
    helper: '指标/时间/维度',
    placeholder: '输入指标、时间范围、维度，例如：近7天负面舆情占比',
    responsePrefix: '数据洞察',
    glow: 'from-cyan-300 via-sky-500 to-blue-700',
  },
  qa: {
    label: '问答',
    helper: '通用问题',
    placeholder: '直接问我任何问题，例如：为什么社媒投诉在周三激增？',
    responsePrefix: '问答回复',
    glow: 'from-indigo-300 via-violet-500 to-blue-700',
  },
  report: {
    label: '生成报告',
    helper: '结构化产出',
    placeholder: '描述背景、目标、受众与格式要求，例如：输出周报提纲',
    responsePrefix: '报告草案',
    glow: 'from-emerald-300 via-teal-500 to-cyan-700',
  },
};

const quickPrompts: Record<ModeKey, string[]> = {
  data: ['近30天负面声量趋势', '渠道分布 Top5 与环比', '重点事件与影响指数'],
  qa: ['本周口碑变化的核心原因？', '竞品A为何转正更快？', '如何降低客服压力？'],
  report: ['生成本周舆情周报', '输出危机复盘模板', '生成管理层简报要点'],
};

export default function AIAssistant() {
  const [mode, setMode] = useState<ModeKey>('qa');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [hovered, setHovered] = useState(false);
  const [sweepKey, setSweepKey] = useState(0);
  const [thinking, setThinking] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [pendingResponse, setPendingResponse] = useState('');
  const [inputFocused, setInputFocused] = useState(false);
  const [inputHovered, setInputHovered] = useState(false);
  const reducedMotion = useReducedMotion();
  const listRef = useRef<HTMLDivElement | null>(null);

  const activeMode = modeConfig[mode];
  const canSend = input.trim().length > 0 && !thinking && !streamingText;
  const modeSplitActive = inputFocused || inputHovered;
  const placeholder = activeMode.placeholder;

  const toneSuffix = useMemo(() => {
    if (mode === 'data') return '已按结构化方式解析。';
    if (mode === 'report') return '已先输出结构骨架，再补充细节。';
    return '已提炼重点并给出建议。';
  }, [mode]);

  useEffect(() => {
    if (!pendingResponse) return;
    let index = 0;
    const step = () => {
      index += 2;
      setStreamingText(pendingResponse.slice(0, index));
      if (index >= pendingResponse.length) {
        setMessages((prev) => [
          ...prev,
          {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: pendingResponse,
          },
        ]);
        setPendingResponse('');
        setStreamingText('');
      }
    };

    step();
    const timer = window.setInterval(step, reducedMotion ? 20 : 35);
    return () => window.clearInterval(timer);
  }, [pendingResponse, reducedMotion]);

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTo({ top: listRef.current.scrollHeight, behavior: reducedMotion ? 'auto' : 'smooth' });
  }, [messages, thinking, streamingText, reducedMotion]);

  const mockAssistantReply = (question: string) =>
    `${activeMode.responsePrefix}：围绕“${question}”，已完成重点信息提取、争议信号判断与下一步行动建议。${toneSuffix}`;

  const handleSend = () => {
    const content = input.trim();
    if (!content || !canSend) return;

    setMessages((prev) => [...prev, { id: `user-${Date.now()}`, role: 'user', content }]);
    setInput('');
    setThinking(true);

    window.setTimeout(() => {
      setThinking(false);
      setPendingResponse(mockAssistantReply(content));
    }, reducedMotion ? 300 : 800);
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.35 }}
      onHoverStart={() => {
        setHovered(true);
        setSweepKey((prev) => prev + 1);
      }}
      onHoverEnd={() => setHovered(false)}
      className="group relative h-full overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-b from-white to-slate-50/80 p-4 shadow-[0_8px_24px_rgba(15,23,42,0.06)] transition-colors"
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(56,189,248,0.16),transparent_52%)]" />
      <AnimatePresence>
        {hovered && !reducedMotion && (
          <motion.span
            key={sweepKey}
            initial={{ x: '-120%', opacity: 0 }}
            animate={{ x: '120%', opacity: 0.55 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="pointer-events-none absolute inset-y-0 w-1/2 -skew-x-12 bg-gradient-to-r from-transparent via-sky-200/50 to-transparent"
          />
        )}
      </AnimatePresence>

      <div className="relative z-10 flex h-full flex-col">
        <header className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-900">AI 对话助手</h3>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-600">LIVE</span>
          </div>
          <p className="text-[11px] text-slate-400">进入输入区可切换模式</p>
        </header>

        <div
          ref={listRef}
          className="relative flex-1 space-y-2 overflow-auto rounded-xl border border-slate-100 bg-white/85 p-3"
        >
          <AnimatePresence mode="popLayout">
            {messages.length === 0 && !thinking && !streamingText && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                className="flex min-h-full flex-col"
              >
                <p className="text-center text-xs text-slate-500">输入问题，或移动到输入区触发模式分裂。</p>
                <div className="relative flex flex-1 items-center justify-center pt-2">
                  <div
                    className="relative h-44 w-full max-w-[330px] overflow-hidden rounded-xl border border-slate-100 bg-gradient-to-b from-slate-50 via-white to-slate-50/70"
                    style={{ perspective: 900 }}
                  >
                    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_48%,rgba(56,189,248,0.2),rgba(255,255,255,0)_55%)]" />
                    <div className="pointer-events-none absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full bg-sky-100/40 blur-2xl" />
                    <AnimatePresence mode="wait">
                      {!modeSplitActive ? (
                        <motion.div
                          key="single-sphere"
                          initial={{ opacity: 0, scale: 0.78, y: 6 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.72, y: -6 }}
                          transition={{ duration: 0.32, ease: 'easeOut' }}
                          className="absolute inset-0"
                        >
                          <motion.div
                            animate={reducedMotion ? { scale: 1 } : { scale: [1, 1.1, 1], opacity: [0.45, 0.7, 0.45] }}
                            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                            className="absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-200/55"
                          />
                          <div className="absolute left-1/2 top-1/2 h-[72px] w-[72px] -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-full bg-gradient-to-br from-cyan-300 via-sky-500 to-blue-700 shadow-[0_18px_30px_rgba(29,78,216,0.3)]">
                            <motion.span
                              animate={reducedMotion ? { x: '0%' } : { x: ['0%', '-50%'] }}
                              transition={{ duration: 4.5, repeat: Infinity, ease: 'linear' }}
                              className="absolute inset-y-[6px] left-[-50%] w-[200%] rounded-full opacity-30"
                              style={{
                                backgroundImage:
                                  'repeating-linear-gradient(0deg, rgba(255,255,255,0.28) 0 2px, rgba(255,255,255,0) 2px 12px)',
                              }}
                            />
                            <motion.span
                              animate={
                                reducedMotion
                                  ? { x: 0, y: 0, opacity: 0.55 }
                                  : { x: [0, 4, -2, 0], y: [0, -2, 1, 0], opacity: [0.45, 0.68, 0.52, 0.45] }
                              }
                              transition={{ duration: 3.8, repeat: Infinity, ease: 'easeInOut' }}
                              className="absolute left-3 top-3 h-2.5 w-6 rounded-full bg-white/55 blur-[0.7px]"
                            />
                            <span className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_30%_28%,rgba(255,255,255,0.34),rgba(255,255,255,0)_38%)]" />
                            <span className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_68%_72%,rgba(3,7,18,0.32),rgba(3,7,18,0)_58%)]" />
                            <span className="absolute inset-0 rounded-full shadow-[inset_0_0_0_1px_rgba(255,255,255,0.2),inset_0_10px_16px_rgba(255,255,255,0.14),inset_0_-12px_18px_rgba(2,6,23,0.24)]" />
                            <span className="absolute left-4 top-[18px] h-1.5 w-3 rounded-full bg-white/70" />
                            <span className="absolute left-[22px] top-[22px] h-1.5 w-2 rounded-full bg-white/60" />
                            <span className="absolute left-[28px] top-[26px] h-1 w-1.5 rounded-full bg-white/55" />
                          </div>
                        </motion.div>
                      ) : (
                        <motion.div
                          key="split-spheres"
                          initial={{ opacity: 0, scale: 0.94 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.94 }}
                          transition={{ duration: 0.28, ease: 'easeOut' }}
                          className="absolute inset-0 flex items-center justify-center px-2"
                        >
                          <div className="grid w-full max-w-[312px] grid-cols-3 gap-2">
                            {(Object.keys(modeConfig) as ModeKey[]).map((item, idx) => {
                            const config = modeConfig[item];
                            const selected = item === mode;
                            return (
                              <motion.button
                                key={item}
                                type="button"
                                onClick={() => setMode(item)}
                                initial={{ opacity: 0, y: 14, scale: 0.88, filter: 'blur(4px)' }}
                                animate={{ opacity: 1, y: 0, scale: selected ? 1.03 : 1, filter: 'blur(0px)' }}
                                transition={{
                                  type: 'spring',
                                  stiffness: 280,
                                  damping: 22,
                                  delay: reducedMotion ? 0 : 0.04 + idx * 0.08,
                                }}
                                className={`flex flex-col items-center justify-center rounded-lg border px-1.5 py-2 text-center transition ${
                                  selected
                                    ? 'border-sky-300 bg-sky-50/80 shadow-[0_8px_16px_rgba(14,165,233,0.16)]'
                                    : 'border-slate-200 bg-white/90 hover:border-slate-300'
                                }`}
                                aria-label={`切换到${config.label}`}
                              >
                                {!reducedMotion && (
                                  <motion.span
                                    initial={{ scaleX: 0, opacity: 0 }}
                                    animate={{ scaleX: 1, opacity: 0.6 }}
                                    transition={{ duration: 0.28, delay: idx * 0.06 }}
                                    className="mb-1.5 h-px w-8 origin-center bg-gradient-to-r from-transparent via-sky-300 to-transparent"
                                  />
                                )}
                                <motion.span
                                  animate={
                                    reducedMotion
                                      ? { y: 0 }
                                      : { y: selected ? [0, -1.5, 0] : [0, -0.8, 0] }
                                  }
                                  transition={{
                                    y: { duration: 2.4, repeat: Infinity, ease: 'easeInOut' },
                                  }}
                                  className={`relative mb-2 h-8 w-8 overflow-hidden rounded-full bg-gradient-to-br ${config.glow} ${
                                    selected ? 'shadow-[0_8px_16px_rgba(30,41,59,0.25)]' : 'shadow-[0_6px_12px_rgba(30,41,59,0.18)]'
                                  }`}
                                >
                                  <motion.span
                                    animate={reducedMotion ? { x: '0%' } : { x: ['0%', '-50%'] }}
                                    transition={{ duration: 3.6, repeat: Infinity, ease: 'linear' }}
                                    className="absolute inset-y-[3px] left-[-50%] w-[200%] rounded-full opacity-25"
                                    style={{
                                      backgroundImage:
                                        'repeating-linear-gradient(0deg, rgba(255,255,255,0.24) 0 1.5px, rgba(255,255,255,0) 1.5px 7px)',
                                    }}
                                  />
                                  <motion.span
                                    animate={
                                      reducedMotion
                                        ? { x: 0, y: 0, opacity: 0.4 }
                                        : { x: [0, 1.5, -1, 0], y: [0, -0.8, 0.4, 0], opacity: [0.32, 0.5, 0.38, 0.32] }
                                    }
                                    transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut' }}
                                    className="absolute left-1.5 top-1.5 h-1.5 w-3 rounded-full bg-white/45 blur-[0.8px]"
                                  />
                                  <span className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_32%_30%,rgba(255,255,255,0.28),rgba(255,255,255,0)_42%)]" />
                                  <span className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_70%_72%,rgba(2,6,23,0.28),rgba(2,6,23,0)_60%)]" />
                                </motion.span>
                                <p className="text-[11px] font-medium text-slate-700">{`AI${config.label}`}</p>
                                <p className="mt-0.5 text-[10px] text-slate-400">{config.helper}</p>
                              </motion.button>
                            );
                            })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
                <div className="mt-3 grid grid-cols-1 gap-1.5">
                  {quickPrompts[mode].map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => setInput(prompt)}
                      className="rounded-lg border border-slate-100 bg-slate-50 px-2.5 py-2 text-left text-xs text-slate-600 transition hover:border-sky-200 hover:bg-sky-50 hover:text-sky-700"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[86%] rounded-2xl px-3 py-2 text-xs leading-relaxed ${
                  message.role === 'user'
                    ? 'bg-sky-600 text-white'
                    : 'border border-slate-100 bg-slate-50 text-slate-700'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}

          <AnimatePresence>
            {thinking && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="relative flex justify-start overflow-hidden rounded-2xl border border-cyan-100 bg-gradient-to-r from-cyan-50 to-sky-50 px-3 py-2 text-xs text-slate-600"
              >
                {!reducedMotion && (
                  <motion.div
                    animate={{ x: ['-100%', '100%'] }}
                    transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                    className="pointer-events-none absolute inset-y-0 w-1/2 bg-gradient-to-r from-transparent via-cyan-200/50 to-transparent"
                  />
                )}
                <div className="relative flex items-center gap-2">
                  <span>AI 思考中</span>
                  <span className="flex gap-1">
                    {[0, 1, 2].map((dot) => (
                      <motion.i
                        key={dot}
                        animate={reducedMotion ? undefined : { y: [0, -2, 0], opacity: [0.45, 1, 0.45] }}
                        transition={{ duration: 0.7, repeat: Infinity, delay: dot * 0.12 }}
                        className="h-1 w-1 rounded-full bg-cyan-500 not-italic"
                      />
                    ))}
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {streamingText && (
            <div className="flex justify-start">
              <div className="max-w-[86%] rounded-2xl border border-slate-100 bg-slate-50 px-3 py-2 text-xs leading-relaxed text-slate-700">
                {streamingText}
                <motion.span
                  animate={reducedMotion ? undefined : { opacity: [0, 1, 0] }}
                  transition={{ duration: 0.9, repeat: Infinity }}
                  className="ml-0.5 inline-block h-3 w-0.5 bg-slate-500 align-middle"
                />
              </div>
            </div>
          )}
        </div>

        <div
          className="relative mt-3"
          onMouseEnter={() => setInputHovered(true)}
          onMouseLeave={() => setInputHovered(false)}
        >
          <motion.div
            animate={
              hovered
                ? {
                    boxShadow: '0 0 0 1px rgba(14,165,233,0.35), 0 8px 24px rgba(14,165,233,0.12)',
                  }
                : { boxShadow: '0 0 0 1px rgba(148,163,184,0.18)' }
            }
            className="rounded-xl bg-white p-2"
          >
            <div className="mb-1 flex items-center justify-between px-1">
              <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-700">
                <span className={`h-1.5 w-1.5 rounded-full bg-gradient-to-br ${activeMode.glow}`} />
                {activeMode.label}
              </span>
              <span
                className={`text-[11px] transition ${
                  hovered ? 'text-sky-600' : 'text-slate-400'
                }`}
              >
                {modeSplitActive ? '模式分裂已激活' : '进入输入区触发分裂'}
              </span>
            </div>
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onFocus={() => setInputFocused(true)}
                onBlur={() => setInputFocused(false)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                rows={2}
                placeholder={placeholder}
                disabled={thinking || !!streamingText}
                className="min-h-[64px] flex-1 resize-none rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700 outline-none ring-sky-300 placeholder:text-slate-400 focus:border-sky-300 focus:bg-white focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60"
              />
              <button
                type="button"
                onClick={handleSend}
                disabled={!canSend}
                className="inline-flex h-9 items-center justify-center rounded-lg bg-sky-600 px-3 text-xs text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                aria-label="发送消息"
              >
                发送
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.section>
  );
}
