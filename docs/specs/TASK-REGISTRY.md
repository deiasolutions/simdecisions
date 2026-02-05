# SimDecisions Task Registry

## Overview
- **Current Phase:** Phase 2 - Metrics & Observability
- **Next Task:** TASK-009 (Event Ledger)
- **Target Completion:** Apr 11, 2026

---

## Phase 1: WIRE-001 âœ… COMPLETE

### TASK-001: Router Wiring
- **Status:** âœ… COMPLETE
- **Description:** Wire decide_route() into task creation in server.py
- **Acceptance:** Tasks route by intent (designâ†’llm, codeâ†’terminal)

### TASK-002: KB Injection
- **Status:** âœ… COMPLETE
- **Description:** Call preview_injection() when creating tasks, inject content
- **Acceptance:** Task files contain actual KB content, not just entity IDs

### TASK-003: WebSocket Functional
- **Status:** âœ… COMPLETE
- **Description:** Replace echo-only WebSocket with real message broadcasting
- **Acceptance:** UI receives real-time task updates via WebSocket

### TASK-004: Gate Enforcement
- **Status:** âœ… COMPLETE
- **Description:** Add allow_flight_commits check to git_commit
- **Acceptance:** All three gates enforced, cannot bypass

### TASK-005: Integration Test
- **Status:** âœ… COMPLETE
- **Description:** End-to-end test proving the wired system works
- **Acceptance:** Create task â†’ route â†’ KB inject â†’ execute â†’ capture response

---

## Phase 2: METRICS-001 â† CURRENT

### TASK-009: Event Ledger v1
- **Status:** PENDING
- **Effort:** 8-10 hours (revised upward per ADR-001 schema width)
- **Description:** Append-only log of all system events — foundation for four-vector entity model, oracle tier economics, sensitivity analysis, and fraud detection
- **Governing Spec:** ADR-001-Event-Ledger-Foundation.md
- **Implementation:**
  - Create `runtime/ledger.py`
  - **14-column SQLite schema (ADR-001 Decision 1):**
    ```sql
    CREATE TABLE events (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
        event_type          TEXT NOT NULL,
        actor               TEXT NOT NULL,
        target              TEXT,
        domain              TEXT,
        signal_type         TEXT CHECK(signal_type IN ('gravity','light','internal')),
        oracle_tier         INTEGER CHECK(oracle_tier BETWEEN 0 AND 4),
        random_seed         INTEGER,
        completion_promise  TEXT,
        verification_method TEXT,
        payload_json        TEXT,
        cost_tokens         INTEGER,
        cost_usd            REAL,
        cost_carbon         REAL
    );
    ```
  - **Indexes:** event_type, actor, domain, timestamp, signal_type, oracle_tier
  - **Universal entity IDs (ADR-001 Decision 2):** `{type}:{id}` format — e.g. `agent:BEE-001`, `human:dave`, `system:gate-check`
  - **Signal type taxonomy (ADR-001 Decision 3):** gravity (blocking), light (informational), internal (autonomous)
  - **Flat domain taxonomy (ADR-001 Decision 4):** coding, design, planning, review, testing, deployment, communication, coordination, documentation, research, git, kb, flight, gate, system
  - **Three-currency cost model (ADR-001 Decision 6):** cost_tokens + cost_usd + cost_carbon on every cost-bearing event. Carbon nullable until methodology exists.
  - **Event types:** task_created, task_routed, task_completed, gate_checked, gate_passed, message_sent, message_broadcast, flight_started, flight_ended, kb_injected, cost_recorded
  - **API endpoints:** POST /api/events (internal), GET /api/events (query with filters)
- **Acceptance:**
  - Every significant action logged with full 14-column schema
  - Events queryable by type, time range, actor, domain, signal_type
  - Append-only (no updates/deletes)
  - Universal entity IDs used for actor/target (not bot_id)
  - Signal types classified per ADR-001 Decision 3 guidelines (best-effort, not mandatory for v1)
  - Three cost columns present on schema; tokens and USD populated on LLM calls
- **References:**
  - ADR-001 Decisions 1-4, 6 (schema, entity IDs, signals, domains, cost model)
  - ADR-001 Decision 5 (entity_profiles schema specified but NOT built in this task)
  - Architecture Session §8 (Event Ledger Schema)
  - Architecture Session §22 (Revised Implementation Priorities)

