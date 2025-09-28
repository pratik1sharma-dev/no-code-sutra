## RFC: LangGraph-native execution, durable checkpoints, and data contracts

- Authors: Platform Team
- Date: 2025-09-01
- Status: Draft
- Related files: `backend/src/services/langgraph_workflows/workflow_executor.py`, `backend/src/main.py`, `backend/src/services/node_dispatcher.py`, `README.md`

### Summary
Adopt LangGraph-native graph construction and routing, introduce durable checkpointing, and formalize node data contracts. This removes bespoke orchestration (manual topological sort and ad-hoc `data_mapping`), improves reliability (resume/retry), and hardens LLM outputs via validation and normalization.

### Motivation
- Reliance on a custom topological executor limits branching, parallelism, and resumability.
- LLM outputs can drift from requested schemas, causing brittle downstream nodes.
- Lack of durable checkpointing complicates retries, idempotency, and long-running workflows.
- Observability is limited without event streaming/tracing.

### Current state (abridged)
- Backend builds a `StateGraph` but executes nodes using a custom topological order; edges are not leveraged for conditions/parallelism.
- In-memory `MemorySaver` is used for checkpoints.
- Data flows via per-edge `data_mapping`; nodes often accept loosely defined inputs.
- Node dispatch is modular via `NodeDispatcher` (good SRP/OCP foundation).

### Goals
- Use LangGraph edges and conditional routing for execution order and branching.
- Introduce durable checkpoints (Redis/Postgres) for resume/retry/idempotency.
- Define explicit node I/O contracts (reads/writes) enforced by Pydantic models.
- Normalize and repair LLM outputs to canonical shapes.
- Stream step events for UI and auditing.
- Preserve the `NodeDispatcher` modularity and existing node library.

### Non-goals
- Large-scale redesign of the frontend editor UX.
- Replacing the existing node set or Instagram feature scope.

### Proposal
1) Graph construction and routing (LangGraph-native)
   - Map nodes with `workflow.add_node(id, executor)`.
   - Use `add_edge(source, target)` for normal flow.
   - Use `add_conditional_edges(node_id, condition_fn, mapping)` for branching (e.g., based on `content_type`, `score`, or presence of fields).
   - Enable parallel branches when dependencies allow (no shared state hazards beyond declared reads/writes).

2) Durable checkpointing
   - Replace `MemorySaver` with a durable checkpointer (`langgraph-checkpoint`): Redis or SQL (Postgres).
   - Persist run state, step results, and metadata for resume/retry and idempotency.

3) Data contracts and schema enforcement
   - Each node type declares:
     - `reads`: list of state keys it consumes.
     - `writes`: list of canonical state keys it produces.
     - `ConfigModel`: Pydantic model for its config.
     - `InputModel`/`OutputModel`: Pydantic models for its I/O (versioned, e.g., `v1`).
   - Producer nodes (LLM-backed) must:
     - Validate LLM output against `OutputModel`.
     - Apply alias maps (e.g., `title→headline`, `points→bullets`) and normalizers.
     - Attempt repair (re-prompt with validation deltas) up to N times before fail-soft.
     - Write both `raw_response` and canonical fields to state.
   - Consumer nodes accept canonical fields and perform minimal normalization.
   - Structural conversions require explicit Transform/Adapter nodes inserted by the generator.

4) Edge mapping (kept minimal)
   - Reserve edge-level `data_mapping` for trivial renames only.
   - Prefer node-level contracts and Transform nodes for non-trivial changes.

5) Event streaming and observability
   - Use LangGraph streaming to emit step start/finish, partial outputs, and errors.
   - Persist a compact step log per execution; surface to UI in real time.

6) Human-in-the-loop via interrupts
   - Introduce an Approval node (caption/image) using `interrupt` semantics.
   - On approval, resume from checkpoint; on reject, return to a repair node or terminate.

7) Scheduler integration
   - Connect the scheduler to launch graphs from saved definitions/inputs.
   - Store run IDs and checkpoint keys in DB; allow reruns and retries.

### Generator contract changes (JSON)
Current minimal shape:
```json
{
  "nodes": [
    {"id": "n1", "type": "aiAgent", "data": {"config": {}}},
    {"id": "n2", "type": "imageGenerator", "data": {"config": {}}}
  ],
  "edges": [
    {"source": "n1", "target": "n2", "data_mapping": {"prompt": "n1.output"}}
  ]
}
```

