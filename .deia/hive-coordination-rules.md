# DEIA Hive Coordination Rules — simdecisions

## Identity

This is **simdecisions** — the spec-first development repository for SimDecisions.

## Coordination

- **Tasks:** `.deia/hive/tasks/BEE-001/` — Tasks assigned to BEE-001
- **Responses:** `.deia/hive/responses/` — Work completed by bees
- **Archive:** `.deia/hive/archive/` — Completed tasks

## Rules

1. **Spec-first development** — No coding without a governing ADR or spec
2. **Sequential execution** — BEE-001 only, one task at a time
3. **Manual gates** — Dave approves all commits
4. **Copy, don't reference** — Code is copied in and refactored, not imported
5. **File-based storage** — SQLite for indexed data, files for specs/tasks/state

## Current Phase

**Phase 2: Metrics & Observability**

Next task: TASK-009 (Event Ledger v1) — COMPLETE, awaiting archive

## Planned Capabilities

**PyBees (MVP target)** — Deterministic Python executable workers
- Spec: `specs/SPEC-PyBee-Python-Executable-Species.md`
- Tasks: TASK-020 through TASK-029
- Status: Spec complete, implementation pending

## Reference

- `specs/TASK-REGISTRY.md` — Task definitions
- `specs/ADR-001-Event-Ledger-Foundation.md` — Event ledger schema
- `specs/ROADMAP-DETAILED.md` — Timeline
