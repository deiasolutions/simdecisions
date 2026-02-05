# SimDecisions Roadmap: February → August 2026

## The Goal

**Ship a working SimDecisions by August 2026.**

One product. End-to-end. Usable by someone other than you.

---

## Current State (as of Feb 2026)

| Component | Status |
|-----------|--------|
| API structure | ✅ Works |
| Task file loop | ✅ Works |
| Flight tracking | ✅ Works |
| Multi-LLM support | ✅ Works |
| CLI bee launch | ✅ Works |
| BOK patterns | ✅ Works (29+) |
| Router | ✅ Wired (Phase 1) |
| KB injection | ✅ Wired (Phase 1) |
| WebSocket | ✅ Functional (Phase 1) |
| Gate enforcement | ✅ Complete (Phase 1) |
| Event ledger | ❌ Missing |
| DES engine | ❌ Missing |
| Visual UI | ❌ Missing |

---

## Resource Reality

- **You:** 20-30 hours/week
- **Claude Code:** Implementation partner
- **Claude.ai:** Strategy, docs, thinking
- **Budget:** ~$50-200/month LLM APIs

**Constraint:** This is a solo project with AI assistance. Scope accordingly.

---

## Phase 0: Consolidation ✅ COMPLETE
**Weeks 1-2 (Feb 1-14)**

### Actions
1. Archive `deia_raqcoon_v1/` and `raqcoon_improv/`
2. Delete cruft (New folder, temp files, dead experiments)
3. Commit clean state to main
4. Update README to declare SimDecisions as the product
5. Create `simdecisions/` folder structure (or rename existing)

### Exit Criteria
- [x] One clear codebase, no competing versions
- [x] README says what this is
- [x] Clean git history from this point forward

### Time: ~4-6 hours

---

## Phase 1: Wire the Machine ✅ COMPLETE
**Weeks 3-6 (Feb 15 - Mar 14)**

### Week 3-4: Critical Wiring
| Task | Effort | Why Critical |
|------|--------|--------------|
| Wire router into task creation | 2-3 hrs | Tasks must route by intent |
| Wire KB injection into tasks | 3-4 hrs | Tasks need actual KB content |
| Make WebSocket functional | 4-6 hrs | Real-time updates for UI |
| Complete gate enforcement | 2 hrs | All gates must be checked |

### Week 5-6: Integration
| Task | Effort | Why Critical |
|------|--------|--------------|
| Event ledger v1 | 6-8 hrs | Append-only log of everything |
| Integrate minder with server | 2 hrs | Auto-start, not manual |
| End-to-end integration test | 4-6 hrs | Prove the machine runs |
| CLI headless mode (JSON output) | 3-4 hrs | Programmatic control |

### Exit Criteria
- [x] Create task → routes correctly → KB injected → executes → response captured
- [x] WebSocket shows real-time task updates
- [x] All gates enforced (cannot bypass)
- [ ] Event ledger captures every action (moved to Phase 2)
- [x] Can run headless (no UI required)

### Time: ~30-40 hours total

### Mission: WIRE-001
- TASK-001: Router wiring ✅
- TASK-002: KB injection ✅
- TASK-003: WebSocket functional ✅
- TASK-004: Gate enforcement ✅
- TASK-005: Integration test ✅

---

## Phase 2: Metrics & Observability ← CURRENT
**Weeks 7-10 (Mar 15 - Apr 11)**

### Week 7-8: Metrics Foundation
| Task | Effort | Description |
|------|--------|-------------|
| Event ledger v1 | 6-8 hrs | Append-only log of all system events |
| Cost tracking (tokens, $) | 4-6 hrs | Per task, per agent, per flight |
| Time tracking | 4-6 hrs | Duration, wait time, cycle time |
| Event ledger query API | 4-6 hrs | Retrieve and filter events |

### Week 9-10: Visibility
| Task | Effort | Description |
|------|--------|-------------|
| Dashboard v1 | 8-10 hrs | Real-time metrics display |
| Flight summaries | 4-6 hrs | Auto-generated recap per flight |
| Export formats | 2-3 hrs | JSON and CSV output |
| Historical analysis queries | 4-6 hrs | Query patterns over time |

