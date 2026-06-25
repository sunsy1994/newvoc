# Comment User AI Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the sales dashboard trigger AI-based comment-user profiling from all comments of a selected user, then write the LLM JSON into the existing comment-user profile tables.

**Architecture:** Add a small backend service that fetches all global comments for a `comment_user_id`, renders `画像提示词.txt` with the concrete comment list, calls an OpenAI-compatible chat completion endpoint with `response_format={"type":"json_object"}`, validates the JSON object, and reuses existing profile summarization/loading logic. Expose one minimal API for the frontend `去画像` action.

**Tech Stack:** FastAPI, psycopg, httpx, pytest, PostgreSQL.

---

### Task 1: Prompt Rendering And AI Client

**Files:**
- Create: `app/services/comment_user_ai_profile.py`
- Test: `tests/test_comment_user_ai_profile.py`

- [ ] **Step 1: Write failing tests for prompt rendering and JSON-mode request payload**

Run: `python -m pytest tests/test_comment_user_ai_profile.py -q`

Expected: FAIL because `app.services.comment_user_ai_profile` does not exist.

- [ ] **Step 2: Implement `render_comment_user_profile_prompt`, `build_openai_chat_payload`, and JSON parsing**

The service will replace the template input section with:

```text
用户ID：<comment_user_id>

评论列表：
1. [comment_id=c1] 第一条评论
2. [comment_id=c2] 第二条评论
```

The OpenAI-compatible payload will include:

```json
{
  "model": "<model>",
  "messages": [{"role": "user", "content": "<rendered prompt>"}],
  "response_format": {"type": "json_object"},
  "temperature": 0
}
```

- [ ] **Step 3: Run tests and keep them green**

Run: `python -m pytest tests/test_comment_user_ai_profile.py -q`

Expected: PASS.

### Task 2: Global Comment Extraction And Profile Persistence

**Files:**
- Modify: `app/services/profile_library.py`
- Create/Modify: `app/services/comment_user_ai_profile.py`
- Test: `tests/test_comment_user_ai_profile.py`

- [ ] **Step 1: Write failing tests for global comment filtering and persistence delegation**

The test will build rows with two users, assert only the matching `comment_user_id` comments are selected, and assert the final run function calls the existing DB profile loader with the AI JSON.

- [ ] **Step 2: Add `load_comment_user_profile_records` to reuse existing insert/upsert logic without requiring Excel**

This function accepts normalized records:

```python
{
    "comment_user_id": "...",
    "profile_batch": "...",
    "prompt_version": "...",
    "llm_result_json": {...},
    "source_file_name": "ai_profile"
}
```

- [ ] **Step 3: Run focused backend tests**

Run: `python -m pytest tests/test_profile_library.py tests/test_comment_user_ai_profile.py -q`

Expected: PASS.

### Task 3: Minimal API Endpoint

**Files:**
- Modify: `app/routers/tasks.py`
- Test: `tests/test_task_api.py`

- [ ] **Step 1: Write failing API test for `POST /api/profiles/comment-users/{comment_user_id}/ai-run`**

The test monkeypatches the runner and verifies request fields are passed through.

- [ ] **Step 2: Add request model and endpoint**

Endpoint request body:

```json
{
  "profile_batch": "20260616_ai_profile",
  "prompt_version": "comment_user_profile_v1",
  "prompt_file": "画像提示词.txt"
}
```

- [ ] **Step 3: Run API tests**

Run: `python -m pytest tests/test_task_api.py::test_comment_user_ai_profile_api_runs_profile -q`

Expected: PASS.

### Task 4: Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused test suite**

Run: `python -m pytest tests/test_profile_library.py tests/test_comment_user_ai_profile.py tests/test_task_api.py -q`

Expected: PASS.

- [ ] **Step 2: Confirm no frontend work is included in this MVP**

The frontend `去画像` button wiring remains a next step after the backend endpoint is verified.
