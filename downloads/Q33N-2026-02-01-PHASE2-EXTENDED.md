# Q33N: Phase 2 Extended Tasks for BEE-001

## Task Queue (TASK-013 through TASK-018)

| Task | What | Hours | Priority |
|------|------|-------|----------|
| TASK-013 | Minder integration (auto-start) | 1-2 | P1 |
| TASK-014 | Gate enforcement (allow_flight_commits) | 0.5-1 | P1 |
| TASK-015 | /api/spec/plan endpoint | 4-6 | P2 |
| TASK-016 | /api/tasks/run endpoint | 3-4 | P2 |
| TASK-017 | /api/tasks/verify endpoint | 2-3 | P2 |
| TASK-018 | PTY auto-cleanup | 1-2 | P2 |

**Total:** ~12-18 hours sequential

---

## Execution Order

After completing TASK-009-012 (METRICS-001), continue with:

1. **TASK-013** — Minder runs automatically with server
2. **TASK-014** — Complete gate enforcement (quick fix)
3. **TASK-015** — Spec plan endpoint (Phase 1 from roadmap)
4. **TASK-016** — Task run endpoint (Phase 2 from roadmap)
5. **TASK-017** — Task verify endpoint (Phase 2 from roadmap)
6. **TASK-018** — PTY cleanup (stability fix)

---

## Working Directory

```
deia_raqcoon/
```

---

## File Destination

```
.deia/hive/tasks/BEE-001/
```

---

## Summary

**TASK-013:** Add lifespan context manager to server.py, auto-start async minder loop

**TASK-014:** Add `allow_flight_commits` check to git_commit (30 min fix)

**TASK-015:** Create spec_parser.py, task_graph.py, /api/spec/plan endpoint

**TASK-016:** Create executor.py, /api/tasks/run endpoint with optional wait

**TASK-017:** Create verifier.py, /api/tasks/verify endpoint (ruff, pytest)

**TASK-018:** Add PTY session TTL, cleanup loop, /api/pty/stats endpoint

---

## Complete Queue

After all tasks (009-018):

| Task | Status | What |
|------|--------|------|
| TASK-009 | PENDING | Event ledger |
| TASK-010 | PENDING | Cost tracking |
| TASK-011 | PENDING | Dashboard |
| TASK-012 | PENDING | Export |
| TASK-013 | PENDING | Minder integration |
| TASK-014 | PENDING | Gate enforcement |
| TASK-015 | PENDING | Spec plan |
| TASK-016 | PENDING | Task run |
| TASK-017 | PENDING | Task verify |
| TASK-018 | PENDING | PTY cleanup |

**Total backlog:** 10 tasks, ~27-39 hours
