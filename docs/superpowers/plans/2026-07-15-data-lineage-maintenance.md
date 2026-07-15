# Data Lineage Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a system-management data lineage catalog that explains where important metrics, rules, LLM labels and Agent summaries come from and where they are consumed.

**Architecture:** Store design-time lineage as unified PostgreSQL nodes and directed edges. Seed code-owned technical definitions idempotently, expose focused FastAPI list/detail/mutation endpoints, and render a Next.js management page with summary metrics, filters, a lineage table and a three-column detail drawer.

**Tech Stack:** Python 3, FastAPI, Pydantic, psycopg 3, PostgreSQL, pytest, Next.js, React, TypeScript, Tailwind CSS.

## Global Constraints

- First version is business-output-level lineage, not a full database-column catalog.
- Do not change existing metric, rule, dashboard or Agent calculations.
- System node codes, kinds, generation types and implementation references are code-owned and protected.
- System edges cannot be deleted; artificial nodes and edges remain editable.
- Do not add a graph database, runtime Agent-instance tracking, automatic code scanning, approval workflow or complex cycle detection.
- Preserve existing user-maintained business definitions, owners and statuses during seed synchronization.

---

### Task 1: Lineage Schema, Seeds and Read Service

**Files:**
- Create: `app/services/data_lineage.py`
- Create: `tests/test_data_lineage.py`

**Interfaces:**
- Produces: `LINEAGE_NODE_SEEDS`, `LINEAGE_EDGE_SEEDS`, `ensure_lineage_catalog()`, `list_lineage_nodes()`, and `get_lineage_detail()`.
- Consumes: existing `DATABASE_URL`, `normalize_row()` and psycopg connection patterns.

- [ ] **Step 1: Write failing seed and summary tests**

Add tests asserting the catalog contains direct aggregation, derived metric, rule judgement, LLM label, LLM summary and consumer-only seeds; all edge endpoints exist; all lineage codes are unique; and summary counts identify incomplete business definitions.

```python
def test_lineage_seeds_cover_business_generation_types():
    from app.services.data_lineage import LINEAGE_NODE_SEEDS

    assert {item["generation_type"] for item in LINEAGE_NODE_SEEDS} >= {
        "raw_fact",
        "direct_aggregation",
        "derived_metric",
        "rule_judgement",
        "llm_label",
        "llm_summary",
        "consumer_only",
    }


def test_lineage_seed_edges_only_reference_existing_nodes():
    from app.services.data_lineage import LINEAGE_EDGE_SEEDS, LINEAGE_NODE_SEEDS

    codes = {item["lineage_code"] for item in LINEAGE_NODE_SEEDS}
    assert all(edge["upstream_code"] in codes and edge["downstream_code"] in codes for edge in LINEAGE_EDGE_SEEDS)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_data_lineage.py -q -p no:cacheprovider`

Expected: fail because `app.services.data_lineage` does not exist.

- [ ] **Step 3: Implement schema and seeds**

Create `system_lineage_node` and `system_lineage_edge` with uniqueness, foreign keys, enum-like `CHECK` constraints, timestamps and system flags. Seed at least the agreed source facts, metrics, rules, LLM labels, dashboards, Agent Tools and Agent outputs.

Use an upsert that updates code-owned technical fields but deliberately omits these user-owned fields from the conflict update:

```text
business_definition
owner
status
```

- [ ] **Step 4: Implement list and detail reads**

`list_lineage_nodes()` accepts `q`, `node_kind`, `business_domain`, `generation_type`, and `status`; returns `summary` and `nodes`. Each node includes upstream and downstream counts and `uses_llm` derived from generation type.

`get_lineage_detail()` returns:

```python
{
    "node": {...},
    "upstream": [...],
    "downstream": [...],
    "edges": [...],
    "available_nodes": [...],
}
```

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python -m pytest tests/test_data_lineage.py -q -p no:cacheprovider`

Expected: all seed, validation and summary tests pass.

### Task 2: Protected Mutations and FastAPI Endpoints

**Files:**
- Modify: `app/services/data_lineage.py`
- Modify: `app/routers/tasks.py`
- Modify: `tests/test_data_lineage.py`
- Modify: `tests/test_task_api.py`

**Interfaces:**
- Consumes: Task 1 service.
- Produces: `create_lineage_node()`, `update_lineage_node()`, `create_lineage_edge()`, `delete_lineage_edge()` and five `/api/system/data-lineage` routes.

- [ ] **Step 1: Write failing protection tests**

Test pure validation before database writes:

```python
def test_system_node_update_rejects_technical_fields():
    with pytest.raises(ValueError, match="系统节点技术字段"):
        validate_node_update({"is_system": True}, {"generation_type": "llm_summary"})


def test_edge_validation_rejects_self_reference():
    with pytest.raises(ValueError, match="不能依赖自身"):
        validate_edge_payload({"upstream_code": "metric.a", "downstream_code": "metric.a", "relation_type": "depends_on"})
