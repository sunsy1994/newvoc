# AUTO VOC AI Workspace Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing expanded AI modal into a responsive full-screen analysis workspace while preserving API, capability, and local-history behavior.

**Architecture:** Keep `AiCopilotPanel` as the state owner and preserve `ExpandedAiWorkspace` props. Recompose the expanded view into header, empty/conversation canvas, fixed composer, and a lightweight history drawer; update `ChatMessageList` to support document-style assistant responses and user-respecting auto-scroll.

**Tech Stack:** Next.js 14, React 18, TypeScript 5, Tailwind CSS 3, Lucide React.

## Global Constraints

- Do not change the AI endpoint, request body, response type, capability definitions, or `auto-voc-chat-history-v1` storage key.
- Do not add dependencies or a new state-management layer.
- Modify only `AutoVocHomePage.tsx`, `ChatMessageList.tsx`, and directly related styles if required.
- Preserve unrelated working-tree changes.

---

### Task 1: Full-screen workspace and composer behavior

**Files:**
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`

**Interfaces:**
- Consumes: existing `ExpandedAiWorkspace` props, `aiCapabilities`, `ChatMessage[]`, and `submitDataQuestion`.
- Produces: the same component props and submission contract, plus local history-drawer state.

- [ ] **Step 1: Record baseline type safety**

Run: `npm run typecheck`

Expected: exit code 0.

- [ ] **Step 2: Recompose the expanded workspace**

Keep the existing `ExpandedAiWorkspace` signature. Replace its internal layout with a `min-h-[100dvh]` overlay and a `max-w-[1440px]` workspace containing:

- a top bar with `AUTO VOC Copilot`, current capability, history button, and close button;
- a four-card capability area in the empty state;
- a centered Orb, prompt, three recommendation buttons, and composer;
- a compact capability switcher plus message canvas after the first message;
- a bottom composer that remains outside the scrolling message area.

- [ ] **Step 3: Add keyboard-safe composer behavior**

Add this behavior directly to the textarea:

```tsx
onKeyDown={(event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
    event.preventDefault();
    event.currentTarget.form?.requestSubmit();
  }
}}
```

Keep `Shift + Enter` as a newline and keep the existing form submit handler.

- [ ] **Step 4: Add truthful local-history drawer**

Use `messages` only. Display the first user question, total message count, and a clear-history action. Add an `onClearHistory` callback to `ExpandedAiWorkspace`, implemented by `setMessages([])` in `AiCopilotPanel`. Do not present multiple sessions.

- [ ] **Step 5: Add Escape handling with cleanup**

When expanded, register a `keydown` listener that closes the history drawer first, otherwise closes the workspace. Return a cleanup function from the effect.

- [ ] **Step 6: Verify and commit Task 1**

Run: `npm run typecheck`

Expected: exit code 0.

```bash
git add frontend/src/components/home/AutoVocHomePage.tsx
git commit -m "feat: redesign expanded AI workspace"
```

### Task 2: Document-style message stream and final verification

**Files:**
- Modify: `frontend/src/components/home/ChatMessageList.tsx`

**Interfaces:**
- Consumes: unchanged `ChatMessageListProps`.
- Produces: unchanged `ChatMessageList` export with improved presentation and scroll behavior.

- [ ] **Step 1: Respect the reader's scroll position**

Add a container ref and track whether the user is within 120px of the bottom. On new messages or loading changes, scroll only when the view is still near the bottom. Keep reduced-motion users on instant scrolling.

- [ ] **Step 2: Widen assistant responses**

Keep user messages right-aligned and capped near 72% width. Render assistant messages as left-aligned document surfaces up to the full content width, with comfortable `leading-7`, clear AUTO VOC identity, and inline recommendation buttons beneath the answer.

- [ ] **Step 3: Preserve loading and error states**

Keep the existing loading indicator and `isError` styling. Add keyboard-visible focus styling to recommendation buttons.

- [ ] **Step 4: Run final verification**

Run: `npm run typecheck`

Expected: exit code 0.

Run: `git diff --check`

Expected: exit code 0.

Inspect the diff and confirm no API URL, request body, storage key, capability definition, or unrelated file changed.

- [ ] **Step 5: Commit Task 2**

```bash
git add frontend/src/components/home/ChatMessageList.tsx
git commit -m "feat: refine AI conversation stream"
```

### Task 3: Aurora Soft visual atmosphere

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`

**Interfaces:**
- Consumes: existing workspace and capability markup.
- Produces: visual-only Aurora classes; no state or API changes.

- [ ] Add low-opacity cyan, blue, and peach ambient gradients to the empty workspace.
- [ ] Add capability-specific pastel gradients and a restrained selected border.
- [ ] Add focus glow to the composer and subtle colored elevation to prompt cards.
- [ ] Reduce ambient color strength in conversation state and under `prefers-reduced-motion`.
- [ ] Run `npm run typecheck` and `git diff --check`, then commit.
