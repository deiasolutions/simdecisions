# Q33N Mission: SPEC-FOUNDATION
## SimDecisions — Spec-First Development Phase

**Issued by:** Dave (Human Sovereign)
**Date:** 2026-02-04
**Priority:** CRITICAL — gates all subsequent work
**Assigned to:** Q33N → BEE-001 (sequential execution)

---

## Mission Context

The Feb 4, 2026 architecture session produced a major vision expansion for SimDecisions. Four new BOK patterns, a four-vector entity model (α,σ,π,ρ), oracle tier economics, and competitive landscape analysis significantly broadened the product's scope and ambition.

**The lesson from v1:** Coding against incomplete specs produced a codebase that was 70% done and 0% wired. We will not repeat this. This mission establishes spec-first development in a clean repository before any implementation begins.

---

## Mission Objective

**Create the `simdecisions` repository as a spec-complete foundation, then begin TASK-009 (Event Ledger) as the first implementation task.**

---

## Phase A: Repository Setup

### A.1 Create New Repo

```
Repository: simdecisions
Owner: davee (existing GitHub account)
Visibility: Private (for now)
Branch strategy: main only until v1
```

### A.2 Directory Structure

```
simdecisions/
├── README.md                    # Product overview (from UNIFIED-VISION.md)
├── .deia/
│   └── hive/
│       ├── tasks/
│       │   └── BEE-001/
│       ├── responses/
│       └── archive/
├── specs/
│   ├── ADR-001-Event-Ledger-Foundation.md
│   ├── ROADMAP-DETAILED.md
│   ├── TASK-REGISTRY.md
│   ├── UNIFIED-VISION.md
│   ├── RAGGIT_Specification_v0.2.0.md
│   └── architecture/
│       ├── 2026-02-04-SimDecisions-Architecture-Session.md
│       ├── BOK-PATTERN-oort-cloud-partitioning.md
│       ├── BOK-PATTERN-prophecy-engine.md
│       ├── BOK-PATTERN-alterverse-tree.md
│       └── BOK-PATTERN-autonomy-ratio-neural-feedback.md
├── federalist/
│   ├── NO-01-through-NO-20.md   # All 20 papers
│   ├── INTERLUDE-complete.md
│   ├── INTERLUDE-v2-reflection-horizon.md
│   └── RESPONSE-moltbook.md
├── runtime/                     # Implementation (empty until Phase B)
│   └── .gitkeep
├── core/                        # Implementation (empty until Phase B)
│   └── .gitkeep
├── adapters/                    # Implementation (empty until Phase B)
│   └── .gitkeep
├── kb/                          # Implementation (empty until Phase B)
│   └── .gitkeep
├── schemas/                     # Implementation (empty until Phase B)
│   └── .gitkeep
└── tests/                       # Implementation (empty until Phase B)
    └── .gitkeep
```

### A.3 What Moves In (Copy, Don't Link)

| Source | Destination | Notes |
|--------|-------------|-------|
| All Federalist Papers (NO-01 through NO-20) | `federalist/` | As-is |
| Interludes | `federalist/` | As-is |
| Moltbook Response Paper | `federalist/` | As-is |
| ADR-001 | `specs/` | As-is |
| Architecture Session doc | `specs/architecture/` | As-is |
| ROADMAP-DETAILED.md | `specs/` | Updated version |
| TASK-REGISTRY.md | `specs/` | Updated version (ADR-001 aligned) |
| UNIFIED-VISION.md | `specs/` | As-is |
| RAGGIT Specification | `specs/` | As-is |
| BOK patterns (4 new) | `specs/architecture/` | From Feb 4 session |

### A.4 What Does NOT Move Yet

| Item | Why |
|------|-----|
| `deia_raqcoon/` source code | Stays in old repo until TASK-009+ implementation pulls specific modules |
| BEE analysis reports (BEE1/2/3) | Historical — stay in old repo, referenced but not copied |
| ShiftCenter | Stays in its own repo — umbrella org is post-v1 |
| UI mockups | Stays in old repo until Phase 4 |

---

## Phase B: Spec Completeness Audit

Before coding begins, verify spec coverage. The following specs must exist in `specs/` and be internally consistent:

### B.1 Specs That Exist ✅

| Spec | Status | Location |
|------|--------|----------|
| ADR-001 Event Ledger Schema | ✅ Complete | specs/ADR-001 |
| Architecture Session capture | ✅ Complete | specs/architecture/ |
| Roadmap | ✅ Complete | specs/ROADMAP |
| Task Registry | ✅ Complete | specs/TASK-REGISTRY |
| Unified Vision | ✅ Complete | specs/UNIFIED-VISION |
| 4 BOK Patterns | ✅ Complete | specs/architecture/ |

