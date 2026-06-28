# Data Question Agent Package Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the working data-question Agent into a focused `app/agents/data_question` package without changing API or runtime behavior.

**Architecture:** `graph.py` owns LangGraph orchestration, `state.py` owns shared types and catalogs, `parser.py` owns LLM action parsing and validation, `tools.py` owns deterministic data access, and `prompts.py` owns prompt construction. The package root exposes the single public `run_data_question_agent` entry point.

**Tech Stack:** Python, LangGraph, FastAPI, pytest.

## Global Constraints

- Preserve the current endpoint and response contract.
- Preserve the configured runtime LLM and all tool data definitions.
- Do not keep a compatibility service file after router imports move.
- Existing Agent tests must remain behaviorally equivalent.

### Task 1: Lock the target package boundary

- [ ] Add a failing architecture test that expects all six package files and imports the public runner from `app.agents.data_question`.
- [ ] Run the test and confirm it fails because the package does not exist.

### Task 2: Split responsibilities

- [ ] Create `state.py` with state and catalog definitions.
- [ ] Create `prompts.py` with both prompt builders.
- [ ] Create `tools.py` with deterministic event tools.
- [ ] Create `parser.py` with configured LLM invocation, action parsing, validation, and pending clarification handling.
- [ ] Create `graph.py` with graph nodes, conditional routing, composition, and public runner.
- [ ] Export the runner from package `__init__.py`.

### Task 3: Switch imports and remove the old module

- [ ] Change the FastAPI router and tests to import from `app.agents.data_question`.
- [ ] Delete `app/services/data_question_agent.py`.
- [ ] Run Agent tests and confirm behavior remains unchanged.

### Task 4: Verify integration

- [ ] Run `python -m pytest tests/test_data_question_agent.py -q`.
- [ ] Run focused frontend architecture tests.
- [ ] Run `npm run typecheck`.
- [ ] Restart FastAPI and verify the real configured model answers a data question.
