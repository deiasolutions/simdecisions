# SimDecisions Task Registry

## Overview
- **Current Phase:** Phase 2 - Metrics & Observability
- **Next Task:** TASK-009 (Event Ledger)
- **Target Completion:** Apr 11, 2026

---

## Phase 1: WIRE-001 ✅ COMPLETE

### TASK-001: Router Wiring
- **Status:** ✅ COMPLETE
- **Description:** Wire decide_route() into task creation in server.py
- **Acceptance:** Tasks route by intent (design→llm, code→terminal)

### TASK-002: KB Injection
- **Status:** ✅ COMPLETE
- **Description:** Call preview_injection() when creating tasks, inject content
- **Acceptance:** Task files contain actual KB content, not just entity IDs

### TASK-003: WebSocket Functional
- **Status:** ✅ COMPLETE
- **Description:** Replace echo-only WebSocket with real message broadcasting
- **Acceptance:** UI receives real-time task updates via WebSocket

### TASK-004: Gate Enforcement
- **Status:** ✅ COMPLETE
- **Description:** Add allow_flight_commits check to git_commit
- **Acceptance:** All three gates enforced, cannot bypass

### TASK-005: Integration Test
- **Status:** ✅ COMPLETE
- **Description:** End-to-end test proving the wired system works
- **Acceptance:** Create task → route → KB inject → execute → capture response

---

## Phase 2: METRICS-001 ← CURRENT

### TASK-009: Event Ledger v1
- **Status:** PENDING
- **Effort:** 6-8 hours
- **Description:** Append-only log of all system events
- **Implementation:**
  - Create `runtime/ledger.py`
  - SQLite table: events(id, timestamp, event_type, actor, payload_json)
  - Event types: task_created, task_routed, task_completed, gate_checked, message_sent, flight_started, flight_ended
  - API endpoint: POST /api/events (internal), GET /api/events (query)
- **Acceptance:**
  - Every significant action logged with timestamp
  - Events queryable by type, time range, actor
  - Append-only (no updates/deletes)

### TASK-010: Cost Tracking
- **Status:** PENDING
- **Effort:** 4-6 hours
- **Description:** Track token usage and estimated cost per task/agent/flight
- **Implementation:**
  - Extend event payload with token_count, estimated_cost_usd
  - Add cost columns to messages table if needed
  - Create aggregation queries: cost_by_task, cost_by_agent, cost_by_flight
  - API endpoint: GET /api/costs?group_by=task|agent|flight
- **Acceptance:**
  - Know token count per API call
  - Know estimated $ cost per task
  - Can aggregate by agent or flight

### TASK-011: Dashboard v1
- **Status:** PENDING
- **Effort:** 8-10 hours
- **Description:** Real-time metrics display in browser
- **Implementation:**
  - HTML/JS dashboard (can be simple, not React yet)
  - WebSocket connection for live updates
  - Display: active tasks, recent events, cost summary, flight status
  - Auto-refresh every 5 seconds or on WebSocket push
- **Acceptance:**
  - See current system state at a glance
  - Updates in real-time without manual refresh
  - Shows cost accumulation

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