### Exit Criteria
- [ ] Know cost per task, per agent, per flight
- [ ] Know time spent at each stage
- [ ] Dashboard shows live system state
- [ ] Can export data for analysis
- [ ] Flights auto-generate summaries

### Time: ~40-50 hours total

### Mission: METRICS-001
| Task | Description | Status | Effort |
|------|-------------|--------|--------|
| TASK-009 | Event ledger v1 | PENDING | 6-8 hrs |
| TASK-010 | Cost tracking per task/agent | PENDING | 4-6 hrs |
| TASK-011 | Dashboard v1 (real-time metrics) | PENDING | 8-10 hrs |
| TASK-012 | Export formats (JSON/CSV) | PENDING | 2-3 hrs |

**Total Phase 2 Effort: 21-27 hours**

---

## Phase 3: Simulation Engine
**Weeks 11-16 (Apr 12 - May 23)**

### Week 11-12: DES Core
| Task | Effort | Description |
|------|--------|-------------|
| Future Event List + clock | 6-8 hrs | Core DES data structure |
| Work item schema | 4-6 hrs | Define work unit structure |
| Arrival generation (Poisson) | 4-6 hrs | Statistical work arrivals |
| Queue types (FIFO, priority) | 4-6 hrs | Multiple queue disciplines |

### Week 13-14: Routing & Scheduling
| Task | Effort | Description |
|------|--------|-------------|
| Routing rules | 6-8 hrs | SLA, skills, escalation logic |
| Sim-agent scheduling | 6-8 hrs | Agent availability, assignment |
| Abandonment modeling | 3-4 hrs | Work item timeout/abandonment |

### Week 15-16: Time Control
| Task | Effort | Description |
|------|--------|-------------|
| Timeline controls | 6-8 hrs | Pause, resume, speed multiplier |
| Checkpoints | 6-8 hrs | Save/restore simulation state |
| Branching | 6-8 hrs | Fork from checkpoint |
| A/B comparison | 4-6 hrs | Compare variant outcomes |

### Exit Criteria
- [ ] Can run statistical simulation with arrivals
- [ ] Can pause, resume, speed up simulation
- [ ] Can save checkpoint and restore
- [ ] Can fork scenario and compare variants
- [ ] DES mode and Production mode share same agent definitions

### Time: ~60-80 hours total

### Mission: GOVERNANCE-001
| Task     | Description                                                                                                                              | Status  | Effort   | Dependencies     |
|----------|------------------------------------------------------------------------------------------------------------------------------------------|---------|----------|------------------|
| TASK-020 | **Change Zone Framework** <br> Implement the `kb/change_governance.yml` config and extend the gate system to be a dynamic function. | PENDING | 10-15 hrs | TASK-009 (Ledger)|


---

## Phase 4: Visual Layer
**Weeks 17-22 (May 24 - Jul 4)**

### Week 17-18: Foundation
| Task | Effort | Description |
|------|--------|-------------|
| UI framework | 6-8 hrs | React + Tailwind setup |
| Component library | 6-8 hrs | Basic reusable components |
| API integration | 4-6 hrs | Connect UI to backend |

### Week 19-20: Designers
| Task | Effort | Description |
|------|--------|-------------|
| Org designer | 8-12 hrs | Drag-drop roles/teams |
| Agent cards | 6-8 hrs | Configure sim-agents visually |
| Queue designer | 6-8 hrs | Design queue topology |
| Routing rules UI | 6-8 hrs | Visual rule builder |

### Week 21-22: Runtime UI
| Task | Effort | Description |
|------|--------|-------------|
| Timeline UI | 8-10 hrs | Playhead, controls |
| Live dashboard | 6-8 hrs | Metrics overlay |
| Chat interface | 6-8 hrs | Watch agent communication |
| Artifact viewer | 4-6 hrs | View generated outputs |

### Exit Criteria
- [ ] Can design org visually (no code)
- [ ] Can configure agents visually
- [ ] Can watch simulation run in real-time
- [ ] Can see metrics updating live
- [ ] Can read agent communication

### Time: ~70-90 hours total

---

## Phase 5: Package & Ship
**Weeks 23-26 (Jul 5 - Aug 1)**