### B.2 Specs That Need Creation (TASK for BEE-001)

| Spec | Purpose | Priority | Effort |
|------|---------|----------|--------|
| ADR-002: API Endpoint Registry | Canonical list of all endpoints, models, auth | HIGH | 2-3 hrs |
| ADR-003: Entity ID Convention | Universal `{type}:{id}` scheme, migration from bot_id | HIGH | 1-2 hrs |
| ADR-004: Hive Protocol | Task file format, claim/complete/archive lifecycle, Q33N coordination | MEDIUM | 3-4 hrs |
| ADR-005: Oracle Tier Implementation | VOI logic, tier selection, graduation criteria | MEDIUM | 2-3 hrs |
| SPEC-SIM-001: DES Engine Requirements | Core simulation spec — FEL, clock, checkpoints, branching | LOW (Phase 3) | 4-6 hrs |

**Note:** ADR-002 and ADR-003 should be written BEFORE TASK-009 coding begins. ADR-004 and ADR-005 can be written in parallel with TASK-009.

---

## Phase C: Begin Implementation — TASK-009

Once Phase A (repo) and Phase B (critical specs) are complete, BEE-001 begins TASK-009: Event Ledger v1.

### Governing Spec
**ADR-001-Event-Ledger-Foundation.md** — this is the primary instruction set. It contains:
- Full 14-column schema
- Universal entity ID convention
- Signal type taxonomy (gravity/light/internal)
- Flat domain taxonomy
- Three-currency cost model
- Entity profile schema (design only, don't build)
- What's nullable now vs. required later

### Implementation Scope

1. Create `runtime/ledger.py`
   - SQLite table per ADR-001 Decision 1 schema
   - `record_event()` function accepting all 14 fields
   - `query_events()` with filters: event_type, actor, domain, signal_type, time range
   - Append-only (no UPDATE, no DELETE)

2. Wire API endpoints
   - `POST /api/events` — internal event recording (not user-facing)
   - `GET /api/events` — query with filters
   - `GET /api/events/export?format=json|csv` — bulk export

3. Instrument existing code
   - Task creation → `task_created` event (gravity, domain from intent)
   - Task routing → `task_routed` event (internal, coding/design/planning)
   - Task completion → `task_completed` event (gravity)
   - Gate checks → `gate_checked` / `gate_passed` events (gravity)
   - Messages → `message_sent` event (light)
   - Flights → `flight_started` / `flight_ended` events (gravity)

4. Tests
   - Record and query round-trip
   - Filter by each supported dimension
   - Export format validation
   - Append-only enforcement (no mutation)

### Acceptance Criteria

- [ ] 14-column schema created per ADR-001
- [ ] Universal entity IDs used (no bare bot_id in ledger)
- [ ] Signal types classified for all v1 event types
- [ ] Three cost columns present (carbon nullable)
- [ ] Every significant system action produces an event
- [ ] Events queryable by type, actor, domain, signal_type, time range
- [ ] JSON and CSV export functional
- [ ] Append-only enforced — no update/delete operations
- [ ] All tests pass

### Effort Estimate
8-10 hours

---

## Constraints

1. **Sequential execution** — BEE-001 only, one task at a time
2. **Spec-first** — No coding without a governing ADR or spec
3. **ADR-001 is authoritative** — Schema decisions are made, not open for debate
4. **Copy, don't reference** — Code from deia_raqcoon is copied in and refactored, not imported
5. **Manual gates** — Dave approves all commits (allow_q33n_git = false until explicitly set)
6. **File-based storage** — SQLite for indexed data, files for specs/tasks/state

---

## Success Criteria for This Mission

| Milestone | Measure |
|-----------|---------|
| Repo exists and is clean | README, directory structure, all specs in place |
| Spec audit passed | ADR-002 and ADR-003 written |
| TASK-009 complete | Event ledger records and queries all system events |
| Foundation validated | Can trace a task from creation through completion in the ledger |

---

## References

| Document | Purpose |
|----------|---------|
| ADR-001-Event-Ledger-Foundation.md | Schema decisions for TASK-009 |
| 2026-02-04-SimDecisions-Architecture-Session.md | Full architecture context |
| ROADMAP-DETAILED.md | Phase timeline and effort estimates |
| TASK-REGISTRY.md | Task definitions and acceptance criteria |
| UNIFIED-VISION.md | Product positioning and scope |
| Federalist Papers (NO-01 through NO-20) | Governance philosophy |

---

*Issued under human sovereignty. All gates manual. All commits require Dave's approval.*

**— Q33N (Dave) → BEE-001**
