# Soft SaaS Market Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade AutoVOC's global shell and market dashboard to a restrained Soft SaaS visual system while preserving all existing data and interactions.

**Architecture:** Keep the current Next.js routes, server data fetching, component boundaries, and two-level navigation. Establish the visual system through existing CSS variables and focused class changes, then apply it to the shell, dashboard header, metrics, AI summary, and story-card surfaces without introducing a new component library.

**Tech Stack:** Next.js 14, React 18, TypeScript 5, Tailwind CSS 3, Lucide React, Motion.

## Global Constraints

- Do not change backend APIs, dashboard payload types, data calculations, query parameter behavior, or existing detail interactions.
- Do not add a UI framework or new dependency.
- Modify only the global shell, market dashboard, and directly shared styles/components.
- Preserve the story order and the conclusion-evidence-visual structure.
- Preserve unrelated working-tree changes and exclude them from commits.

---

### Task 1: Soft SaaS tokens and global shell

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/components/layout/AppShell.tsx`
- Modify: `frontend/src/components/sidebar/Sidebar.tsx`
- Modify: `frontend/src/components/sidebar/NavItem.tsx`

**Interfaces:**
- Consumes: existing `--sys-*` CSS variables and `Sidebar` component.
- Produces: the same `AppShell({ children }: AppShellProps)` and navigation props, with updated responsive presentation.

- [ ] **Step 1: Capture the current verification baseline**

Run: `npm run typecheck`

Expected: exit code 0. If it fails before changes, record the existing error and do not attribute it to this task.

- [ ] **Step 2: Define the restrained Soft SaaS shell tokens**

Update only the `--sys-*` declarations in `frontend/src/app/globals.css` so they consistently provide page, card, panel, border, ink, muted, subtle, accent, hover, selected, focus-ring, and shadow values. Use warm neutral surfaces, `#5d9691` as the primary accent, low-opacity shadows, and visible focus contrast.

- [ ] **Step 3: Make the shell responsive without changing navigation behavior**

Keep this component signature unchanged:

```tsx
export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-[100dvh] bg-[var(--sys-page)] p-3 text-[var(--sys-ink)] sm:p-4">
      <div className="mx-auto flex min-h-[calc(100dvh-24px)] max-w-[1920px] overflow-hidden rounded-[24px] border border-[var(--sys-border)] bg-[var(--sys-card)] shadow-[var(--sys-shell-shadow)] sm:min-h-[calc(100dvh-32px)]">
        <Sidebar />
        <main className="min-w-0 flex-1 bg-[var(--sys-page)] p-4 sm:p-6 xl:p-8">{children}</main>
      </div>
    </div>
  );
}
```

Adjust sidebar width, surface hierarchy, brand mark, active navigation, hover, and focus classes only. Keep all href calculation and pathname matching unchanged.

- [ ] **Step 4: Verify the shell task**

Run: `npm run typecheck`

Expected: exit code 0 and no new TypeScript errors.

- [ ] **Step 5: Commit the shell task**

```bash
git add frontend/src/app/globals.css frontend/src/components/layout/AppShell.tsx frontend/src/components/sidebar/Sidebar.tsx frontend/src/components/sidebar/NavItem.tsx
git commit -m "feat: refresh soft SaaS application shell"
```

### Task 2: Market dashboard hierarchy and controls

**Files:**
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Modify: `frontend/src/components/voc/VocDashboardThemeFrame.tsx`
- Modify: `frontend/src/components/voc/VocDashboardHeader.tsx`
- Modify: `frontend/src/components/voc/MetricCard.tsx`
- Modify: `frontend/src/components/voc/MarketAiSummaryCard.tsx`

**Interfaces:**
- Consumes: `MarketDashboardPayload`, `VocEvent`, existing `event_id` query parameter, and existing theme context.
- Produces: unchanged exported component names and props; updated responsive hierarchy and states.

- [ ] **Step 1: Preserve the page data flow while improving the layout hierarchy**

Keep `getEvents`, `getMarketDashboard`, `formatNumber`, `PageProps`, and all component props unchanged. Change layout classes so the page uses a compact 5-column metric row on wide screens, responsive 2-column behavior on medium screens, and a single column on narrow screens. Keep the story modules in their current order.

