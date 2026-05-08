# Story1 Event VOC Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize the existing story1 product so event pages reflect the new “event-driven VOC precision marketing asset system” spec.

**Architecture:** Add a small pure data/strategy layer that classifies events, computes marketing vs product-risk metrics, and exposes data-readiness requirements. Existing asset pages consume this layer without broad rewrites.

**Tech Stack:** React 19, TypeScript, Vite, Tailwind CSS, existing static asset data modules.

---

### Task 1: Event VOC Strategy Layer

**Files:**
- Create: `app/src/components/assets/eventVocStrategy.ts`
- Create: `app/src/components/assets/eventVocStrategy.test.mjs`
- Modify: `app/package.json`

- [ ] **Step 1: Write failing tests**

Create `app/src/components/assets/eventVocStrategy.test.mjs` with assertions for:
- `classifyEventScenario("新品上市")` returns `营销事件`
- `classifyEventScenario("质量争议")` returns `产品舆情事件`
- `getEventStoryFocus()` returns different business questions for marketing and product-risk events
- `getDataReadinessChecklist()` exposes P0/P1 data groups

- [ ] **Step 2: Run test and verify it fails**

Run: `cd app && npm run test:asset-strategy`

Expected: FAIL because `eventVocStrategy.ts` does not exist yet.

- [ ] **Step 3: Implement `eventVocStrategy.ts`**

Add exported helpers:
- `classifyEventScenario(eventType: string)`
- `getEventStoryFocus(eventType: string)`
- `getEventMetricSet(eventType: string)`
- `getDataReadinessChecklist()`
- `getEventStrategySummary(eventType: string, modelName: string)`

- [ ] **Step 4: Add test script**

Add package script:

```json
"test:asset-strategy": "node src/components/assets/eventVocStrategy.test.mjs"
```

- [ ] **Step 5: Run tests**

Run: `cd app && npm run test:asset-strategy`

Expected: PASS.

### Task 2: Event Library Story Layer

**Files:**
- Modify: `app/src/components/assets/EventLibraryPage.tsx`
- Modify: `app/src/components/assets/data/eventLibraryData.ts`

- [ ] **Step 1: Add event scenario fields to sample data**

Add fields where useful:
- `targetAudience`
- `businessOwner`
- `storyGoal`

- [ ] **Step 2: Update EventLibraryPage**

Use `getEventStoryFocus()` and `getEventMetricSet()` to display:
- event scenario badge
- core business question
- suggested analysis path
- marketing/risk metric chips
- data-readiness CTA

- [ ] **Step 3: Verify typecheck**

Run: `cd app && npm run build`

Expected: TypeScript build succeeds.

### Task 3: Content and KOL Decision Signals

**Files:**
- Modify: `app/src/components/assets/ContentLibraryPage.tsx`
- Modify: `app/src/components/assets/KolLibraryPage.tsx`

- [ ] **Step 1: Add content decision section**

Surface content as “传播承载层”:
- show `contentRole`
- show value/risk flags
- show comment structure indicators
- show whether the content supports marketing reuse or product-risk evidence

- [ ] **Step 2: Add KOL decision section**

Surface KOL as “投放决策资产”:
- audience mindset/stage/intent Top3
- effective engagement rate
- risk score
- recommended use case

- [ ] **Step 3: Verify UI build**

Run: `cd app && npm run build`

Expected: Vite build succeeds.

### Task 4: Commit

**Files:**
- All modified files from Tasks 1-3

- [ ] **Step 1: Review diff**

Run: `git diff -- app/src/components/assets app/package.json`

- [ ] **Step 2: Run final verification**

Run:
- `cd app && npm run test:asset-strategy`
- `cd app && npm run build`

- [ ] **Step 3: Commit**

Run:

```bash
git add app/package.json app/src/components/assets
git commit -m "feat: optimize event VOC asset workflow"
```
