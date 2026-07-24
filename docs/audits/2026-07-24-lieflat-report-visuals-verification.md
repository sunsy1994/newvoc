# Lieflat 报告可视化验证记录

验证日期：2026-07-24 至 2026-07-25  
分支：`codex/lieflat-ai-report-visuals`  
验证环境：Windows，真实本地 PostgreSQL，Next.js 14 production build

## 自动化验证

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 后端全量测试 | `python -m pytest -q -p no:cacheprovider` | exit 0；336 passed；1 个既有 LangGraph pending-deprecation warning |
| 前端类型检查 | `npm run typecheck`（`frontend`） | exit 0 |
| 前端生产构建 | `npm run build`（`frontend`） | exit 0；编译成功；30/30 静态页面生成成功 |
| 外部图表运行时扫描 | `rg -n "echarts\|chart\\.js\|cdn\\.jsdelivr\|dangerouslySetInnerHTML\|eval\\(" frontend/src/components/voc/report-visuals` | 无匹配 |
| diff 格式检查 | `git diff --check` | exit 0；仅 Windows LF/CRLF 提示 |
| PKO 稳定排序 | `test_l12_uses_comment_id_as_stable_tie_breaker` | 通过；互动量和发布时间相同时按 `comment_id` 升序 |
| PKO 真实总数 | `test_product_pko_real_report_path_keeps_up_to_fifty_renderable_records` | 通过；生产链路保留真实总数 60，确定性展示 50 |
| L12 缓存 meta | `test_l12_cache_meta_keeps_real_total_larger_than_displayed_data` | 通过；接受 `displayed_count=50/total_count=60`，拒绝总数小于展示数 |
| 事件图表叙事 | 两个 event report insight 测试 | 通过；固定映射、160 字上限、非字符串拒绝、空图不采用 LLM 推断 |
| 事件模式切换 | `test_event_report_view_toggle_exposes_pressed_state` | 通过；看板/报告按钮暴露 `aria-pressed` |
| 混合图表 SSR | `test_event_report_mixed_svg_and_legacy_charts_render_in_input_order` | 通过；SVG 与旧版图表保持输入顺序并由同一入口渲染 |
| 空状态 | `test_missing_data_stays_empty` 及九模板 renderability 参数化测试 | 通过；无业务数据时保留固定模板、给出 `empty_reason`，不生成演示数据 |

混合图表测试严格按 RED/GREEN 执行：新增测试首先因
`renderStructuredReportChart is not a function` 失败；导出最小统一渲染函数并复用到
`StructuredReportView` 后通过。

终审修复同样按 RED/GREEN 执行：新增的 PKO 真实总数、事件图表叙事与
`aria-pressed` 测试最初共 4 项失败，最小实现后全部通过。事件图表叙事固定映射为
F3/L14 使用市场章节、F6 使用产品章节、L13 使用销售章节；只有对应图表数据满足
SVG 渲染契约时才写入受限长度的 LLM 短结论，图表数值与 meta 仍全部来自确定性代码。

## 真实数据与服务检查

- 当前 shell 未直接设置 `DATABASE_URL`，但 `app.config` 提供了项目现有配置值。
- 未打印或写入数据库 DSN。
- 使用该配置执行 `select 1` 成功，证明真实本地 PostgreSQL 可连接。
- 真实事件接口 `GET /api/voc/events?limit=3` 返回 HTTP 200；验收事件为
  `EVT-2026-001`。
- `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` 可启动。
- build 后使用
  `node node_modules/next/dist/bin/next start -p 3000` 启动 production server，
  `GET /auto-voc` 返回 HTTP 200（响应体 54,873 bytes）。
- 所有本次启动的 uvicorn、Next.js、Chrome/Playwright 辅助进程在验证结束时均已终止；
  8000、3000、8001、3001 无遗留监听。

## 视觉验收状态

本次未能生成可信的 1280px/1440px 浏览器截图，因此不把视觉截图标记为通过。

实际阻塞证据：

1. `npm run dev` 在受限环境中失败，原始错误为 `Error: spawn EPERM`。
2. Playwright 自带 Chromium 未安装；改用本机 Chrome executable 后仍失败，
   原始错误为 `browserType.launch: spawn EPERM`。
3. 尝试授权 headless Chrome 截图的升级调用被中断，未产出截图。
4. production server 与真实数据库/API 本身可访问，但当前 Windows 子进程环境无法稳定
   启动受控浏览器，所以未执行以下逐页人工证据：市场摘要/图表、产品 L12/F7、
   销售图表、事件综合报告、报告资产重开，以及 1280/1440 对照。

可重复的安全替代证据是：

- Next.js production build 完整通过；
- React SSR 行为测试覆盖 SVG/legacy 混合渲染、闭合 registry、九个 SVG 模板、
  无效输入回退和显式空状态；
- 后端全量测试覆盖真实 chart spec 的固定顺序、数值转换、PKO 50 条上限和保存后原样返回；
- 源码扫描确认没有 ECharts、Chart.js、CDN、`dangerouslySetInnerHTML` 或 `eval`。

## 已知限制与后续验收

功能与构建验证通过，但视觉验收仍是明确的未完成项。应在 `PATH`/`Path` 已清理、
允许 Chrome 子进程启动的本机终端中，重新启动真实服务并补拍以下页面：

- 市场：摘要模式、图表模式；
- 产品：含 L12 与 F7 的图表模式；
- 销售：图表模式；
- 事件综合报告：报告模式；
- 报告资产：重开同一保存的 chart spec；
- 每个页面分别以 1280px 与 1440px 检查；
- 至少一个缺少相关数据的真实事件空状态。

在上述截图完成前，不应宣称浏览器视觉验收已完成。