### TASK-010: Cost Tracking & Aggregation
- **Status:** PENDING
- **Effort:** 4-6 hours
- **Description:** Aggregation queries and API for cost data already captured in event ledger (per ADR-001 Decision 6, cost_tokens/cost_usd/cost_carbon columns ship with TASK-009)
- **Governing Spec:** ADR-001-Event-Ledger-Foundation.md (Decision 6)
- **Implementation:**
  - Token-to-dollar mapping config (hardcoded v1 per ADR-001): Claude Sonnet/Opus/Haiku, GPT-4o rates
  - Aggregation queries: cost_by_task, cost_by_agent, cost_by_flight, cost_by_domain
  - API endpoint: GET /api/costs?group_by=task|agent|flight|domain
  - Cost summary in GET /api/summary (extend existing endpoint)
  - Per-oracle-tier cost breakdown (leverages oracle_tier column from event ledger)
- **Acceptance:**
  - Know token count and estimated $ cost per LLM call
  - Can aggregate costs by agent, task, flight, or domain
  - Token-to-dollar mapping configurable (not hardcoded in queries)
  - Oracle tier cost distribution visible
- **Dependencies:** TASK-009 (event ledger with cost columns must exist first)

### TASK-011: Dashboard v1
- **Status:** PENDING
- **Effort:** 8-10 hours
- **Description:** Real-time metrics display in browser — leverages event ledger's domain, signal_type, and cost columns
- **Implementation:**
  - HTML/JS dashboard (can be simple, not React yet)
  - WebSocket connection for live updates
  - Display: active tasks, recent events, cost summary (three currencies), flight status
  - Domain-level activity breakdown (from event ledger domain field)
  - Signal type distribution (gravity/light/internal ratios — proto-α visibility)
  - Oracle tier cost breakdown
  - Auto-refresh every 5 seconds or on WebSocket push
- **Acceptance:**
  - See current system state at a glance
  - Updates in real-time without manual refresh
  - Shows cost accumulation in tokens and USD
  - Shows activity by domain
- **Dependencies:** TASK-009 (event ledger), TASK-010 (cost aggregation)

### TASK-012: Export Formats
- **Status:** PENDING
- **Effort:** 2-3 hours
- **Description:** Export event ledger and metrics as JSON/CSV
- **Implementation:**
  - GET /api/events/export?format=json|csv
  - GET /api/costs/export?format=json|csv
  - Include date range filters
- **Acceptance:**
  - Can download events as JSON
  - Can download events as CSV (Excel-compatible)
  - Can filter by date range

---

## CANCELLED TASKS

These were created from stale January 5, 2026 BEE3 gap analysis. Work was already done or specs were obsolete.

| Task | Original Description | Cancellation Reason |
|------|---------------------|---------------------|
| TASK-013 | Minder integration | From stale data |
| TASK-014 | Gate enforcement (allow_flight_commits) | Already done in TASK-004 |
| TASK-015 | /api/spec/plan endpoint | Phase 3+ work, not Phase 2 |
| TASK-016 | /api/tasks/run endpoint | Phase 3+ work, not Phase 2 |
| TASK-017 | /api/tasks/verify endpoint | Phase 3+ work, not Phase 2 |
| TASK-018 | PTY auto-cleanup | Low priority, not Phase 2 |

---

## Unknown Status

| Task | Notes |
|------|-------|
| TASK-006 | Not found in records - may not exist |
| TASK-007 | Not found in records - may not exist |
| TASK-008 | Not found in records - may not exist |

---

## Future Phases (Not Yet Tasked)

### Phase 3: Simulation Engine (Apr 12 - May 23)
- DES core (Future Event List, clock)
- Work item schema
- Arrival generation
- Queue types
- Routing rules
- Sim-agent scheduling
- Timeline controls
- Checkpoints
- Branching
- A/B comparison

### Phase 4: Visual Layer (May 24 - Jul 4)
- UI framework
- Component library
- Org designer
- Agent cards
- Queue designer
- Routing rules UI
- Timeline UI
- Live dashboard
- Chat interface
- Artifact viewer

### Phase 5: Package & Ship (Jul 5 - Aug 1)
- Scenario package format
- Export/import
- Validation
- Starter templates
- Documentation
- Landing page
- Beta testing

---

## Update Log

| Date | Change |
|------|--------|
| 2026-02-02 | Created task registry |
| 2026-02-02 | Cancelled TASK-013 through TASK-018 (stale source) |
| 2026-02-02 | Confirmed Phase 1 complete, Phase 2 current |
| 2026-02-04 | Updated TASK-009/010/011 to align with ADR-001 14-column event ledger schema, universal entity IDs, signal taxonomy, three-currency cost model |
