import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, Loader2, Route, ShieldCheck } from 'lucide-react';
import {
  getJourneyMatrix,
  getJourneyOverview,
  getJourneyPainpoints,
  getJourneyTouchpoints,
} from '@/lib/customer-journey-api';
import type {
  JourneyMatrixCell,
  JourneyOverviewResponse,
  JourneyPainpointItem,
  JourneyTouchpointListResponse,
} from '@/types/customerJourney';
import ActionSuggestions from './ActionSuggestions';
import ChannelStageMatrix from './ChannelStageMatrix';
import StageOverviewRail from './StageOverviewRail';
import TouchpointEvidenceList from './TouchpointEvidenceList';

interface PageState {
  loading: boolean;
  error: string;
  overview: JourneyOverviewResponse | null;
  matrix: JourneyMatrixCell[];
  touchpoints: JourneyTouchpointListResponse | null;
  painpoints: JourneyPainpointItem[];
}

export default function CustomerJourneyPage() {
  const [state, setState] = useState<PageState>({
    loading: true,
    error: '',
    overview: null,
    matrix: [],
    touchpoints: null,
    painpoints: [],
  });

  useEffect(() => {
    let mounted = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: '' }));
      try {
        const [overview, matrix, touchpoints, painpoints] = await Promise.all([
          getJourneyOverview(),
          getJourneyMatrix(),
          getJourneyTouchpoints({ pageSize: 20 }),
          getJourneyPainpoints(),
        ]);
        if (!mounted) return;
        setState({ loading: false, error: '', overview, matrix, touchpoints, painpoints });
      } catch (error) {
        if (!mounted) return;
        setState({
          loading: false,
          error: error instanceof Error ? error.message : '真实数据接口不可用',
          overview: null,
          matrix: [],
          touchpoints: null,
          painpoints: [],
        });
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const summary = useMemo(() => {
    const stages = state.overview?.stages ?? [];
    const touchpointCount = stages.reduce((sum, item) => sum + item.touchpointCount, 0);
    const activeStages = stages.filter((item) => item.touchpointCount > 0).length;
    const channelCount = new Set(state.matrix.map((item) => item.sourceChannel)).size;
    return { touchpointCount, activeStages, channelCount };
  }, [state.matrix, state.overview]);

  return (
    <div className="min-h-screen bg-[#f5f7fb] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.header
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-950">
                <Route className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-950">VOC 看用户</p>
                <p className="text-xs text-slate-500">渠道级客户旅程分析，不做跨渠道身份打通</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs text-slate-600">
              <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-slate-50 px-3 py-1">
                <Database className="h-3.5 w-3.5" /> 真实触点
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">
                <ShieldCheck className="h-3.5 w-3.5" /> 不跨渠道合并用户
              </span>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-3">
            <Metric label="触点数" value={summary.touchpointCount} />
            <Metric label="有数据阶段" value={summary.activeStages} />
            <Metric label="覆盖渠道" value={summary.channelCount} />
          </div>
        </motion.header>

        {state.loading ? (
          <div className="flex min-h-[360px] items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-500">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            加载真实旅程数据...
          </div>
        ) : state.error ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900">
            未展示样例数据。请先启动后端、导入触点数据并运行用户旅程ETL。接口信息：{state.error}
          </div>
        ) : (
          <main className="space-y-6">
            <StageOverviewRail stages={state.overview?.stages ?? []} />
            <ChannelStageMatrix cells={state.matrix} />
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.05fr_0.95fr]">
              <TouchpointEvidenceList total={state.touchpoints?.total ?? 0} items={state.touchpoints?.items ?? []} />
              <ActionSuggestions items={state.painpoints} />
            </div>
          </main>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-950">{value.toLocaleString('zh-CN')}</p>
    </div>
  );
}