- [ ] **Step 2: Consolidate the page header and filter states**

Keep this form contract unchanged:

```tsx
<form className="voc-dashboard-filter-form flex w-full flex-wrap items-center gap-2 lg:w-auto lg:justify-end">
  <select name="event_id" defaultValue={selectedEventId}>
    {events.map((item) => (
      <option key={item.event_id} value={item.event_id}>
        {item.event_name}
      </option>
    ))}
  </select>
  <button type="submit">查看</button>
  <ThemeSelect />
</form>
```

Add clear hover, focus-visible, open, and selected styles. Do not add client-side routing or change form submission semantics.

- [ ] **Step 3: Rebalance metrics and the AI summary**

Keep `MetricCardProps`, tone names, values, and hints unchanged. Use consistent card radius, border, shadow, icon container, numeric hierarchy, and minimum height. Keep `MarketAiSummaryCard({ eventId })` behavior unchanged while making it the visual conclusion entry point without decorative high-saturation gradients.

- [ ] **Step 4: Verify the dashboard hierarchy task**

Run: `npm run typecheck`

Expected: exit code 0 and no new TypeScript errors.

- [ ] **Step 5: Commit the dashboard hierarchy task**

```bash
git add frontend/src/app/voc/events/market/page.tsx frontend/src/components/voc/VocDashboardThemeFrame.tsx frontend/src/components/voc/VocDashboardHeader.tsx frontend/src/components/voc/MetricCard.tsx frontend/src/components/voc/MarketAiSummaryCard.tsx
git commit -m "feat: refine market dashboard hierarchy"
```

### Task 3: Story-card consistency and final verification

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify only if their existing classes cannot be covered by shared styles: `frontend/src/components/voc/VolumeRhythmStoryCard.tsx`, `frontend/src/components/voc/SubjectStoryCard.tsx`, `frontend/src/components/voc/PlatformStoryCard.tsx`, `frontend/src/components/voc/RegionalResponseStoryCard.tsx`, `frontend/src/components/voc/TopicSpreadStoryCard.tsx`, `frontend/src/components/voc/CommentQualityStoryCard.tsx`

**Interfaces:**
- Consumes: existing story-card props and shared `voc-*` class names.
- Produces: unchanged component exports and interactions with consistent visual surfaces.

- [ ] **Step 1: Normalize existing story-card surfaces through shared selectors**

In `frontend/src/app/globals.css`, use existing `voc-*` hooks to normalize border color, background, radius, shadow, section spacing, headings, muted copy, chart tracks, tooltips, and interactive row states. Do not change chart data, ranking order, modal state, or click handlers.

- [ ] **Step 2: Apply narrow component edits only where no shared hook exists**

Add a descriptive class such as `voc-story-card` to the outer `<article>` or `<section>` of a story component only when required for the shared selector. Do not restructure component markup or extract a new abstraction.

- [ ] **Step 3: Verify accessibility and responsive guards statically**

Run:

```powershell
rg -n "h-screen|window\.addEventListener\(['\"]scroll|outline-none(?!.*focus)" frontend/src/components/layout frontend/src/components/sidebar frontend/src/components/voc frontend/src/app/voc/events/market
```

Expected: no new `h-screen`, raw scroll listener, or focus-less interactive control in the changed files. Review any pre-existing match manually.

- [ ] **Step 4: Run final build-time verification**

Run: `npm run typecheck`

Expected: exit code 0.

Run: `git diff --check`

Expected: exit code 0 with no whitespace errors.

- [ ] **Step 5: Perform live interaction and visual verification**

At desktop and narrow viewport widths, verify: primary and secondary navigation, event selector submission, theme dropdown, AI summary entry, chart hover states, detail drawers/modals, empty dashboard state, long event names, and absence of horizontal page overflow. Compare the market dashboard before and after at the same viewport and event.

- [ ] **Step 6: Commit the story-card and verification task**

```bash
git add frontend/src/app/globals.css frontend/src/components/voc
git commit -m "feat: unify market dashboard story cards"
```
