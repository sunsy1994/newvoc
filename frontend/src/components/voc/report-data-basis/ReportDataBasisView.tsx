import {
  resolveDepartmentDataBasis,
  type DataBasisProcessType,
} from "./reportDataBasis";

const PROCESS_LABELS: Record<DataBasisProcessType, string> = {
  direct: "直接统计",
  rule: "规则计算",
  llm_label: "LLM 标签",
  llm_summary: "LLM 总结",
};

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--theme-muted)]">{title}</p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {items.map((item) => (
          <span key={item} className="rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] px-2.5 py-1 text-xs leading-5 text-[var(--theme-body)]">
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export function ReportDataBasisView({
  departmentName,
  eventName,
  generatedAt,
}: {
  departmentName: string;
  eventName?: string;
  generatedAt?: string;
}) {
  const sections = resolveDepartmentDataBasis(departmentName);

  if (!sections.length) {
    return (
      <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-8 text-center text-sm text-[var(--theme-muted)]">
        当前报告未配置业务数据依据。
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <section className="rounded-2xl border border-[var(--theme-border)] bg-[linear-gradient(135deg,var(--theme-white),var(--theme-selected-bg))] p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--theme-primary)]">Data Basis</p>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-[var(--theme-ink)]">这份报告如何使用数据</h2>
            <p className="mt-1 text-sm leading-6 text-[var(--theme-body)]">
              按故事线说明数据来源、处理方式与指标口径；所有结论均基于现有数据，不在本页补充推断。
            </p>
          </div>
          <dl className="grid min-w-[280px] grid-cols-2 gap-x-5 gap-y-1 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-4 py-3 text-xs">
            <dt className="text-[var(--theme-muted)]">事件</dt>
            <dd className="text-right font-medium text-[var(--theme-ink)]">{eventName || "未记录"}</dd>
            <dt className="text-[var(--theme-muted)]">报告生成时间</dt>
            <dd className="text-right font-medium text-[var(--theme-ink)]">{generatedAt || "未记录"}</dd>
          </dl>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-2">
        {sections.map((section, index) => (
          <section key={section.chapterId} className="overflow-hidden rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-card)] shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
            <header className="flex items-center gap-3 border-b border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-4 py-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--theme-primary)] text-xs font-semibold text-white">
                {String(index + 1).padStart(2, "0")}
              </span>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--theme-muted)]">Story Chapter</p>
                <h3 className="text-sm font-semibold text-[var(--theme-ink)]">{section.title}</h3>
              </div>
            </header>

            <div className="space-y-5 p-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <ListBlock title="使用数据" items={section.dataItems} />
                <ListBlock title="数据来源" items={section.sources} />
              </div>

              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--theme-muted)]">处理过程</p>
                <div className="mt-2 space-y-2">
                  {section.processingSteps.map((step) => (
                    <div key={`${step.type}-${step.description}`} className="flex gap-3 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2.5">
                      <span className="mt-0.5 shrink-0 rounded-md bg-[var(--theme-selected-bg)] px-2 py-0.5 text-[10px] font-semibold text-[var(--theme-primary)]">
                        {PROCESS_LABELS[step.type]}
                      </span>
                      <p className="text-xs leading-5 text-[var(--theme-body)]">{step.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-3 border-t border-[var(--theme-border)] pt-4 sm:grid-cols-2">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--theme-muted)]">指标口径</p>
                  <ul className="mt-2 space-y-1 text-xs leading-5 text-[var(--theme-body)]">
                    {section.metricDefinitions.map((item) => <li key={item}>· {item}</li>)}
                  </ul>
                </div>
                <div className="space-y-3">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--theme-muted)]">支撑内容</p>
                    <p className="mt-1 text-xs leading-5 text-[var(--theme-body)]">{section.supports}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--theme-muted)]">数据完整性</p>
                    <p className="mt-1 text-xs leading-5 text-[var(--theme-body)]">{section.availabilityNote}</p>
                  </div>
                </div>
              </div>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
