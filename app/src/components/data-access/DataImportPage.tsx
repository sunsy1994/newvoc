import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle2,
  ChevronRight,
  Download,
  FileSpreadsheet,
  Files,
  FolderUp,
  Orbit,
  PlugZap,
  RefreshCcw,
  ScrollText,
  ServerCog,
  ShieldCheck,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { AssetPageChangeHandler } from '@/components/assets/assetNavigation';
import { createImportJob, getImportJobs, getImportTemplates } from '@/lib/data-access-api';
import type { DataSourceTemplate, ImportJob } from '@/types/dataAccess';

interface DataImportPageProps {
  onPageChange: AssetPageChangeHandler;
}

export default function DataImportPage({ onPageChange }: DataImportPageProps) {
  const [templates, setTemplates] = useState<DataSourceTemplate[]>([]);
  const [jobs, setJobs] = useState<ImportJob[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('tpl-content');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [operator, setOperator] = useState('local-admin');
  const [submitMessage, setSubmitMessage] = useState('');

  useEffect(() => {
    getImportTemplates().then(setTemplates);
    getImportJobs().then(setJobs);
  }, []);

  const selectedTemplate = useMemo(
    () => templates.find((item) => item.id === selectedTemplateId) ?? templates[0],
    [selectedTemplateId, templates]
  );

  const handleCreateJob = async () => {
    if (!selectedTemplate || !selectedFile) return;
    const result = await createImportJob({
      sourceKey: selectedTemplate.sourceKey,
      templateId: selectedTemplate.id,
      operator,
      file: selectedFile,
    });
    setSubmitMessage(result.message);
    const nextJobs = await getImportJobs();
    setJobs(nextJobs);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f7f9fc] via-[#f3f7fb] to-[#ebf1f7] p-6">
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
                <span>数据导入</span>
              </div>
              <h1 className="mt-2 text-2xl font-semibold text-slate-950">数据导入</h1>
              <p className="mt-2 text-sm text-slate-500">
                每类数据源使用独立模板。先下载模板填充，再通过统一接口提交导入任务。
              </p>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-600">
              <p className="font-medium text-slate-900">推荐流程</p>
              <p className="mt-1">下载模板 → 填表 → 提交导入 → 校验结果 → 进入 PostgreSQL</p>
            </div>
          </div>
        </motion.section>

        <section className="grid gap-4 xl:grid-cols-[1.1fr,0.9fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">模板中心</p>
                <p className="text-xs text-slate-500">需要几个数据源，就准备几个标准模板。</p>
              </div>
              <Files className="h-4 w-4 text-slate-400" />
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {templates.map((template) => (
                <div key={template.id} className={`rounded-3xl border p-4 transition-colors ${selectedTemplateId === template.id ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-slate-50/60'}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold">{template.sourceName}</p>
                      <p className={`mt-1 text-xs ${selectedTemplateId === template.id ? 'text-slate-300' : 'text-slate-500'}`}>
                        {template.description}
                      </p>
                    </div>
                    <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${selectedTemplateId === template.id ? 'bg-white/10' : 'bg-white'}`}>
                      {template.formats.includes('txt') ? <ScrollText className="h-5 w-5" /> : <FileSpreadsheet className="h-5 w-5" />}
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <Badge className={selectedTemplateId === template.id ? 'bg-white/10 text-white' : 'bg-slate-200 text-slate-700'}>
                      {template.fileName}
                    </Badge>
                    <Badge className={selectedTemplateId === template.id ? 'bg-emerald-500/20 text-emerald-200' : 'bg-emerald-100 text-emerald-700'}>
                      {template.formats.join(' / ').toUpperCase()}
                    </Badge>
                  </div>

                  <div className="mt-4 flex gap-2">
                    <Button
                      size="sm"
                      variant={selectedTemplateId === template.id ? 'secondary' : 'outline'}
                      className="h-8"
                      onClick={() => setSelectedTemplateId(template.id)}
                    >
                      设为当前模板
                    </Button>
                    <Button size="sm" variant="outline" className="h-8 bg-white" asChild>
                      <a href={template.downloadPath} download>
                        <Download className="mr-1 h-3.5 w-3.5" />
                        下载
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">提交导入任务</p>
                <p className="text-xs text-slate-500">当前先接统一接口签名，后端服务接上即可真实导入。</p>
              </div>
              <FolderUp className="h-4 w-4 text-slate-400" />
            </div>

            <div className="mt-4 space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-xs text-slate-500">当前模板</p>
                <p className="mt-1 text-sm font-semibold text-slate-950">{selectedTemplate?.sourceName}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {selectedTemplate?.requiredFields.map((field) => (
                    <Badge key={field} className="bg-slate-900 text-white">{field}</Badge>
                  ))}
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {selectedTemplate?.optionalFields.map((field) => (
                    <Badge key={field} variant="outline">{field}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">模板选择</p>
                <Select value={selectedTemplateId} onValueChange={setSelectedTemplateId}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择模板" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.sourceName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">选择文件</p>
                <Input
                  type="file"
                  accept=".csv,.xlsx,.txt"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
                <p className="mt-2 text-xs text-slate-500">
                  当前文件：{selectedFile?.name ?? '未选择文件'}
                </p>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">操作人</p>
                <Input value={operator} onChange={(event) => setOperator(event.target.value)} placeholder="local-admin" />
              </div>

              <div className="rounded-2xl border border-blue-100 bg-blue-50/70 p-4 text-sm text-blue-950">
                <p className="font-medium">接口请求</p>
                <p className="mt-2 font-mono text-xs">POST /api/data-import/jobs</p>
                <p className="mt-2 text-xs text-blue-800">
                  请求体为 `multipart/form-data`，字段包含 `source_key`、`template_id`、`operator`、`file`。
                </p>
              </div>

              <Button
                className="w-full gap-2 bg-slate-950 hover:bg-slate-800"
                onClick={handleCreateJob}
                disabled={!selectedFile}
              >
                <PlugZap className="h-4 w-4" />
                创建导入任务
              </Button>

              {submitMessage && (
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4 text-sm text-emerald-800">
                  {submitMessage}
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.2fr,0.8fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">导入任务记录</p>
                <p className="text-xs text-slate-500">统一看状态、写入行数和拒绝原因。</p>
              </div>
              <RefreshCcw className="h-4 w-4 text-slate-400" />
            </div>

            <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>任务</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>写入</TableHead>
                    <TableHead>拒绝</TableHead>
                    <TableHead>时间</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium text-slate-900">{job.fileName}</p>
                          <p className="text-xs text-slate-500">{job.id}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={job.status === 'success' ? 'bg-emerald-100 text-emerald-700' : job.status === 'running' ? 'bg-blue-100 text-blue-700' : job.status === 'queued' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}>
                          {job.status === 'success' ? '成功' : job.status === 'running' ? '运行中' : job.status === 'queued' ? '排队中' : '失败'}
                        </Badge>
                      </TableCell>
                      <TableCell>{job.insertedRows}</TableCell>
                      <TableCell>{job.rejectedRows}</TableCell>
                      <TableCell>{job.createdAt}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">校验规则</p>
                  <p className="text-xs text-slate-500">先把导入质量控住，再谈分析。</p>
                </div>
                <ShieldCheck className="h-4 w-4 text-slate-400" />
              </div>
              <div className="mt-4 space-y-3 text-sm text-slate-700">
                {[
                  '缺少模板必填字段直接拒绝导入。',
                  '没有原始主键时，导入脚本按链接或文本哈希补统一 ID。',
                  '作者与评论作者统一写入 account 池，避免后续画像断裂。',
                  '内容可关联多个事件，关系表单独维护，不在内容表里硬编码。',
                ].map((item) => (
                  <div key={item} className="flex gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
                    <p>{item}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">后端交付物</p>
                  <p className="text-xs text-slate-500">前后端对接时需要的最小集合。</p>
                </div>
                <ServerCog className="h-4 w-4 text-slate-400" />
              </div>
              <div className="mt-4 space-y-2">
                {[
                  'PostgreSQL schema: data_asset',
                  'SQL: /data-access-schema.sql',
                  'API: /data-import-api-contract.md',
                  '模板文件: /data-import-templates/*.csv',
                  '前端适配层: src/lib/data-access-api.ts',
                ].map((item) => (
                  <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50/70 px-3 py-2 font-mono text-xs text-slate-700">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-[linear-gradient(135deg,_#0f172a,_#1d4ed8_65%,_#0f766e)] p-5 text-white shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold">下一步</p>
                  <p className="mt-1 text-xs text-white/75">继续往真服务推进时，先做导入接口和文件落地。</p>
                </div>
                <Orbit className="h-4 w-4 text-white/75" />
              </div>
              <div className="mt-4 space-y-2 text-sm text-white/85">
                <p>1. 接 `POST /api/data-import/jobs` 的真实文件上传。</p>
                <p>2. 导入脚本写入 PostgreSQL 的 `dwd_*` 和 `rel_*`。</p>
                <p>3. 再补标签任务和 ADS 汇总任务。</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
