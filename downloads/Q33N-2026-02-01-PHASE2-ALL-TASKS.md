# Q33N: Phase 2 Tasks for BEE-001

## Location
```
C:\Users\davee\Downloads\
```

## Files
```
2026-02-01-PHASE2-ALL-TASKS.zip
```

Contains:
- TASK-009-event-ledger.md
- TASK-010-cost-tracking.md
- TASK-011-dashboard.md
- TASK-012-export.md

## Destination
```
.deia/hive/tasks/BEE-001/
```

## Execution Order (Sequential)

| Order | Task | What | Hours |
|-------|------|------|-------|
| 1 | TASK-009 | Event ledger | 4-6 |
| 2 | TASK-010 | Cost tracking | 3-4 |
| 3 | TASK-011 | Dashboard | 6-8 |
| 4 | TASK-012 | Export | 2-3 |

**Total:** ~15-21 hours

## Summary

**TASK-009:** Create `runtime/ledger.py`, log all events to `.deia/events/YYYY-MM-DD.jsonl`

**TASK-010:** Create `runtime/costing.py`, track tokens and cost per task, update `/api/summary`

**TASK-011:** Create `docs/mockups/metrics-dashboard.html`, real-time WebSocket dashboard

**TASK-012:** Add `/api/events/export` and `/api/tasks/export` for CSV/JSON download

## Working Directory

BEE-001 works in:
```
deia_raqcoon/
```

## Deadline

**Feb 15, 2026**

## Start

BEE-001 begins with TASK-009.
