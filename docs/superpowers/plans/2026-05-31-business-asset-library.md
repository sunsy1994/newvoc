# Business Asset Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a business-facing asset library for events, contents, comments, and author/KOL assets.

**Architecture:** Add an asset query service backed by PostgreSQL, expose read-only FastAPI endpoints, then extend the static admin UI with a new first-level menu and asset subtabs.

**Tech Stack:** Python, FastAPI, PostgreSQL, psycopg, pytest, static HTML/CSS/JS.

---

### Task 1: Asset Query Service

**Files:**
- Create: `app/services/asset_library.py`
- Create: `tests/test_asset_library.py`

- [ ] Write tests for the business columns of each asset type.
- [ ] Implement SQL query definitions for events, contents, comments, and authors.
- [ ] Implement search, limit, and offset.
- [ ] Run tests.

### Task 2: Asset API

**Files:**
- Modify: `app/routers/tasks.py`
- Modify: `tests/test_task_api.py`

- [ ] Add API tests for `/api/assets/events`, `/contents`, `/comments`, `/authors`.
- [ ] Implement endpoints.
- [ ] Run tests.

### Task 3: Asset Library UI

**Files:**
- Modify: `app/static/index.html`
- Modify: `app/static/styles.css`
- Modify: `app/static/app.js`
- Modify: `tests/test_static_ui.py`

- [ ] Add static tests for first-level asset menu and four subtabs.
- [ ] Add asset library view.
- [ ] Add search and table rendering.
- [ ] Run tests.

### Task 4: Verification

**Files:**
- Modify: `README.md`

- [ ] Document asset library.
- [ ] Run `pytest -v`.
- [ ] Restart local server.
- [ ] Commit changes.
