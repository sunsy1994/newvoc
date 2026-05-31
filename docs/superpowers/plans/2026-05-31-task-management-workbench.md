# Task Management Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the stage 1 “任务管理” workbench for uploading event VOC source files, running ETL jobs, and viewing job outputs.

**Architecture:** FastAPI serves a small backend API and a static management page. The existing `etl/event_voc_ods_etl.py` remains the ETL engine. Runtime task state is stored under `runtime/tasks/<batch_id>/task.json` with uploaded inputs and generated CSV outputs.

**Tech Stack:** Python, FastAPI, pandas/openpyxl, pytest, PostgreSQL-ready schema direction, static HTML/CSS/JS for the first UI.

---

### Task 1: App Skeleton And Task Store

**Files:**
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/services/__init__.py`
- Create: `app/services/task_store.py`
- Create: `tests/test_task_store.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write failing tests**

Create `tests/test_task_store.py` with tests for creating a batch, saving uploaded filenames, updating status, and listing newest tasks first.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_task_store.py -v`

Expected: fail because `app.services.task_store` does not exist.

- [ ] **Step 3: Implement task store**

Implement JSON-backed metadata under a configurable runtime directory. A task record has `batch_id`, `status`, `created_at`, `updated_at`, `input_files`, `summary`, and `error_message`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_task_store.py -v`

Expected: pass.

### Task 2: ETL Runner Service

**Files:**
- Create: `app/services/etl_runner.py`
- Create: `tests/test_etl_runner.py`

- [ ] **Step 1: Write failing tests**

Create tests that copy sample input into a temporary batch, run ETL, and assert `etl_summary.json` is parsed into task metadata.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_etl_runner.py -v`

Expected: fail because `app.services.etl_runner` does not exist.

- [ ] **Step 3: Implement ETL runner**

Call `run_etl(input_dir, output_dir)` from `etl.event_voc_ods_etl`, update status to `running`, then `success` or `failed`, and preserve error text.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_etl_runner.py -v`

Expected: pass.

### Task 3: FastAPI Task API

**Files:**
- Create: `app/main.py`
- Create: `app/routers/__init__.py`
- Create: `app/routers/tasks.py`
- Create: `tests/test_task_api.py`

- [ ] **Step 1: Write failing API tests**

Test template download, task list, upload endpoint, run endpoint, table list endpoint, and table preview endpoint using FastAPI `TestClient`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_task_api.py -v`

Expected: fail because API files do not exist.

- [ ] **Step 3: Implement API**

Expose:

- `GET /api/tasks`
- `POST /api/tasks/upload`
- `POST /api/tasks/{batch_id}/run`
- `GET /api/tasks/{batch_id}`
- `GET /api/tasks/{batch_id}/tables`
- `GET /api/tasks/{batch_id}/tables/{table_name}`
- `GET /api/templates/{template_name}`

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_task_api.py -v`

Expected: pass.

### Task 4: Task Management UI

**Files:**
- Create: `app/static/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`
- Modify: `app/main.py`

- [ ] **Step 1: Add smoke test**

Add a test asserting `GET /` returns HTML containing `任务管理`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_task_api.py::test_home_page_serves_task_management_ui -v`

Expected: fail because `/` is not implemented.

- [ ] **Step 3: Implement UI**

Build a restrained data-operations dashboard:

- left navigation with `任务管理`
- upload panel for three files
- task list with status badges
- run button
- summary cards
- table selector and preview table

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_task_api.py -v`

Expected: pass.

### Task 5: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: Document run commands**

Add install/start commands:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- [ ] **Step 2: Verify all tests**

Run: `pytest -v`

Expected: all tests pass.

- [ ] **Step 3: Start local server**

Run: `uvicorn app.main:app --host 127.0.0.1 --port 8000`

Expected: app is available at `http://127.0.0.1:8000/`.
