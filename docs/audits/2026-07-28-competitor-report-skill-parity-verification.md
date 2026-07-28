# 竞品报告 Skill Parity 验证记录

验证日期：2026-07-28  
工作区：`D:\voc\story1\.worktrees\competitor-report-skill-parity`  
范围：Task 4 自动化集成验证；浏览器对照由主任务执行

## 成功标准与自动化证据

| 成功标准 | 自动化证据 | 结果 |
| --- | --- | --- |
| AI 报告请求“生成5月最后一周的竞品动态报告”返回并保存 `2026-05-25` 至 `2026-05-31` | `test_unified_agent_api_returns_and_stores_named_month_last_week_scope` 通过真实 `/api/agents/run`、dispatcher、竞品报告 graph 和确定性 scope resolver，仅替换外部 LLM/数据库/存储边界；同时断言响应范围、保存 payload 范围和 `report_run_id=42` | 通过 |
| 聊天消息链接到新建竞品报告资产 | `test_auto_voc_competitor_report_request_and_asset_action_contract` 精确断言链接为 `/assets/reports?report_type=competitor_report&report_run_id=${encodeURIComponent(...)}`，且响应 `report_asset` 只转换并保存 `report_run_id` | 通过 |
| 竞品报告资产以 `view_kind="html"` 返回完整 McKinsey HTML | `test_report_asset_detail_returns_only_the_required_event_or_html_view` 使用项目本地 `generate_html_from_records` 生成报告，再通过资产查询边界取回；断言 `McKinsey Consulting`、Top3、作者/趋势/主题/Sankey 四个图表容器 | 通过 |
| 事件报告资产保持原结构化视图 | 同一资产详情测试精确断言 event report 的 `view_kind="structured"` 和原 `structured_report` payload；前端架构测试继续断言 `StructuredReportView` | 通过 |
| 竞品 HTML 隔离显示，不影响宿主页面 | `test_report_assets_fetch_typed_detail_and_render_html_in_a_scriptless_iframe` 断言 `srcDoc`、`sandbox=""`，并拒绝 `allow-scripts` 与父页面 `dangerouslySetInnerHTML` | 通过 |

Task 4 新增断言在正确 worktree 的首次执行即全部通过（3 passed）。这是对 Task 1–3
已经实现的行为补充集成覆盖，不是新增生产行为，因此没有合理的生产代码 RED，也没有
为了制造失败而修改生产代码。

## 执行命令与结果

所有命令均从上述 worktree 执行；前端命令的工作目录为 `frontend`。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 新增集成断言 | `python -m pytest tests/test_task_api.py::test_unified_agent_api_returns_and_stores_named_month_last_week_scope tests/test_asset_library.py::test_report_asset_detail_returns_only_the_required_event_or_html_view tests/test_next_frontend_architecture.py::test_auto_voc_competitor_report_request_and_asset_action_contract -q -p no:cacheprovider` | exit 0；3 passed，5 warnings；7.98s |
| Task 4 focused suite | `python -m pytest tests/test_task_api.py tests/test_asset_library.py tests/test_next_frontend_architecture.py -q -p no:cacheprovider` | exit 0；143 passed，46 warnings；21.21s |
| 后端全量回归 | `python -m pytest -q -p no:cacheprovider` | exit 0；546 passed，60 warnings；25.31s |
| 前端类型检查 | `npm run typecheck` | exit 0；`tsc --noEmit` 无错误 |
| 前端 production build | `npm run build` | exit 0；Next.js 14.2.35 编译、lint/type validity 检查通过；静态页面 30/30 |

pytest warnings 均为现有依赖告警：Starlette `python_multipart`、Pydantic V2
deprecated `Field` 参数、Pydantic protected namespace、LangGraph checkpoint pending
deprecation，以及 TestClient 使用 httpx `app` shortcut 的 deprecation。没有测试失败。

## 浏览器对照待验项

本任务按分工不执行浏览器交互，因此没有截图，也不把视觉验收标记为通过。主任务需用
同一桌面 viewport，通过 AI 入口生成 `2026-05-25` 至 `2026-05-31` 报告，打开新建
资产，并与最终 skill 的 McKinsey 样例逐项记录：

1. 聊天回答与报告内 scope 文本均为 `2026-05-25` 至 `2026-05-31`。
2. McKinsey 样例要求的全部章节存在且顺序一致。
3. Top3 卡片布局、排序、内容与缺少不足三条时的状态。
4. 作者贡献、趋势、主题图表实际渲染，无 CDN 依赖导致的空白。
5. Sankey 实际渲染，节点、连线与标签可读。
6. 缺失视频洞察等缺失数据均显示“无”，不生成虚构内容。
7. 浏览器 console 无脚本、资源、React hydration 或 iframe 错误。

自动化已证明 HTML 内含本地 ECharts 初始化和四个图表容器，但这不等价于浏览器像素级
对照或运行时图表验收。在主任务补齐上述证据前，不应宣称浏览器视觉验收完成。
