# System AI Prompt Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add system-management pages and APIs for AI provider parameters and prompt templates, then make comment-user AI profiling read those managed settings instead of hardcoded config/txt request parameters.

**Architecture:** Store one active AI config and versioned prompt templates in PostgreSQL under `data_asset`. Backend services expose CRUD-lite APIs and seed defaults from current `app/config.py` plus `画像提示词.txt` when the database is empty. The sales “去画像” flow calls the same AI-run endpoint, which now resolves AI config and prompt content from the managed settings.

**Tech Stack:** FastAPI, PostgreSQL, psycopg, Next.js App Router, TypeScript, Tailwind CSS, pytest.

---

### Task 1: Backend System Settings Tables And Service

**Files:**
- Modify: `schema/data_access_schema.sql`
- Create: `app/services/system_settings.py`
- Modify: `app/routers/tasks.py`
- Test: `tests/test_system_settings.py`
- Test: `tests/test_task_api.py`

- [ ] Add `data_asset.system_ai_config` and `data_asset.system_prompt_template`.
- [ ] Implement service functions for reading/upserting AI config and prompt templates.
- [ ] Add API endpoints under `/api/system/...`.
- [ ] Write tests for API routing, API-key masking, default prompt seeding, and active prompt retrieval.

### Task 2: AI Profile Flow Reads Managed Settings

**Files:**
- Modify: `app/services/comment_user_ai_profile.py`
- Test: `tests/test_comment_user_ai_profile.py`

- [ ] Change `run_comment_user_ai_profile` to resolve `base_url/api_key/model/timeout` from system settings when arguments are not explicitly provided.
- [ ] Change prompt rendering to use active database prompt content by default.
- [ ] Keep file fallback for the first seed only.

### Task 3: Frontend System Management Pages

**Files:**
- Modify: `frontend/src/config/navigation.ts`
- Create: `frontend/src/types/system.ts`
- Create: `frontend/src/components/system/SystemSettingsPage.tsx`
- Create: `frontend/src/app/system/parameters/page.tsx`
- Create: `frontend/src/app/system/prompts/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Add 一级菜单“系统管理”.
- [ ] Add “参数维护” page for AI config.
- [ ] Add “提示词维护” page for prompt templates.
- [ ] Use the established clean SaaS card/table/form style.

### Task 4: Verification

- [ ] Run focused backend tests.
- [ ] Run frontend architecture test.
- [ ] Run `npm run typecheck`.
