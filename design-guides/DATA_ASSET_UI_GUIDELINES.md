# Data Asset UI Guidelines

## Purpose
- This file defines the visual and layout rules for all data asset pages.
- Use it before editing any asset library page, relation view, filter area, list, or detail drawer.

## Page Family
- Event Library
- Content Library
- Comment Library
- KOL Library
- Author Library
- Competitor Library
- Asset relation dialogs

## Layout Rules
- Use `max-w-7xl` page width and `p-6` outer spacing unless a page has a strong reason not to.
- Keep the default page rhythm as:
  - header / context block
  - filter block
  - summary cards
  - list or table
  - detail drawer or relation dialog
- Primary cards use `rounded-2xl` or `rounded-3xl`, `border border-gray-200`, `bg-white`, `shadow-sm`.
- Do not mix too many radii on the same page. Prefer `rounded-3xl` for page sections and `rounded-2xl` for inner cards.

## Filter Layout
- All filter items must use left label and right control alignment.
- Labels have fixed width and controls fill the remaining space.
- Filters may wrap across rows, but each row must stay visually aligned.
- Use shared filter wrapper component when available. Current default is `AssetFilterField`.
- Search is also treated as a filter item and should align with the same pattern.
- Avoid placing small floating labels above controls on data asset pages unless there is a clear exception.
- Keep filter rows clean and dense. Prefer 2 columns on medium screens and 3 columns on wide screens.

## Alignment Rules
- Left text and right control must align vertically in the same row.
- Summary cards should align baseline for title and number blocks.
- Action buttons inside list rows should stay in one cluster with consistent height.
- In tables and cards, metadata rows should use a stable order and avoid ragged spacing.
- When content wraps, it should wrap by row, not break the label-control pairing.

## Color Rules
- Base surface: white or very light blue-gray.
- Border: `gray-200` family.
- Text:
  - primary: `gray-900`
  - secondary: `gray-500` or `gray-600`
  - tertiary/meta: `gray-400` or `gray-500`
- Primary action and key accent: blue.
- Secondary structural accent: emerald only for positive operational meaning, not as the default brand accent.
- Alert and risk colors can use orange or red only when the meaning is truly warning or risk.
- Do not introduce unrelated palette directions per page. Asset pages should feel like one system.

## Interaction Rules
- Buttons in the same area should share the same height. Default small action height is `h-6` or `h-7`.
- Relation view, detail view, and quick jump actions should sit in the same action cluster.
- Hover states should be subtle. Prefer border, background, or shadow changes over movement-heavy animation.
- Keep animation restrained, typically `150ms` to `300ms`.

## Typography Rules
- Page title: `text-xl font-semibold`.
- Section title: `text-sm font-medium` or `text-base font-semibold`.
- Card labels: `text-xs text-gray-500`.
- KPI values: `text-2xl font-semibold`.
- Avoid decorative or experimental typography in data asset pages.

## Component Conventions
- Filter item:
  - `rounded-2xl border border-gray-200 bg-gray-50/80 px-3 py-2`
  - label width fixed
  - control width fluid
- Summary card:
  - `rounded-2xl border border-gray-200 bg-white p-4 shadow-sm`
- Table/list container:
  - `rounded-3xl border border-gray-200 bg-white shadow-sm`
- Metadata pill:
  - use restrained neutral or semantic colors
  - avoid too many saturated pills in the same row
- Detail drawer:
  - keep sections grouped by information type
  - keep quick actions visually separated in a light tinted panel

## Consistency Rules
- Reuse shared components before creating page-specific variants.
- If one asset page gets a new filter pattern, propagate it to sibling asset pages if the pattern is generic.
- Relation dialogs should follow the same shell:
  - top title and description
  - filter bar
  - main visualization
  - right-side hover detail or quick actions

## Editing Checklist
1. Read this file.
2. Check whether the page already has a shared asset component you should reuse.
3. Preserve left-label-right-control filter alignment.
4. Keep spacing and color rhythm consistent with sibling asset pages.
5. Avoid introducing a one-off layout unless the feature truly needs it.
