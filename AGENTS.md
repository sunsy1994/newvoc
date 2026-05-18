# Repository Working Rules

## Required Reads Before UI Changes
- Before editing any data asset page or related component, read `design-guides/DATA_ASSET_UI_GUIDELINES.md`.
- Before editing VOC dashboard pages, also read `design-guides/VOC_UI_STYLE.md`.

## Data Asset Scope
- Data asset pages include:
  - `app/src/components/assets/EventLibraryPage.tsx`
  - `app/src/components/assets/ContentLibraryPage.tsx`
  - `app/src/components/assets/CommentLibraryPage.tsx`
  - `app/src/components/assets/KolLibraryPage.tsx`
  - `app/src/components/assets/AuthorLibraryPage.tsx`
  - `app/src/components/assets/CompetitorLibraryPage.tsx`
  - `app/src/components/assets/*RelationViewDialog.tsx`
  - Shared asset UI such as `app/src/components/assets/AssetFilterField.tsx`

## Execution Rule
- Treat the files above as a consistent product surface.
- Reuse existing shared layout and filter patterns before creating new ones.
- If a new asset page is added, align it with `design-guides/DATA_ASSET_UI_GUIDELINES.md`.

## Current Product Architecture
- The project now has a "数据接入" product line in the frontend, with three related modules:
  - `数据接入`
  - `数据导入`
  - `数据计算`
- Frontend is a Vite + React app under `app/`.
- Backend is a Python + FastAPI service under `backend/`.
- Frontend dev requests to `/api` are proxied by `app/vite.config.ts` to `http://127.0.0.1:8000`.

## Core Data Flow
- Target flow is:
  - Excel / text source files
  - import API
  - `dwd_*` / `rel_*` tables
  - pandas calculation tasks
  - `ads_*` service tables or profile outputs
  - frontend query and display
- Import solves "data entry into the system".
- Calculation solves "turn detailed rows into page-ready metrics".
- Do not mix these two concerns when extending the feature set.

## Data Import Rules
- User-facing import templates are Chinese-column `xlsx` files, not CSV.
- Database tables and backend fields remain English.
- Backend import logic must map Chinese headers to English DB columns.
- Current template downloads live under `app/public/data-import-templates/`.
- Current import backend code lives mainly in:
  - `backend/app/api.py`
  - `backend/app/import_service.py`
  - `backend/app/template_registry.py`
  - `backend/app/schemas.py`

## Labeling Boundary
- The user already performs AI or manual labeling offline before import.
- Imported labels are authoritative business input, not system-generated labels.
- This is especially true for comment and account profile fields such as:
  - `观点标签`
  - `意图标签`
  - `情感标签`
  - `用户画像`
  - `用户阶段`
  - `心智标签`
  - `画像标签`
- Do not redesign the system to re-run AI tagging for these fields unless the user explicitly changes the workflow.
- AI capabilities, if added later, should be positioned as optional summary/enhancement features, not the default tagging source.

## Data Calculation Rules
- Data calculation is implemented as Python pandas tasks.
- pandas tasks should read tables, compute aggregate metrics, and write result tables.
- The system should compute metrics such as:
  - counts
  - ratios
  - distributions
  - heat
  - growth
  - risk
  - summary metrics for event / author / KOL / content views
- The system should not treat labeling as part of the default calc pipeline.
- Current calc task backend code lives mainly in:
  - `backend/app/task_registry.py`
  - `backend/app/task_service.py`
  - `backend/app/task_run_store.py`
  - `backend/app/tasks/`

## Current Calculation Tasks
- Existing pandas task examples:
  - `event_asset_overview`
  - `author_event_summary`
  - `content_comment_profile`
  - `kol_event_summary`
- These tasks should consume imported label fields instead of generating labels.
- If a new task is added, keep its responsibility narrow and make its input tables and output tables explicit.

## Database Conventions
- PostgreSQL is the target production-like storage.
- Primary schema design doc is `docs/postgresql/data_access_schema.sql`.
- Use English table and field names in DB.
- Current conventions already confirmed with the user:
  - one content row may belong to multiple events
  - author and comment author are in one unified account pool
  - `ads_*` tables are current-state outputs, not daily snapshot history
  - `risk_summary` is not a required persisted DB field

## Frontend Integration Notes
- Data access frontend pages are primarily under `app/src/components/data-access/`.
- Key files to inspect first before extending this area:
  - `app/src/App.tsx`
  - `app/src/components/Sidebar.tsx`
  - `app/src/components/data-access/DataAccessPage.tsx`
  - `app/src/components/data-access/DataImportPage.tsx`
  - `app/src/components/data-access/DataCalcPage.tsx`
  - `app/src/lib/data-access-api.ts`
  - `app/src/lib/data-calc-api.ts`
- Frontend API adapters normalize backend `snake_case` responses into frontend `camelCase` models.

## Backend Integration Notes
- FastAPI entrypoint is `backend/app/main.py`.
- API routing currently lives in `backend/app/api.py`.
- Import task states and calc run states may be stored locally in JSON files under `backend/storage/` when PostgreSQL is unavailable.
- Do not assume PostgreSQL is always installed on the current machine during development.
- When DB is available, pandas tasks should use database reads and writes as the source of truth.

## Current API Surface
- Data import related endpoints:
  - `GET /api/data-access/overview`
  - `GET /api/data-import/templates`
  - `GET /api/data-import/jobs`
  - `GET /api/data-import/templates/{template_id}/download`
  - `POST /api/data-import/jobs`
- Data calc related endpoints:
  - `GET /api/data-calc/graph`
  - `GET /api/data-calc/tasks`
  - `GET /api/data-calc/tasks/{task_id}`
  - `POST /api/data-calc/tasks/{task_id}/run`

## Implementation Guardrails
- Prefer extending the current data access architecture rather than creating a parallel import or calc system.
- Keep import templates, backend schema mapping, and frontend copy in sync.
- When changing import columns, update all three together:
  - template file
  - backend header mapping
  - schema / ingestion logic
- When changing calc outputs, update all three together:
  - pandas task
  - output schema or service table expectations
  - frontend page or API model
- Do not revert unrelated local changes in the repo. The worktree may already contain user-owned edits.

## Useful Reference Files
- Data asset bottom-table draft:
  - `docs/DATA_ASSET_SCHEMA_DRAFT_V1.md`
- Data import API contract:
  - `docs/DATA_IMPORT_API_CONTRACT.md`
- PostgreSQL schema:
  - `docs/postgresql/data_access_schema.sql`
- Backend startup notes:
  - `backend/README.md`