Proposed backward-compatible extension:
```json
{
  "entry": "n1",
  "nodes": [
    {"id": "n1", "type": "aiAgent", "reads": ["input.prompt"], "writes": ["content", "hashtags"], "version": "v1"},
    {"id": "n2", "type": "imageGenerator", "reads": ["content"], "writes": ["image_url"], "version": "v1"},
    {"id": "n3", "type": "textOverlay", "reads": ["content", "image_url"], "writes": ["composed_image_url"], "version": "v1"},
    {"id": "n4", "type": "instagram_post", "reads": ["composed_image_url", "content"], "writes": ["instagram_post"], "version": "v1"}
  ],
  "edges": [
    {"source": "n1", "target": "n2"},
    {"source": "n2", "target": "n3"},
    {"source": "n3", "target": "n4"}
  ],
  "conditions": [
    {"source": "n1", "guards": [
      {"if": "content_type == 'image'", "target": "n2"},
      {"if": "content_type == 'text_only'", "target": "n5"}
    ]}
  ],
  "data_mapping": {
    "n3": {"overlay_text": "content.headline"}
  }
}
```

Notes:
- `entry` is optional; defaults to the first node for backward compatibility.
- `reads`/`writes` guide validation and can be derived from node registry.
- `conditions` map to `add_conditional_edges` during build.
- `data_mapping` becomes node-scoped and optional for trivial remaps.

### Backend changes
1) Executor
   - Build graphs with `add_edge` and `add_conditional_edges`; remove custom topological sort.
   - Replace `MemorySaver` with Redis/SQL checkpointer; inject run IDs and metadata.
   - Expose streaming endpoint for step events.

2) Node interfaces
   - Introduce Pydantic `ConfigModel`, `InputModel`, `OutputModel` per node type.
   - Implement alias maps and normalizers for LLM nodes; add repair loop.
   - Write canonical outputs plus `raw_response` into state.

3) Registry enhancements
   - Extend `NodeDispatcher` backing registry with contracts and versions.
   - Surface `reads`/`writes` to the frontend via `/api/nodes/registry`.

### Migration plan
- Phase 0 (Scaffold): Add contracts to Instagram flow nodes; keep current executor path.
- Phase 1 (Executor swap): Use LangGraph edges/conditions; keep `data_mapping` compatibility.
- Phase 2 (Durable checkpoints): Switch to Redis/SQL; add retry policies.
- Phase 3 (Streaming + UI): Emit step events and display live execution.
- Phase 4 (Human approval): Add Approval node with `interrupt` and resume.
- Phase 5 (Scheduler): Kick off saved graphs on schedules; persist run lineage.

### Risks & mitigations
- Schema drift from LLMs → Validation + alias maps + repair loop; fail-soft defaults.
- Breaking existing workflows → Backward-compatible schema; adapters and dual-path executor during Phase 1.
- Operational complexity (Redis/DB) → Provision managed Redis/DB; feature flag checkpoints.

### Success metrics
- ≥95% successful executions sustained; reduced schema-related failures.
- Mean time to recovery on transient errors reduced by ≥50% via retries/resume.
- Live step logs visible for ≥99% of runs.
- Time to first post unchanged (≤20s) or improved through parallelism where safe.

### Open questions
- Which checkpoint backend to standardize on first (Redis vs Postgres)?
- Minimum contract set for non-Instagram nodes in MVP phase?
- Versioning policy for node I/O contracts (`v1`, `v1.1`, etc.).

### Appendix A: Condition function sketch
```python
def route_by_content_type(state: dict) -> str:
    ctype = state.get('content_type') or state.get('content', {}).get('type')
    if ctype == 'image':
        return 'n2'
    if ctype == 'text_only':
        return 'n5'
    return 'default'
```

### Appendix B: Alias map example (aiAgent output)
```json
{
  "aliases": {
    "headline": ["headline", "title"],
    "bullets": ["bullets", "points", "list"],
    "hashtags": ["hashtags", "tags"]
  }
}
```

### Appendix C: Transform node example
```json
{
  "id": "t1",
  "type": "transform.content_to_prompt",
  "reads": ["content"],
  "writes": ["image_prompt"],
  "config": {"template": "{headline} — {bullets_joined}"}
}
```

