import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronRight,
  Database,
  FileCode2,
  GitBranchPlus,
  Play,
  ScrollText,
  TimerReset,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { AssetPageChangeHandler } from '@/components/assets/assetNavigation';
import { getCalcGraph, getCalcTaskDetail, getCalcTasks, runCalcTask } from '@/lib/data-calc-api';
import type { CalcGraphResponse, CalcTask, CalcTaskDetail } from '@/types/dataCalc';

interface DataCalcPageProps {
  onPageChange: AssetPageChangeHandler;
}

const groupStyles = {
  source: 'bg-slate-100 text-slate-700',
  task: 'bg-blue-100 text-blue-700',
  output: 'bg-emerald-100 text-emerald-700',
} as const;

export default function DataCalcPage({ onPageChange }: DataCalcPageProps) {
  const [tasks, setTasks] = useState<CalcTask[]>([]);
  const [graph, setGraph] = useState<CalcGraphResponse>({ nodes: [], edges: [] });
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedTaskDetail, setSelectedTaskDetail] = useState<CalcTaskDetail | null>(null);
  const [runMessage, setRunMessage] = useState('');

  useEffect(() => {
    getCalcTasks().then(setTasks);
    getCalcGraph().then(setGraph);
  }, []);

  useEffect(() => {
    if (!selectedTaskId) return;
    getCalcTaskDetail(selectedTaskId).then(setSelectedTaskDetail);
  }, [selectedTaskId]);

  const stats = useMemo(() => {
    const enabled = tasks.filter((item) => item.isEnabled).length;
    const running = tasks.filter((item) => item.status === 'running').length;
    const success = tasks.filter((item) => item.status === 'success').length;
    return { enabled, running, success, total: tasks.length };
  }, [tasks]);

  const runTask = async (taskId: string) => {
    const result = await runCalcTask(taskId);
    setRunMessage(result.message);
    const nextTasks = await getCalcTasks();
    setTasks(nextTasks);
    if (selectedTaskId === taskId) {
      const detail = await getCalcTaskDetail(taskId);
      setSelectedTaskDetail(detail);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f7f9fc] via-[#f4f8fb] to-[#edf2f7] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.section
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <button onClick={() => onPageChange('data-access')} className="rounded-md px-2 py-1 hover:bg-slate-100">
                  返回数据接入
                </button>
                <ChevronRight className="h-4 w-4" />
                <span>数据计算</span>
              </div>
              <h1 className="mt-2 text-2xl font-semibold text-slate-950">数据计算</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                通过 Python + pandas 执行计算任务，把导入的明细表加工成事件库、作者库、KOL库可直接查询的服务表。
              </p>
            </div>
            <div className="rounded-3xl bg-slate-950 px-4 py-3 text-sm text-white">
              <p className="font-medium">执行方式</p>
              <p className="mt-1 text-slate-300">FastAPI 调度任务脚本，pandas 读表和写表。</p>
            </div>
          </div>
        </motion.section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            ['任务总数', stats.total, '已注册计算任务'],
            ['启用任务', stats.enabled, '当前可运行'],
            ['运行中', stats.running, '正在计算'],
            ['成功任务', stats.success, '最近一次执行成功'],
          ].map(([label, value, hint]) => (
            <div key={String(label)} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
              <p className="mt-2 text-sm text-slate-500">{hint}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.15fr,0.85fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">可视化任务流</p>
                <p className="text-xs text-slate-500">从明细表，经 pandas 任务，流向服务表。</p>
              </div>
              <GitBranchPlus className="h-4 w-4 text-slate-400" />
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {(['source', 'task', 'output'] as const).map((group) => (
                <div key={group} className="space-y-3">
                  <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">
                    {group === 'source' ? 'Source Tables' : group === 'task' ? 'Pandas Tasks' : 'Output Tables'}
                  </p>
                  {graph.nodes.filter((node) => node.group === group).map((node) => (
                    <div key={node.id} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-medium text-slate-900">{node.name}</p>
                        <Badge className={groupStyles[node.group]}>{node.group}</Badge>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">{node.description}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">运行模型</p>
                  <p className="text-xs text-slate-500">每个任务都对应一个真实 Python 脚本。</p>
                </div>
                <FileCode2 className="h-4 w-4 text-slate-400" />
              </div>
              <div className="mt-4 space-y-3 text-sm text-slate-700">
                {[
                  '任务元数据保存在后端注册表，前端读取后可视化展示。',
                  'FastAPI 接口可运行单个任务，并记录执行历史。',
                  '脚本内容可直接查看，便于你确认 pandas 逻辑。',
                  '输出表建议以 replace 或 delete + insert 的方式刷新。',
                ].map((item) => (
                  <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            {runMessage && (
              <div className="rounded-3xl border border-emerald-200 bg-emerald-50/80 p-4 text-sm text-emerald-800 shadow-sm">
                {runMessage}
              </div>
            )}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900">任务列表</p>
              <p className="text-xs text-slate-500">点击任务查看脚本内容、输入输出表和运行历史。</p>
            </div>
            <Database className="h-4 w-4 text-slate-400" />
          </div>
          <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>任务</TableHead>
                  <TableHead>分组</TableHead>
                  <TableHead>输入表</TableHead>
                  <TableHead>输出表</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tasks.map((task) => (
                  <TableRow key={task.taskId}>
                    <TableCell>
                      <div>
                        <p className="font-medium text-slate-900">{task.taskName}</p>
                        <p className="text-xs text-slate-500">{task.taskDesc}</p>
                      </div>
                    </TableCell>
                    <TableCell>{task.taskGroup}</TableCell>
                    <TableCell className="text-xs text-slate-600">{task.inputTables.join(', ')}</TableCell>
                    <TableCell className="text-xs text-slate-600">{task.outputTables.join(', ')}</TableCell>
                    <TableCell>
                      <Badge className={task.status === 'success' ? 'bg-emerald-100 text-emerald-700' : task.status === 'running' ? 'bg-blue-100 text-blue-700' : task.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'}>
                        {task.status === 'success' ? '成功' : task.status === 'running' ? '运行中' : task.status === 'failed' ? '失败' : '未运行'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedTaskId(task.taskId)}>
                          查看详情
                        </Button>
                        <Button size="sm" className="h-7 gap-1 px-2 text-xs bg-slate-950 hover:bg-slate-800" onClick={() => runTask(task.taskId)}>
                          <Play className="h-3.5 w-3.5" />
                          运行
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>
      </div>

      <Sheet open={Boolean(selectedTaskId)} onOpenChange={(open) => !open && setSelectedTaskId(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-2xl">
          {selectedTaskDetail && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedTaskDetail.taskName}</SheetTitle>
                <SheetDescription>{selectedTaskDetail.taskDesc}</SheetDescription>
              </SheetHeader>
              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                  <div className="grid grid-cols-2 gap-3 text-slate-700">
                    <p>脚本路径：{selectedTaskDetail.scriptPath}</p>
                    <p>入口函数：{selectedTaskDetail.entryFunc}</p>
                    <p>运行模式：{selectedTaskDetail.runMode}</p>
                    <p>最近运行：{selectedTaskDetail.lastRunAt ?? '-'}</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
                    <FileCode2 className="h-4 w-4 text-blue-600" />
                    pandas 脚本内容
                  </div>
                  <pre className="mt-3 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                    <code>{selectedTaskDetail.scriptContent}</code>
                  </pre>
                </div>

                <div className="rounded-2xl border border-slate-200 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
                    <TimerReset className="h-4 w-4 text-emerald-600" />
                    最近运行记录
                  </div>
                  <div className="mt-3 space-y-3">
                    {selectedTaskDetail.recentRuns.length === 0 ? (
                      <p className="text-xs text-slate-500">暂无运行记录。</p>
                    ) : (
                      selectedTaskDetail.recentRuns.map((run) => (
                        <div key={run.runId} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="font-medium text-slate-900">{run.runId}</p>
                            <Badge className={run.status === 'success' ? 'bg-emerald-100 text-emerald-700' : run.status === 'running' ? 'bg-blue-100 text-blue-700' : run.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}>
                              {run.status}
                            </Badge>
                          </div>
                          <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-600">
                            <p>开始：{run.startedAt}</p>
                            <p>结束：{run.finishedAt ?? '-'}</p>
                            <p>处理行数：{run.processedRows}</p>
                            <p>输出行数：{run.outputRows}</p>
                          </div>
                          {run.logPath && (
                            <div className="mt-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-500">
                              <ScrollText className="mr-1 inline h-3.5 w-3.5" />
                              {run.logPath}
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
