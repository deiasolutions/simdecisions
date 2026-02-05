# SimDecisions Backlog

## Rules

1. **No new repos.** Ideas go here or don't exist.
2. **No new Claude projects.** This is the project.
3. **Weekly review.** Promote, kill, or leave.
4. **"Is This SimDecisions?" test** before promoting anything.

---

## Design Constraints (Laws, Not Features)

These are non-negotiable architectural decisions:

- [ ] Humans always have real role (approval gates, not just observers)
- [ ] Local-first — cloud is optimization, not requirement
- [ ] File-based protocols — markdown over databases
- [ ] Multi-vendor agents — no lock-in to Claude/OpenAI/etc
- [ ] Observable everything — if it runs, it logs
- [ ] Privacy-first discovery — voluntary, user-controlled

---

## "Is This SimDecisions?" Test

Before promoting from SOMEDAY to NEXT, ask:

1. Does it help design systems of interacting agents?
2. Does it help run those systems?
3. Does it help measure results?
4. Does it serve the bootstrap loop?

If no to all four → KILL or leave in SOMEDAY.

---

## NOW (Current Sprint: WIRE-001) ✅ COMPLETE

| ID | Task | Owner | Status |
|----|------|-------|--------|
| WIRE-001-001 | Wire router into task creation | BOT-001 | ✅ done |
| WIRE-001-002 | Wire KB injection | BOT-002 | ✅ done |
| WIRE-001-003 | WebSocket real messaging | BOT-003 | ✅ done |
| WIRE-001-004 | Gate enforcement | BOT-001 | ✅ done |

**Sprint completed:** 2026-02-01

---

## NEXT (By Phase)

### Phase 2: Metrics (Feb 16-28)
- [ ] Event ledger v1 (append-only log)
- [ ] Cost tracking per task (tokens, time)
- [ ] Basic dashboard (read-only metrics view)
- [ ] Export to CSV/JSON

### Phase 3: Simulation (Mar 1-31)
- [ ] DES engine (discrete event simulation)
- [ ] Statistical work arrivals
- [ ] Queue modeling
- [ ] Timeline controls (pause, step, speed)
- [ ] Scenario branching

### Phase 4: Visual (Apr 1-30)
- [ ] React UI shell
- [ ] Agent designer (drag-drop)
- [ ] Flow designer (connections)
- [ ] Runtime view (live execution)
- [ ] Results dashboard

### Phase 5: Ship (May 1-15)
- [ ] Package for distribution
- [ ] Documentation
- [ ] Beta users
- [ ] v1.0 release

### Post-v1.0
- [ ] BABOK interview bot (requirements elicitation)
- [ ] Conversational design mode ("make me a support team")
- [ ] Scenario packages (pre-built templates)
- [ ] Cloud deployment option
- [ ] Multi-user collaboration

---

## SOMEDAY (Parking Lot)

Ideas not yet evaluated:

- Physical controller integration (PLCs, IoT)
- RAGGIT commerce layer
- Mobile app
- Voice interface
- VR/AR visualization
- Blockchain audit trail
- Multi-tenant SaaS

---

## KILLED (Rejected With Reason)

| Idea | Reason | Date |
|------|--------|------|
| Separate RAQCOON product | It's SimDecisions infrastructure | 2026-02-01 |
| Processing-based UI | Browser-based is more accessible | 2026-02-01 |
| New repo for simulation | One repo policy | 2026-02-01 |

---

## Weekly Review Template

Every Sunday:

1. **NOW complete?** Move to done, pull from NEXT
2. **Blockers?** Escalate or kill
3. **SOMEDAY review:** Promote one, kill one
4. **NEXT still valid?** Reorder if needed
5. **New ideas?** Add to SOMEDAY (not NEXT)
