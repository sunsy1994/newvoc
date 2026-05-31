# ETL Transparency And Script Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ETL flow transparency and script maintenance controls to the existing task management workbench.

**Architecture:** Add service modules for flow metadata and script file management, expose FastAPI endpoints under `/api/etl`, then extend the static task management UI with a flow panel and script editor panel.

**Tech Stack:** Python, FastAPI, pytest, static HTML/CSS/JS.

---

### Task 1: Flow Metadata Service

**Files:**
- Create: `app/services/etl_flow.py`
- Create: `tests/test_etl_flow.py`
- Modify: `app/routers/tasks.py`

- [ ] Write tests for flow nodes and batch summary enrichment.
- [ ] Implement static flow metadata with input/output/rules/function names.
- [ ] Add `GET /api/etl/flow`.
- [ ] Run tests.

### Task 2: Script Manager Service

**Files:**
- Create: `app/services/script_manager.py`
- Create: `tests/test_script_manager.py`
- Modify: `app/config.py`

- [ ] Write tests for reading script metadata.
- [ ] Write tests for saving script content and creating backups.
- [ ] Implement fixed-path script manager.
- [ ] Run tests.

### Task 3: Script API

**Files:**
- Modify: `app/routers/tasks.py`
- Modify: `app/main.py`
- Modify: `tests/test_task_api.py`

- [ ] Add API tests for get script, save script, and test-run with a batch.
- [ ] Implement `GET /api/etl/script`.
- [ ] Implement `PUT /api/etl/script`.
- [ ] Implement `POST /api/etl/script/test-run`.
- [ ] Run tests.

### Task 4: UI Panels

**Files:**
- Modify: `app/static/index.html`
- Modify: `app/static/styles.css`
- Modify: `app/static/app.js`
- Modify: `tests/test_static_ui.py`

- [ ] Add static smoke tests for ETL flow and script maintenance UI.
- [ ] Add flow panel.
- [ ] Add script editor panel.
- [ ] Wire buttons to the new API.
- [ ] Run tests.

### Task 5: Verification

**Files:**
- Modify: `README.md`

- [ ] Document script maintenance.
- [ ] Run `pytest -v`.
- [ ] Restart local server.
- [ ] Commit changes.
