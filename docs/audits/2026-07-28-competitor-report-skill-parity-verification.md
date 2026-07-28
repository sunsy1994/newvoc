# 竞品报告 Skill Parity 验证记录

验证日期：2026-07-28

工作区：`D:\voc\story1\.worktrees\competitor-report-skill-parity`

范围：Task 4 自动化集成与 reviewer 修复；浏览器对照由主任务执行

## 成功标准与自动化证据

| 成功标准 | 自动化证据 | 结果 |
| --- | --- | --- |
| AI 报告请求返回并保存 `2026-05-25` 至 `2026-05-31` | `test_competitor_report_closes_ai_save_asset_service_and_http_route_loop` 使用明确年份请求“生成2026年5月最后一周的竞品动态报告”，通过真实 `/api/agents/run`、dispatcher、graph 和确定性 scope resolver；断言响应 `time_scope`、回答文本和数据库写入范围一致 | 通过 |
| 保存后的同一报告可从 HTTP asset API 取回 | 同一闭环测试执行真实 renderer、`save_competitor_report_agent_result`、`get_report_asset` 和 `/api/assets/reports/competitor_report/{report_run_id}`；只替换 LLM、数据查询和 psycopg 数据库连接边界；GET 返回的 `report_run_id` 与 POST 创建值相同 | 通过 |
| 资产返回完整 McKinsey HTML | 闭环 GET 响应断言 `view_kind="html"`、报告内 scope、`McKinsey Consulting`、Top3、账号贡献、经销商章节，四个 chart ID 与四个 `echarts.init` 调用，包含 Sankey | 通过 |
| 聊天消息链接到新建竞品报告资产 | `test_auto_voc_competitor_report_request_and_asset_action_contract` 精确断言链接使用响应中的 `report_run_id`：`/assets/reports?report_type=competitor_report&report_run_id=...` | 通过 |
| 事件报告资产保持原结构化视图 | `test_report_asset_detail_returns_only_the_required_event_or_html_view` 精确断言 event report 的 `view_kind="structured"` 和原 `structured_report` payload；前端仍走 `StructuredReportView` | 通过 |
| iframe 允许运行本地 ECharts，同时保持 origin 隔离 | `test_report_assets_fetch_typed_detail_and_render_html_in_an_origin_isolated_script_iframe` 解析真实 iframe 的 sandbox token，要求恰为 `allow-scripts`；显式拒绝 `allow-same-origin`、forms、popups、top navigation 和 downloads；仍拒绝父页面 `dangerouslySetInnerHTML` | 自动化契约通过；浏览器运行待验 |

## TDD 记录

reviewer 指出的 iframe 阻断问题已按 RED/GREEN 执行：

- RED：
  `python -m pytest tests/test_next_frontend_architecture.py::test_report_assets_fetch_typed_detail_and_render_html_in_an_origin_isolated_script_iframe -q -p no:cacheprovider`
  以 exit 1 失败；实际 sandbox token 为 `[]`，期望 `["allow-scripts"]`。
- 最小生产修改：只把报告 iframe 从 `sandbox=""` 改为
  `sandbox="allow-scripts"`，未增加任何其他 capability。
- GREEN：同一测试 exit 0，`1 passed`。

闭环集成测试补的是 reviewer 发现的证据缺口。实际 save→asset service→HTTP route
生产 seam 已经存在，因此移除 renderer/storage/route mock 并接入同一内存数据库边界后
首次运行即通过；没有为制造 RED 而扩大生产接口。旧的“测试自行生成 HTML 再注入资产
service”的 McKinsey 断言已删除，避免把独立 fixture 误称为 HTTP 闭环。

无年份墙钟依赖已移除：闭环请求改为显式 `2026年5月最后一周`，并额外断言回答文本、
保存行、取回 HTML 都包含相同日期范围。

## 执行命令与结果

所有 Python 命令均从上述 worktree 执行；前端命令的工作目录为 `frontend`。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| reviewer 三项 focused | `python -m pytest tests/test_task_api.py::test_competitor_report_closes_ai_save_asset_service_and_http_route_loop tests/test_asset_library.py::test_report_asset_detail_returns_only_the_required_event_or_html_view tests/test_next_frontend_architecture.py::test_report_assets_fetch_typed_detail_and_render_html_in_an_origin_isolated_script_iframe -q -p no:cacheprovider` | exit 0；3 passed，5 warnings；6.79s |
| Task 4 focused suite | `python -m pytest tests/test_task_api.py tests/test_asset_library.py tests/test_next_frontend_architecture.py -q -p no:cacheprovider` | exit 0；143 passed，46 warnings；19.69s |
| 后端全量回归 | `python -m pytest -q -p no:cacheprovider` | exit 0；546 passed，60 warnings；28.14s |
| 前端类型检查 | `npm run typecheck` | exit 0；`tsc --noEmit` 无错误 |
| 前端 production build | `npm run build` | exit 0；Next.js 14.2.35 编译、lint/type validity 检查通过；静态页面 30/30 |

pytest warnings 均为现有依赖告警：Starlette `python_multipart`、Pydantic V2
deprecated `Field` 参数、Pydantic protected namespace、LangGraph checkpoint pending
deprecation，以及 TestClient 使用 httpx `app` shortcut 的 deprecation。没有测试失败。

## iframe 安全边界

报告 HTML 必须执行内联的项目本地 ECharts，完全禁脚本会让四个 chart 容器保持空白。
当前 viewer 只授予 `allow-scripts`：

- 不授予 `allow-same-origin`，`srcDoc` 报告保持 opaque origin；
- 不授予表单、弹窗、顶层导航、下载或逃逸 sandbox 的能力；
- 保留 `referrerPolicy="no-referrer"`；
- HTML 只进入 iframe `srcDoc`，不注入 React 宿主 DOM。

自动化源代码契约能防止 capability 回归，但不能替代浏览器对 sandbox 实际行为和
ECharts canvas 的运行时检查。

## 浏览器对照待验项

本子任务按分工不执行浏览器交互，因此没有截图，也不把视觉验收标记为通过。主任务需用
同一桌面 viewport，通过 AI 入口生成 `2026-05-25` 至 `2026-05-31` 报告，打开新建
资产，并与最终 skill 的 McKinsey 样例逐项记录：

1. 聊天回答与报告内 scope 文本均为 `2026-05-25` 至 `2026-05-31`。
2. 运行时 iframe `sandbox` 属性恰为 `allow-scripts`，不含任何被禁止 token。
3. McKinsey 样例要求的全部章节存在且顺序一致。
4. Top3 卡片布局、排序、内容与不足三条时的状态。
5. `authorChart`、`trendChart`、`topicChart` 均产生实际 ECharts canvas，而非空容器。
6. `sankeyChart` 产生实际 canvas，节点、连线与标签可读。
7. 缺失视频洞察等缺失数据均显示“无”，不生成虚构内容。
8. 浏览器 console 无脚本、资源、CSP、sandbox、React hydration 或 iframe 错误。

自动化已证明经 HTTP 取回的同一保存 HTML 含本地 ECharts 初始化和四个图表容器，
production build 也已通过；这些证据仍不等价于浏览器图表运行或像素级视觉对照。
在主任务补齐上述证据前，不应宣称浏览器视觉验收完成。
