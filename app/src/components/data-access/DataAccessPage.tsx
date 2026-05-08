import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Cable,
  Database,
  FileSpreadsheet,
  Files,
  FolderSync,
  Layers3,
  Link2,
  ScrollText,
  Sigma,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getDataAccessOverview } from '@/lib/data-access-api';
import type { AssetPageChangeHandler } from '@/components/assets/assetNavigation';
import type { DataAccessOverview } from '@/types/dataAccess';

interface DataAccessPageProps {
  onPageChange: AssetPageChangeHandler;
}

const toneClasses = {
  blue: 'bg-blue-50 text-blue-700 border-blue-200',
  emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  amber: 'bg-amber-50 text-amber-700 border-amber-200',
  slate: 'bg-slate-50 text-slate-700 border-slate-200',
} as const;

export default function DataAccessPage({ onPageChange }: DataAccessPageProps) {
  const [overview, setOverview] = useState<DataAccessOverview | null>(null);

  useEffect(() => {
    getDataAccessOverview().then(setOverview);
  }, []);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(31,111,235,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(16,185,129,0.10),_transparent_28%),linear-gradient(180deg,_#f5f8fc,_#edf2f7)] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.section
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm"
        >
          <div className="grid gap-0 lg:grid-cols-[1.25fr,0.85fr]">
            <div className="p-6">
              <Badge className="rounded-full bg-slate-900 px-3 py-1 text-xs text-white">Data Access Control</Badge>
              <h1 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight text-slate-950">
                数据接入
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                把个人维护的 Excel、CSV、文本数据统一接入 PostgreSQL，沉淀成内容、评论、事件、账号四类标准明细，
                再向数据资产页面稳定供数。
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Button className="gap-2 bg-slate-950 hover:bg-slate-800" onClick={() => onPageChange('data-import')}>
                  进入数据导入
                </Button>
                <Button variant="outline" className="gap-2" onClick={() => onPageChange('data-calc')}>
                  进入数据计算
                  <Sigma className="h-4 w-4" />
                </Button>
                <Button variant="outline" className="gap-2" asChild>
                  <a href="/data-access-schema.sql" target="_blank" rel="noreferrer">
                    查看 PostgreSQL 设计
                    <Database className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>

            <div className="border-l border-slate-200 bg-[linear-gradient(135deg,_#0f172a,_#172554_55%,_#14532d)] p-6 text-white">
              <p className="text-xs uppercase tracking-[0.24em] text-blue-100/80">Pipeline</p>
              <div className="mt-5 space-y-3">
                {[
                  ['01', '本地 Excel / 文本', '先在熟悉的模板里维护数据'],
                  ['02', '模板校验与主键补齐', '导入时生成 content_id / comment_id / account_id'],
                  ['03', 'PostgreSQL 标准化落库', '明细层、关系层、汇总层分开入库'],
                  ['04', '前端统一读接口', '页面不再直接依赖散落文件'],
                ].map(([step, title, desc]) => (
                  <div key={step} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full border border-white/15 bg-white/10 text-sm font-semibold">
                        {step}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{title}</p>
                        <p className="text-xs text-blue-100/75">{desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {overview?.summary.map((item) => (
            <div key={item.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className={`inline-flex rounded-full border px-2.5 py-1 text-xs ${toneClasses[item.tone]}`}>
                {item.label}
              </div>
              <p className="mt-4 text-3xl font-semibold text-slate-950">{item.value}</p>
              <p className="mt-2 text-sm text-slate-500">{item.hint}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.2fr,0.8fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">接入范围</p>
                <p className="text-xs text-slate-500">每个数据源对应一个导入模板，导入后落到标准主表。</p>
              </div>
              <Layers3 className="h-4 w-4 text-slate-400" />
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {overview?.sources.map((source) => (
                <div key={source.id} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white text-slate-700 shadow-sm">
                        {source.type === 'text' ? <ScrollText className="h-5 w-5" /> : <FileSpreadsheet className="h-5 w-5" />}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-950">{source.name}</p>
                        <p className="text-xs text-slate-500">{source.targetTable}</p>
                      </div>
                    </div>
                    <Badge className={source.status === 'ready' ? 'bg-emerald-100 text-emerald-700' : source.status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}>
                      {source.status === 'ready' ? '就绪' : source.status === 'pending' ? '待导入' : '异常'}
                    </Badge>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-xs text-slate-500">记录数</p>
                      <p className="mt-1 font-semibold text-slate-900">{source.recordCount}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">最近同步</p>
                      <p className="mt-1 text-slate-700">{source.lastSyncAt}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">PostgreSQL 目标</p>
                  <p className="text-xs text-slate-500">当前按数据资产口径预留标准表。</p>
                </div>
                <Database className="h-4 w-4 text-slate-400" />
              </div>
              <div className="mt-4 rounded-2xl bg-slate-950 p-4 text-sm text-slate-100">
                <p>database: {overview?.postgres.currentDatabase}</p>
                <p className="mt-1">schema: {overview?.postgres.schemaName}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {overview?.postgres.tables.map((table) => (
                    <Badge key={table} className="bg-white/10 text-slate-100">
                      {table}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">接口骨架</p>
                  <p className="text-xs text-slate-500">前端已按真实调用签名接好。</p>
                </div>
                <Cable className="h-4 w-4 text-slate-400" />
              </div>
              <div className="mt-4 space-y-2">
                {overview?.postgres.keyInterfaces.map((item) => (
                  <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50/70 px-3 py-2 font-mono text-xs text-slate-700">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">最近导入任务</p>
                <p className="text-xs text-slate-500">失败任务可以回到数据导入页重新校验模板。</p>
              </div>
              <FolderSync className="h-4 w-4 text-slate-400" />
            </div>
            <div className="mt-4 space-y-3">
              {overview?.jobs.map((job) => (
                <div key={job.id} className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-slate-950">{job.fileName}</p>
                      <p className="mt-1 text-xs text-slate-500">{job.sourceName} · {job.templateName}</p>
                    </div>
                    <Badge className={job.status === 'success' ? 'bg-emerald-100 text-emerald-700' : job.status === 'running' ? 'bg-blue-100 text-blue-700' : job.status === 'queued' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}>
                      {job.status === 'success' ? '成功' : job.status === 'running' ? '运行中' : job.status === 'queued' ? '排队中' : '失败'}
                    </Badge>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-500 md:grid-cols-4">
                    <p>任务号：<span className="font-medium text-slate-800">{job.id}</span></p>
                    <p>操作人：<span className="font-medium text-slate-800">{job.createdBy}</span></p>
                    <p>写入：<span className="font-medium text-slate-800">{job.insertedRows}</span></p>
                    <p>拒绝：<span className="font-medium text-slate-800">{job.rejectedRows}</span></p>
                  </div>
                  <p className="mt-3 text-sm text-slate-600">{job.message}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">打通方式</p>
                <p className="text-xs text-slate-500">适合你当前个人维护模式。</p>
              </div>
              <Link2 className="h-4 w-4 text-slate-400" />
            </div>
            <div className="mt-4 space-y-3">
              {[
                '你继续维护 Excel / 文本文档，不需要改变当前工作习惯。',
                '统一按模板导入，系统在接口层做字段校验和主键补齐。',
                '数据先进入 PostgreSQL，再由前端统一读接口，不再直接依赖散文件。',
                '后续要接自动标签、汇总计算、检索能力，都可以在数据库层继续叠加。',
              ].map((item) => (
                <div key={item} className="flex gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                  <Files className="mt-0.5 h-4 w-4 text-slate-500" />
                  <p className="text-sm leading-6 text-slate-700">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