### Week 23-24: Packaging
| Task | Effort | Description |
|------|--------|-------------|
| Scenario package format | 4-6 hrs | .simdecisions file spec |
| Export/import | 4-6 hrs | Save and load scenarios |
| Validation | 3-4 hrs | Package integrity checks |
| Starter templates | 6-8 hrs | 3-5 example scenarios |

### Week 25-26: Ship
| Task | Effort | Description |
|------|--------|-------------|
| Documentation | 8-10 hrs | User guide |
| Landing page | 4-6 hrs | What is this, how to get it |
| Bug fixes | 8-12 hrs | Edge cases, polish |
| Beta testing | Ongoing | 5-10 users run scenarios |

### Exit Criteria
- [ ] Someone else can install and run it
- [ ] Documentation explains how to use it
- [ ] 5+ beta users have completed a scenario
- [ ] Landing page explains what it is
- [ ] Known bugs documented, critical ones fixed

### Time: ~40-50 hours total

---

## What's Explicitly OUT of Scope

| Item | Why Out |
|------|---------|
| ClipEgg transport | Future layer, not needed for MVP |
| RAGGIT commerce | Future layer, not needed for MVP |
| Deuterium intent routing | Philosophy exists, implementation later |
| Cloud deployment | Local-first. Cloud after it works locally |
| Authentication | Single-user for MVP |
| Mobile | Desktop/browser only |
| Multi-tenant | One user, one instance |

**Principle:** Ship the simplest thing that proves the model. Expand later.

---

## Decision Points

### End of Phase 1 (Mar 14) ✅ PASSED
**Question:** Does the wired system actually work?
- If yes → Continue to Phase 2 ✅
- If no → Extend Phase 1, diagnose what's broken

### End of Phase 2 (Apr 11)
**Question:** Does observability work?
- If yes → Continue to Phase 3
- If no → Extend Phase 2, fix metrics gaps

### End of Phase 3 (May 23)
**Question:** Is simulation mode valuable without visual UI?
- If yes → Could ship CLI-only version early
- If no → Must complete Phase 4

### End of Phase 4 (Jul 4)
**Question:** Is this usable by someone other than you?
- If yes → Phase 5 is polish
- If no → Extend Phase 4, fix UX gaps

---

## Risk Factors

| Risk | Mitigation |
|------|------------|
| Scope creep (more philosophy, more layers) | This roadmap is the scope. Anything else waits. |
| Time underestimation | Each phase has buffer. If behind, cut scope, not quality. |
| Technical blockers | File-based architecture is proven. No exotic dependencies. |
| Motivation drift | Weekly milestones. Visible progress. Ship something every 2 weeks. |
| Perfectionism | MVP means minimum. Ship ugly, fix later. |

---

## Success Metrics

| Milestone | Target Date | Measure |
|-----------|-------------|---------|
| Machine wired | Mar 14 | End-to-end task flow works ✅ |
| Observable | Apr 11 | Dashboard shows live metrics |
| Simulation runs | May 23 | Can pause, branch, compare |
| Visually usable | Jul 4 | Non-coder can design scenario |
| Shipped | Aug 1 | 5 beta users completed scenarios |

---

## Total Effort Estimate

| Phase | Hours |
|-------|-------|
| Phase 0 | 4-6 |
| Phase 1 | 30-40 |
| Phase 2 | 40-50 |
| Phase 3 | 60-80 |
| Phase 4 | 70-90 |
| Phase 5 | 40-50 |
| **Total** | **244-316 hours** |

At 25 hrs/week = 10-13 weeks of actual work time
With buffer = 26 weeks (6 months)

---

## The Bigger Picture

This roadmap gets you to **SimDecisions v1.0** — a working product that:
- Simulates organizational work
- Executes with real AI agents
- Measures everything
- Lets you compare scenarios
- Runs locally, under your control

After v1.0, the doors open:
- Cloud deployment (SaaS)
- RAGGIT commerce layer (monetize scenarios)
- ClipEgg transport (distributed data)
- Enterprise features (auth, multi-tenant)
- The full Republic of Minds vision

**But none of that matters if v1.0 doesn't ship.**

Ship first. Expand later.
