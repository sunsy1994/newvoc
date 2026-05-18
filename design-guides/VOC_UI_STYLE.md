# VOC UI Style Guide

## Visual Direction
- Primary palette: Blue + Indigo (high saturation, same cool temperature)
- Auxiliary: Cyan/Blue-400 for light accents, Slate/Gray-500 for neutral text
- Avoid warm hues (red/green/orange/yellow) in charts and statuses unless explicitly requested
- Gradients: Blue -> Indigo as primary CTA and highlight gradients
- Card surfaces: soft white with subtle blue tint; use gentle glow for product section

## Chart Color Rules
- 3-series: Blue-600, Indigo-500, Blue-900
- 2-series: Blue-500 vs Indigo-600
- Negative/alert: use Indigo-600/Slate-600 instead of red
- Keep legend dots aligned with series colors

## UI Components
- AI button: Blue-500/Blue-600/Indigo-500 gradient with soft glow and light sweep
- Titles: Blue gradient text on product section; normal sections use gray-900
- Backgrounds: subtle blue-tinted gradient for product theme section
- Status pills: Blue/Indigo backgrounds, avoid green/red

## Typography
- Keep existing project font stack; do not introduce new fonts without approval
- Headings: 600-700 weight, clear spacing
- Body: 400-500 weight, readable sizes

## Code Style
- Use Tailwind utility classes, minimal inline styles
- Keep color tokens consistent across files
- Prefer localized changes; do not introduce global theme unless asked
- Avoid extra dependencies
- Keep component props typed; avoid `any` in new code
- Keep motion/animation durations within 150-350ms unless a looping effect is intended
- Use semantic grouping: `layout -> typography -> color -> effects` ordering in className strings
- Avoid duplicate color literals in the same file; define a small local palette when needed

## Component Conventions
- Card container: `rounded-2xl border border-gray-200/blue-200 bg-white shadow-sm` with blue-tint variants in product section
- Section headers: `text-base font-semibold` and subtitle `text-xs text-gray-500`
- KPI blocks: `rounded-xl border bg-gray-50` (use blue-50 for product)
- Tooltips: `rounded-lg border border-blue-100 bg-white p-3 shadow-lg`
- Tag/Pill: `rounded-full px-2 py-1 text-xs font-medium` with blue/indigo background
- Buttons: `rounded-xl px-4 py-2` with clear hover states; CTA uses blue→indigo gradient
- Charts: consistent axis tick color `#64748b`, grid `#f1f5f9` or blue-tint for product

## Files You Must Check Before Editing
- app/src/components/voc/VocViewPage.tsx
- app/src/components/voc/DepartmentCharts.tsx
- app/src/components/voc/charts/*.tsx
- app/src/components/voc/market/*.tsx
- app/src/components/data/chartsData.ts

## Pre-Edit Checklist
1. Read this file
2. Confirm palette alignment
3. Avoid warm colors unless explicitly requested
4. Keep gradients consistent

