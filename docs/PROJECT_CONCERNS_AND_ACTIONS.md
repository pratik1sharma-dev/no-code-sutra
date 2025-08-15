# Project Concerns, Status, and Action Plan

## 1) Architecture Refactor (SRP/OCP)
- Current status:
  - Modular per-node executors in `backend/src/services/nodes/*`
  - `NodeDispatcher` routes node types → executors
  - `WorkflowExecutor` decoupled from monolith; default node is `ai_agent.execute`
  - `LLMClient` abstraction (Bedrock/OpenAI)
- Next actions:
  - Standardize node I/O with Pydantic models; validate in dispatcher
  - Replace prints with structured logging; add execution/request IDs

## 2) Edge Data Mapping
- Current status:
  - `data_mapping` applied before node execution; reference resolver supports `nodeId.field`
- Next actions:
  - Validation pipeline to detect broken mappings; canvas warnings (FE)

## 3) Persistence Layer
- Current status:
  - SQLAlchemy setup (`db.py`, `models.py`); `DATABASE_URL` (SQLite default)
  - Endpoints: `POST /api/workflows/save`, `POST /api/executions/save`
- Next actions:
  - Add retrieval: list/get workflows, list executions, execution details
  - Versioning tables or columns for workflow history

## 4) Workflow Saving Policy
- Recommended save points:
  - On Generate: optional draft
  - Autosave in builder (throttled) and explicit “Save Draft”
  - On “Save & Run”: persist state + create execution record (version bump)
  - On Publish/Activate: mark version active
- Data to store:
  - id, userId, name, description, nodes, edges, metadata, status, version, createdAt/updatedAt
  - executionId, workflowId, version, status, node_results summary, startedAt/finishedAt

## 5) Instagram Content Quality
- Prompt & schema:
  - Strict JSON schema (headline ≤40, bullets 3–5 ≤20, caption target 150–300, hashtags 5–10)
  - Few-shots by style (educational/promotional/listicle)
- Validation & fixer:
  - Length/policy checks; banned words; emoji/line-break policy
  - Auto-fix pass if invalid
- Variants & scoring:
  - Generate 2–3 variants; heuristic/reranker; keep top; optional A/B
- Hashtags:
  - Curated + trending; dedupe; banned list; normalized casing
- Brand voice:
  - User profile (tone/lexicon/emoji density); CTA library
- Safety/compliance:
  - Moderation filter; competitor/banned term list
- Overlay awareness:
  - Ultra-short overlays; caption complements overlay

## 6) Scheduler Strategy (Uniqueness)
- Hybrid approach:
  - Batch pre-gen (reviewable) for upcoming slots
  - Freshen near post time (hashtags/trends/unique hooks)
- Distinct content per run:
  - “Do-not-repeat” lists; rotate angle/tone/CTA; temperature/top_p; per-slot seeds
  - Similarity guardrail (embeddings/n-gram overlap) → auto-rewrite if too similar
- Data model additions:
  - `scheduled_posts` (slot, variant, seed, constraints, statuses)
  - `recent_posts_index` (embedding/simhash)

## 7) Frontend (Builder) – Summary
- Quick wins: searchable palette; grid/snap; multi-select; auto-layout; inspector with zod
- Edge mapping UI: visual mapper; presets; chips on edge; validation warnings
- Execution clarity: highlight order; logs drawer; per-node test; visual previews
- Generated UX: banner with metadata; guided “fix missing config”

## 8) Testing & CI
- CI: compile backend; lint; run smoke execute of a minimal workflow; type-check
- Unit tests: dispatcher mapping, data_mapping resolver, LLM fallback paths
- E2E: smoke test aiAgent → textOverlay → imageUpload → instagram_post (sim)

## 9) Observability
- Logging: structured logs with request/execution IDs
- Tracing/error: Sentry/OpenTelemetry hooks; basic dashboards for success rate & latency

## 10) Security
- Secrets: env management; secret scanning pre-commit; token rotation docs
- Sanitization: ensure logs never print tokens; scrub PII
- Rate limits/backoff for external APIs

## 11) Rollout Plan (2–3 weeks)
- Week 1: CI + logging + validator/fixer; FE edge mapping UI; autosave
- Week 2: variants/reranker + hashtag service; scheduling pre-gen/freshen hooks; uniqueness guardrail
- Week 3: workflow versioning + retrieval APIs; execution views; polish & docs