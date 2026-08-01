# 产品报告叙事摘要验证记录

验证日期：2026-08-01

工作区：`D:\voc\story1`

分支：`codex/product-report-visual-polish-v2`

相关实现提交：`0980528`、`5fdd0a4`、`9ad4d80`、`7c38e6c`、`76639cf`、`9aad827`、`d6b26cd`。

验证时 HEAD：`d6b26cd fix: stabilize report summary mode switcher`。

## 完整回归

| 检查 | 工作目录 | 精确命令 | 结果 |
| --- | --- | --- | --- |
| 后端及集成全量测试 | `D:\voc\story1` | `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider` | exit 0；568 passed，60 warnings，32.90s |
| 前端类型检查 | `D:\voc\story1\frontend` | `npm run typecheck` | exit 0；`tsc --noEmit` 无错误 |
| 前端生产构建 | `D:\voc\story1\frontend` | `npm run build` | exit 0；Next.js 14.2.35 显示 `Compiled successfully`，完成类型校验，并生成静态页面 30/30 |

全量 pytest 的 60 条 warning 均为现有第三方依赖弃用/兼容性提示，包含 Pydantic、LangGraph、Starlette 与 HTTPX；没有失败测试。

## 行为与兼容性证据

为明确覆盖未改动的市场、销售路径及历史产品兼容性，额外执行：

```powershell
$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_market_report_agent.py tests/test_sales_report_agent.py tests/test_next_frontend_architecture.py::test_report_card_accepts_current_product_contract_and_real_ssr_renders_l6_p2
```

结果：exit 0；29 passed，9 warnings，7.21s。

- 市场行为已由完整 `tests/test_market_report_agent.py` 覆盖，包括业务上下文、报告生成、API 读取与缓存路径。
- 销售行为已由完整 `tests/test_sales_report_agent.py` 覆盖，包括销售线索上下文、报告生成、API 读取与缓存路径。
- 历史产品 fallback 已由 `test_report_card_accepts_current_product_contract_and_real_ssr_renders_l6_p2` 的真实 SSR 探针覆盖：断言历史产品 payload 的 `kind` 仍为 `department`，且其 `reportNarrative` 不含合成的 `storyline`；当前有效产品契约才启用叙事摘要。

## 仓库边界

执行命令：

```powershell
git diff --check
git status --short
```

结果：`git diff --check` exit 0，没有空白错误。审计文档创建前的状态仅列出既有无关未跟踪项：`.agents/`、`.superpowers/`、两个 Excel 文件、既有 audit 目录、`lieflat-chart/`、sample 输入/输出目录及两个中文 `.txt` 文件；这些文件均未修改或暂存。

提交前将只暂存本文件，并重新执行缓存区空白检查与状态检查。
