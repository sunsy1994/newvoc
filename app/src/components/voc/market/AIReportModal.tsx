import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, BarChart3, AlertTriangle, Sparkles, ChevronRight } from 'lucide-react';
import type { AIReportData } from './types';

interface AIReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: AIReportData;
  department?: 'market' | 'product';
}

export default function AIReportModal({ isOpen, onClose, data, department = 'market' }: AIReportModalProps) {
  const isProduct = department === 'product';

  const sectionStyles = {
    event: {
      wrapper: 'border-blue-100 bg-blue-50/80',
      iconWrap: 'bg-blue-100/80 text-blue-700',
      icon: Calendar,
      bullet: 'bg-blue-500',
      title: isProduct ? '问题态势与扩散' : '事件节奏与热度',
      subtitle: isProduct ? '对应PRD模块A/B：态势卡与痛点加速度' : '对应PRD模块A：事件总览'
    },
    metric: {
      wrapper: 'border-indigo-100 bg-indigo-50/75',
      iconWrap: 'bg-indigo-100/80 text-indigo-700',
      icon: BarChart3,
      bullet: 'bg-indigo-500',
      title: isProduct ? '证据链与影响关键结论' : '关键指标与命题表现',
      subtitle: isProduct ? '对应PRD模块C/D：证据可信度与影响面' : '对应PRD模块B/C：命题竞争与内容有效性'
    },
    alert: {
      wrapper: 'border-slate-200 bg-slate-50/90',
      iconWrap: 'bg-slate-200/80 text-slate-700',
      icon: AlertTriangle,
      bullet: 'bg-slate-500',
      title: isProduct ? '处置路径与优先级' : '争议信号与动作建议',
      subtitle: isProduct ? '对应PRD模块E：OTA/服务/改款分流' : '对应PRD模块C/D：误伤信号与人群匹配'
    }
  } as const;

  const splitPoint = (text: string) => {
    const parts = text.split(/[:：]/);
    if (parts.length <= 1) return { lead: '', detail: text };

    return {
      lead: parts[0].trim(),
      detail: parts.slice(1).join('：').trim()
    };
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
            >
              <div className="border-b border-gray-100 p-6">
                <div className="mb-4 flex items-center justify-between">
                  <div className="inline-flex items-center gap-1 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                    <Sparkles className="h-3.5 w-3.5" />
                    {isProduct ? 'AI 摘要（产品部 PRD 版）' : 'AI 摘要（市场部 PRD 版）'}
                  </div>
                  <button
                    onClick={onClose}
                    className="flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-gray-100"
                  >
                    <X className="h-5 w-5 text-gray-400" />
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">{isProduct ? '产品问题战情快报' : '市场传播战果快报'}</h2>
                    <p className="text-sm text-gray-500">有重点、有动作的可执行总结</p>
                  </div>
                </div>
              </div>

              <div className="max-h-[60vh] space-y-4 overflow-y-auto p-6">
                <div className="grid gap-3 rounded-2xl border border-blue-100 bg-gradient-to-r from-blue-50 via-indigo-50/70 to-blue-50 p-4 md:grid-cols-3">
                  {data.keyMetrics.slice(0, 3).map((item, index) => (
                    <div key={index} className="rounded-xl border border-white/60 bg-white/70 p-3">
                      <p className="text-xs font-medium text-blue-600">重点指标 {index + 1}</p>
                      <p className="mt-1 text-sm font-semibold text-gray-900">{item}</p>
                    </div>
                  ))}
                </div>

                <div className={`rounded-2xl border p-4 ${sectionStyles.event.wrapper}`}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${sectionStyles.event.iconWrap}`}>
                        <sectionStyles.event.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="text-base font-semibold text-gray-900">{sectionStyles.event.title}</h3>
                        <p className="text-xs text-gray-500">{sectionStyles.event.subtitle}</p>
                      </div>
                    </div>
                    <span className="rounded-full bg-white/80 px-2 py-1 text-xs font-medium text-blue-700">重点追踪</span>
                  </div>
                  <div className="space-y-2">
                    {data.eventProgress.map((item, index) => (
                      <div key={index} className="rounded-xl border border-white/70 bg-white/75 p-3">
                        <div className="flex items-start gap-2">
                          <div className={`mt-2 h-1.5 w-1.5 rounded-full ${sectionStyles.event.bullet}`}></div>
                          <div className="min-w-0 flex-1">
                            {(() => {
                              const parsed = splitPoint(item);
                              return parsed.lead ? (
                                <>
                                  <p className="text-sm font-semibold text-gray-900">{parsed.lead}</p>
                                  <p className="mt-1 text-sm text-gray-700">{parsed.detail}</p>
                                </>
                              ) : (
                                <p className="text-sm text-gray-700">{parsed.detail}</p>
                              );
                            })()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className={`rounded-2xl border p-4 ${sectionStyles.metric.wrapper}`}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${sectionStyles.metric.iconWrap}`}>
                        <sectionStyles.metric.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="text-base font-semibold text-gray-900">{sectionStyles.metric.title}</h3>
                        <p className="text-xs text-gray-500">{sectionStyles.metric.subtitle}</p>
                      </div>
                    </div>
                    <span className="rounded-full bg-white/80 px-2 py-1 text-xs font-medium text-indigo-700">重点结论</span>
                  </div>
                  <div className="space-y-2">
                    {data.keyMetrics.map((item, index) => (
                      <div key={index} className="rounded-xl border border-white/70 bg-white/80 p-3">
                        <div className="flex items-center gap-2">
                          <ChevronRight className="h-3.5 w-3.5 text-indigo-500" />
                          <p className="text-sm font-medium text-gray-800">{item}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className={`rounded-2xl border p-4 ${sectionStyles.alert.wrapper}`}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${sectionStyles.alert.iconWrap}`}>
                        <sectionStyles.alert.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="text-base font-semibold text-gray-900">{sectionStyles.alert.title}</h3>
                        <p className="text-xs text-gray-500">{sectionStyles.alert.subtitle}</p>
                      </div>
                    </div>
                    <span className="rounded-full bg-white/90 px-2 py-1 text-xs font-medium text-slate-700">优先处理</span>
                  </div>
                  <div className="space-y-2">
                    {data.alerts.map((item, index) => (
                      <div key={index} className="rounded-xl border border-white/80 bg-white/85 p-3">
                        <div className="flex items-start gap-2">
                          <div className={`mt-2 h-1.5 w-1.5 rounded-full ${sectionStyles.alert.bullet}`}></div>
                          <p className="text-sm text-gray-700">{item}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-gray-100 bg-gray-50">
                <button
                  onClick={onClose}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors"
                >
                  知道了
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
