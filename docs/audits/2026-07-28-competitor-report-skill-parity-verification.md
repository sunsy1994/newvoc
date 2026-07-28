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
| iframe 允许运行本地 ECharts，同时保持 origin 隔离 | 自动化精确校验 `sandbox="allow-scripts"` 且拒绝其他 capability；浏览器以相同 sandbox 加载自包含报告，四个图表均生成 canvas | 通过 |

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

## 浏览器运行与视觉验收

主任务使用与资产查看器相同的 `sandbox="allow-scripts"` iframe 加载一份由项目内
`generate_html_from_records` 生成的 `2026-05-25` 至 `2026-05-31` 自包含报告，
并在 in-app browser 中检查 DOM、canvas、截图和 console：

- iframe sandbox token 恰为 `allow-scripts`；
- `McKinsey Consulting`、核心发现、Top3、账号互动贡献、传播走势、话题分布、
  经销商承接和桑基图章节均存在；
- Top3 实际渲染 3 张卡片；
- `authorChart`、`trendChart`、`topicChart`、`sankeyChart` 均生成 ECharts canvas，
  四个容器均有实际子节点；
- 桑基图节点、连线和标签可见；
- 缺失视频洞察显示“无/暂无”，没有虚构补齐；
- 页面无横向溢出；
- browser console 的 error/warning 记录为 0。

本次手工样例经 PowerShell stdin 传递中文测试品牌和作者时，终端编码把部分样例文字
替换成了 `?`；报告模板中的固定中文、章节和图表均正常。这是一次性验收数据构造方式
造成的显示噪声，不涉及数据库/API 生产路径；生产中文安全性与时间范围由完整 HTTP
闭环测试覆盖。视觉验收确认本地 ECharts 在资产 iframe 的安全边界内能够实际运行。

随后又使用 UTF-8 Python 文件重新生成项目报告，并把最终 Skill 的
`assets/default_long_report_style.html` 作为视觉真源，在同一个 in-app browser、
同一个实际 `1280 × 720` viewport 下逐项对照。两侧结果一致：

- 页面 `max-width` 均为 `1200px`；
- H1 均为 `40px / 700 / rgb(26, 26, 46)`；
- 9 个 H2 章节的名称与顺序完全一致；
- 两侧均为 3 张 Top3 卡片；
- 两侧 `authorChart`、`trendChart`、`topicChart`、`sankeyChart` 均产生 canvas；
- 两侧均无横向溢出；
- 首屏线条、标题、说明、四 KPI 卡片、核心发现色块的尺寸、间距和排版一致。

两份报告的指标数值不同是输入数据不同所致，不属于模板偏差。项目报告额外保留了经过
安全转义的业务摘要、缺失态和入选判断，但没有改变最终 Skill 的章节顺序与 McKinsey
视觉骨架。

## 最终交付复验

最终审查修复 prompt 体积、封面字段、评论关键词与 Top3 血缘口径后重新执行：

- `python -m pytest tests/test_competitor_report_agent.py tests/test_data_lineage.py -q -p no:cacheprovider`
  → `127 passed`；
- `python -m pytest -q -p no:cacheprovider` → `548 passed`，60 个既有依赖告警；
- `npm run typecheck` → exit 0；
- `npm run build` → exit 0，30 个页面；
- `git diff --check` → exit 0。