```

Also test duplicate/invalid enum behavior and deletion protection for system edges.

- [ ] **Step 2: Run protection tests and verify RED**

Run: `python -m pytest tests/test_data_lineage.py -q -p no:cacheprovider`

Expected: failures identify missing mutation validation and functions.

- [ ] **Step 3: Implement minimal mutations**

Artificial node creation validates code, name, kind, generation type, domain and status. System-node updates accept only `business_definition`, `owner`, and `status`; artificial nodes accept the full editable set except primary key, `lineage_code`, and `is_system`.

Edge creation validates both endpoints, direct self-reference and uniqueness. Edge deletion first reads `is_system` and rejects protected rows.

- [ ] **Step 4: Write failing API routing tests**

Monkeypatch the service imports in `app.routers.tasks` and assert:

- list filters are forwarded;
- detail returns `404` for a missing code;
- node validation errors return `400`;
- edge create/delete calls the correct service function;
- PostgreSQL errors return `503`.

- [ ] **Step 5: Run API tests and verify RED**

Run: `python -m pytest tests/test_task_api.py -k "data_lineage" -q -p no:cacheprovider`

Expected: fail because routes and request models are absent.

- [ ] **Step 6: Add request models and routes**

Add focused Pydantic request models and these routes without changing existing APIs:

```text
GET    /api/system/data-lineage
GET    /api/system/data-lineage/{lineage_code}
POST   /api/system/data-lineage/nodes
PUT    /api/system/data-lineage/nodes/{lineage_code}
POST   /api/system/data-lineage/edges
DELETE /api/system/data-lineage/edges/{edge_id}
```

- [ ] **Step 7: Run backend tests and verify GREEN**

Run: `python -m pytest tests/test_data_lineage.py tests/test_task_api.py -k "data_lineage" -q -p no:cacheprovider`

Expected: all selected tests pass.

### Task 3: System Management Lineage Interface

**Files:**
- Create: `frontend/src/components/system/DataLineagePage.tsx`
- Create: `frontend/src/app/system/data-lineage/page.tsx`
- Modify: `frontend/src/config/navigation.ts`
- Modify: `frontend/src/types/system.ts`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: Task 2 APIs.
- Produces: typed `LineageNode`, `LineageEdge`, `LineageListPayload`, `LineageDetailPayload` and the `/system/data-lineage` page.

- [ ] **Step 1: Write failing architecture tests**

Require the navigation item, page, typed payloads, list filters, summary cards, lineage table, three-column detail drawer, editable business fields and edge maintenance actions.

```python
assert 'href: "/system/data-lineage"' in navigation
assert "DataLineagePage" in page
assert "生成方式" in component
assert "上游来源" in component
assert "当前对象" in component
assert "下游消费" in component
assert "/system/data-lineage/edges" in component
```

- [ ] **Step 2: Run frontend test and verify RED**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "data_lineage" -q -p no:cacheprovider`

Expected: fail because page and component do not exist.

- [ ] **Step 3: Add types, navigation and page route**

Add `数据血缘维护` under system management using the existing navigation icon set. The page only renders `DataLineagePage`.

- [ ] **Step 4: Build the management UI**

Use existing system theme tokens and a restrained “technical atlas” visual direction:

- six compact summary cards;
- search and four select filters;
- table with type, generation, domain, LLM, upstream/downstream and status;
- right-side detail drawer;
- three-column lineage chain with clickable nodes;
- business definition, owner and status editing;
- add-edge form and artificial-edge deletion;
- clear protected-field labels for system nodes;
- retryable list/detail errors without clearing successful state.

Do not add a graph library or visual canvas.

- [ ] **Step 5: Run frontend tests and typecheck**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "data_lineage or system_management_pages" -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend`.

Expected: selected tests and TypeScript typecheck pass.

### Task 4: Focused Regression Verification

**Files:**
- Verify only; no planned production changes.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: evidence that lineage maintenance works without changing dashboards, assets or Agents.

- [ ] **Step 1: Run focused backend suite**

Run: `python -m pytest tests/test_data_lineage.py tests/test_task_api.py tests/test_agent_dispatcher.py tests/test_event_report_agent.py tests/test_insight_agent.py -q -p no:cacheprovider`

Expected: selected backend tests pass.

- [ ] **Step 2: Run focused frontend suite**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "data_lineage or system_management_pages or insight or report_ai_summary_card" -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend`.

Expected: selected frontend tests and typecheck pass.

- [ ] **Step 3: Verify syntax and diff integrity**

Run: `python -m py_compile app/services/data_lineage.py app/routers/tasks.py`

Run: `git diff --check`

Expected: both commands exit successfully. Review the relevant diff and confirm no existing metric formulas, Agent prompts or report storage behavior changed.
