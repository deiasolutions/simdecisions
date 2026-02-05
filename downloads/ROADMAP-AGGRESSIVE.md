# SimDecisions Roadmap: AGGRESSIVE

## The Goal

**Working product by Feb 15, 2026.**

Not pretty. Not polished. **Working.**

---

## Week 1: Feb 1-8 — WIRE IT

| Day | Task | Hours | Exit |
|-----|------|-------|------|
| **Today (Feb 1)** | Cleanup done | 2 | Clean repo |
| **Sun Feb 2** | Wire router into task creation | 3 | Tasks route by intent |
| **Mon Feb 3** | Wire KB injection | 4 | Tasks include KB content |
| **Tue Feb 4** | WebSocket real messaging | 4 | Real-time updates work |
| **Wed Feb 5** | Gate enforcement complete | 2 | All gates checked |
| **Thu Feb 6** | Integration test | 3 | End-to-end flow works |
| **Fri Feb 7** | Buffer / fix breaks | 4 | Nothing broken |
| **Sat Feb 8** | CLI demo script | 2 | Can demo the loop |

**Week 1 Exit:** Create task → routes → KB injected → agent executes → response captured → WebSocket shows it

---

## Week 2: Feb 9-15 — PROVE IT

| Day | Task | Hours | Exit |
|-----|------|-------|------|
| **Sun Feb 9** | Event ledger v1 | 4 | Append-only log works |
| **Mon Feb 10** | Basic metrics (cost, time) | 3 | Know what things cost |
| **Tue Feb 11** | Flight tracking integration | 2 | Sessions have start/end |
| **Wed Feb 12** | CLI headless mode | 3 | JSON output for scripting |
| **Thu Feb 13** | Multi-agent test (3 agents) | 4 | Parallel agents work |
| **Fri Feb 14** | Bug fixes | 4 | Stable enough to use |
| **Sat Feb 15** | **WORKING PRODUCT** | — | Ship it |

**Week 2 Exit:** You can run a multi-agent scenario, see metrics, have event log, demo to anyone

---

## Feb 15 Deliverable

**What you have:**
- CLI that creates tasks
- Tasks route by intent (code/design/planning)
- KB content injected into tasks
- Multiple agents can execute in parallel
- WebSocket shows real-time progress
- Event ledger captures everything
- Basic metrics (tokens, cost, time)
- Flight sessions with start/end

**What you DON'T have:**
- Visual UI (that's Phase 4)
- DES simulation engine (that's Phase 3)
- Scenario packages (that's Phase 5)
- Anything pretty

**But you have a WORKING PRODUCT.**

---

## After Feb 15

| Phase | Dates | What |
|-------|-------|------|
| **Phase 2: Metrics** | Feb 16-28 | Dashboard, exports, better observability |
| **Phase 3: Simulation** | Mar 1-31 | DES engine, timeline controls, branching |
| **Phase 4: Visual** | Apr 1-30 | React UI, designers, runtime view |
| **Phase 5: Ship** | May 1-15 | Package, docs, beta users |

**v1.0 Launch: May 15** (not August)

---

## Today's Remaining Tasks

1. ✅ Cleanup (in progress with Claude Code)
2. Copy BACKLOG.md to repo
3. Copy UNIFIED-VISION.md to repo (as docs/VISION.md)
4. Update README to declare SimDecisions
5. **Start wiring the router**

---

## The Rules

1. **No new features until the loop works**
2. **No philosophy until the loop works**
3. **No documentation until the loop works**
4. **No visual UI until the loop works**
5. **WIRE. THE. LOOP.**

---

## Daily Check

Ask yourself every day:

> "Does the loop work yet?"

If no → work on the loop.
If yes → next phase.

---

## Success = Feb 15

You run this:
```bash
simdecisions run --scenario demo.yaml
```

And you see:
- Tasks created
- Agents assigned
- Work flowing
- Responses captured
- Metrics reported
- Event log complete

**That's the product. Everything else is polish.**
