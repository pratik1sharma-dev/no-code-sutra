# Workflow Builder UI Improvements

## Goals
- Make building and editing workflows faster, clearer, and safer
- Reduce configuration friction with smart defaults and validation
- Improve execution visibility and confidence before posting

## Quick Wins (1–2 days)
- Node Palette
  - Search and keyboard quick-add (type to filter, Enter to add at cursor)
  - Categories collapsed by default; remember last expanded state
- Canvas Ergonomics
  - Grid + snap-to-grid; better zoom/pan defaults; fit-to-view button
  - Multi-select, drag-to-select, delete/backspace, duplicate (Cmd/Ctrl+D)
  - Auto-layout (dagre) button for messy graphs
- Inspector Panel
  - Right-side Node Inspector using `react-hook-form` + `zod`
  - Inline validation + help text; sensible defaults per node type

## Edge Data Mapping (High Impact)
- Edge click opens a visual mapper
  - Choose target field and bind to "source node → output key"
  - Show current mappings as chips on the edge; edit via modal
- Presets
  - Common mappings (e.g., `aiAgent.output → textOverlay.overlay_text`)
- Validation
  - Warn when mapping references are broken; highlight affected edges/nodes

## Execution Clarity
- Run Preview
  - Highlight execution order on canvas; grey-out unused paths
- Step-by-step Progress
  - Bottom drawer with per-node logs, results, and timings
- Single-node Test
  - "Test Node" button in inspector to validate configuration quickly
- Visual Previews
  - Side panel to preview overlay image and final Instagram caption/hashtags

## Generated Workflow UX
- AI Banner
  - Collapsible "Generated Workflow" banner with metadata
  - Estimated cost, required integrations, auth flags
- Guided Fixes
  - "Fix missing config" CTA jumps to nodes needing inputs; highlights invalid fields

## Content Quality Hooks (for Instagram)
- Prompt Controls
  - Strict JSON schema: headline (<= 40), bullets (3–5, <= 20), caption (<= 2200, target 150–300), hashtags (5–10)
  - Few-shot examples for high-performing styles (educational, promotional, listicle)
- Validation + Fix Pass
  - Length and policy checks; auto-fix if violated
- Variants + Scoring
  - Generate 2–3 variants; heuristic score; keep top; expose A/B in UI
- Hashtags
  - Curated + trending mix; dedupe; banned list; normalize casing

## Scheduling-ready UX
- Variant Strategy
  - Batch generate upcoming slots; freshen before posting (hashtags/trends)
- Uniqueness Guardrail
  - Similarity check vs last N posts; auto-rewrite if above threshold
- Data Model (UI awareness)
  - Show scheduled runs; display chosen variant and last refreshed time

## Developer Tasks
- Palette + Inspector
  - Implement searchable palette and inspector form schemas per node
  - Add keyboard shortcuts and multi-select
- Data Mapping
  - Visual mapper; read/write `data_mapping` on edges; validation
- Execution Drawer
  - Stream logs/results; highlight node on progress; show previews
- Content Pipeline
  - Validator/fixer; variants/reranker; hashtag service; moderation
- Scheduling Hooks
  - Slot pre-gen/freshen flow integration; uniqueness service

## Success Metrics
- Time to configured workflow: ↓ 30%
- Error rate on first run: ↓ 40%
- User satisfaction (builder): ≥ 4.5/5
- Repeat usage: ≥ 60% create second workflow within 7 days