import type { ProductStorylineView } from "@/components/voc/report-summary/productStorylineData";

type ReportSummaryStorylineProps = {
  storyline: ProductStorylineView;
  summaryLabel?: string;
};

export function ReportSummaryStoryline({ storyline, summaryLabel = "事件综合摘要" }: ReportSummaryStorylineProps) {
  return (
    <div className="space-y-6">
      <section
        data-report-storyline-hero
        className="relative overflow-hidden rounded-[24px] border border-[var(--theme-border)] bg-gradient-to-br from-[var(--theme-selected-bg)] to-[var(--theme-white)] p-6 md:p-8"
      >
        <div
          aria-hidden="true"
          className="absolute -right-16 -top-24 h-56 w-56 rounded-full bg-[var(--theme-primary)] opacity-[0.08] blur-3xl"
        />
        <div className="relative max-w-4xl">
          {storyline.eventName ? (
            <p
              data-report-event-identity
              className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--theme-primary)]"
            >
              {storyline.eventName} · {summaryLabel}
            </p>
          ) : null}
          <h2 className="mt-3 text-2xl font-semibold leading-tight tracking-tight text-[var(--theme-ink)] md:text-3xl">
            {storyline.headline}
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--theme-body)] md:text-base">
            {storyline.lead}
          </p>
          {storyline.heroMetrics.length ? (
            <div className="mt-5 flex flex-wrap gap-2">
              {storyline.heroMetrics.map((metric) => (
                <div
                  key={`${metric.label}-${metric.value}`}
                  data-storyline-hero-metric
                  className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 py-2"
                >
                  <p className="text-[11px] font-medium text-[var(--theme-primary)]">
                    {metric.label}
                  </p>
                  <p className="mt-0.5 text-sm font-semibold text-[var(--theme-ink)]">
                    {metric.value}
                  </p>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      <div className="relative">
        <div
          aria-hidden="true"
          className="absolute bottom-7 left-5 top-7 w-px bg-[var(--theme-primary)] opacity-20"
        />
        <ol className="space-y-4">
          {storyline.chapters.map((chapter, index) => {
            const hasSupportingData = chapter.metrics.length > 0 || chapter.evidence.length > 0;

            return (
              <li
                key={chapter.chapterId}
                data-story-chapter={chapter.chapterId}
                className="relative pl-14"
              >
                <div
                  aria-hidden="true"
                  className="absolute left-0 top-5 flex h-10 w-10 items-center justify-center rounded-full bg-[var(--theme-primary)] text-xs font-semibold tracking-[0.08em] text-[var(--theme-white)] opacity-90"
                >
                  {String(index + 1).padStart(2, "0")}
                </div>
                <article className="rounded-[22px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 md:p-6">
                  <div
                    className={
                      hasSupportingData
                        ? "grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px] lg:gap-7"
                        : undefined
                    }
                  >
                    <div className="min-w-0">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--theme-primary)]">
                        章节 {String(index + 1).padStart(2, "0")}
                      </p>
                      <h3 className="mt-2 text-lg font-semibold tracking-tight text-[var(--theme-ink)]">
                        {chapter.title}
                      </h3>
                      <p className="mt-3 text-base font-semibold leading-7 text-[var(--theme-ink)]">
                        {chapter.conclusion}
                      </p>
                      {chapter.body ? (
                        <p className="mt-2 text-sm leading-7 text-[var(--theme-body)]">
                          {chapter.body}
                        </p>
                      ) : null}
                    </div>

                    {hasSupportingData ? (
                      <aside className="space-y-3 border-t border-[var(--theme-border)] pt-4 lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
                        {chapter.metrics.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {chapter.metrics.map((metric, metricIndex) => (
                              <div
                                key={`${metricIndex}-${metric.label}-${metric.value}`}
                                className="rounded-xl bg-[var(--theme-selected-bg)] px-3 py-2"
                              >
                                <p className="text-[11px] font-medium leading-4 text-[var(--theme-primary)]">
                                  {metric.label}
                                </p>
                                <p className="mt-0.5 text-sm font-semibold text-[var(--theme-ink)]">
                                  {metric.value}
                                </p>
                              </div>
                            ))}
                          </div>
                        ) : null}

                        {chapter.evidence.map((evidence, evidenceIndex) => (
                          <blockquote
                            key={`${evidenceIndex}-${evidence.commentId}`}
                            className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-3"
                          >
                            <p className="text-xs font-semibold text-[var(--theme-primary)]">
                              真实评论
                            </p>
                            <p className="mt-1.5 text-sm leading-6 text-[var(--theme-ink)]">
                              “{evidence.commentText}”
                            </p>
                            <footer className="mt-2 text-xs text-[var(--theme-muted)]">
                              {evidence.dimension} · {evidence.target}
                            </footer>
                          </blockquote>
                        ))}
                      </aside>
                    ) : null}
                  </div>
                </article>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
