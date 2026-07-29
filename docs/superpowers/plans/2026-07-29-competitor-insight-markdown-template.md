# Competitor Insight Markdown Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prefill the competitor work insight editor with the fixed Markdown template and parse its three sentiment fields correctly in generated reports.

**Architecture:** Keep the template as a frontend constant because it is an editor draft, not persisted configuration. Extend the existing deterministic Python Markdown parser without changing storage or API contracts.

**Tech Stack:** React, TypeScript, Python, pytest, Next.js.

## Global Constraints

- Existing saved Markdown is never overwritten by the template.
- Empty records receive the template only as an unsaved frontend draft.
- Clearing persisted content restores the unsaved template draft.
- Only the six fixed headings are parsed.
- Existing legacy Markdown remains compatible.

---

### Task 1: Frontend template draft behavior

**Files:**
- Modify: `frontend/src/components/competitors/CompetitorLibraryPage.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces: `competitorInsightMarkdownTemplate: string`.
- Consumes: existing insight GET and DELETE responses.

- [ ] Write failing source-contract tests asserting the six headings, empty-response fallback, clear fallback, and fixed-heading instruction.
- [ ] Run `pytest -q -p no:cacheprovider tests/test_next_frontend_architecture.py -k "competitor_work_insight"` and verify RED.
- [ ] Add the template constant and use `insight.insight_markdown?.trim() ? insight.insight_markdown : competitorInsightMarkdownTemplate`.
- [ ] After successful clear, set the textarea to `competitorInsightMarkdownTemplate`.
- [ ] Add the non-interactive fixed-heading instruction above the textarea.
- [ ] Run the focused test and verify GREEN.

### Task 2: Three-way sentiment parsing

**Files:**
- Modify: `app/agents/competitor_report/skill_generator.py`
- Test: `tests/test_competitor_report_renderer.py`

**Interfaces:**
- Consumes: bullet lines under `## 评论情绪`.
- Produces: `sentiment` with exact `正面`, `中性`, and `负面` keys.

- [ ] Write a failing test using the fixed template format and assert all three sentiment values are rendered separately.
- [ ] Run the focused renderer test and verify RED.
- [ ] Parse `正面：`, `中性：`, and `负面：` with both Chinese and ASCII colons.
- [ ] Preserve unstructured legacy sentiment text as the positive summary when no structured prefixes exist.
- [ ] Run the focused renderer test and verify GREEN.

### Task 3: Regression and commit

**Files:**
- Modify only files listed above if a regression is found.

- [ ] Run `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider`.
- [ ] Run `npm run typecheck` in `frontend`.
- [ ] Run `npm run build` in `frontend`.
- [ ] Run `git diff --check`.
- [ ] Commit with `feat: add competitor insight markdown template`.
