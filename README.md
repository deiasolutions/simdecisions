# SimDecisions

**Design any system of interacting agents, run it, measure results.**

---

## What Is This?

SimDecisions is a simulation and execution platform for organizational dynamics. Two modes:

- **Production** — Real AI agents produce real outputs (code, docs, research)
- **Simulation** — Statistical work arrivals for capacity planning, what-if analysis

Think of it as a **wind tunnel for organizations**. Aerospace doesn't fly untested planes. Why do organizations restructure untested?

---

## Current State

| Component | Status |
|-----------|--------|
| Task file loop | ✅ Works |
| Multi-LLM support | ✅ Works |
| Flight tracking | ✅ Works |
| Router | ✅ Wired |
| KB injection | ✅ Wired |
| Gate enforcement | ✅ Complete |
| Event ledger | ⬜ Phase 2 (TASK-009) |
| DES engine | ⬜ Phase 3 |
| Visual UI | ⬜ Phase 4 |

---

## Directory Structure

```
simdecisions/
├── specs/                      # Specifications (source of truth)
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
├── federalist/                 # Governance philosophy (20-paper canon)
│   ├── NO-01-why-llh.md
│   ├── ... (NO-01 through NO-20)
│   ├── INTERLUDE-complete.md
│   └── INTERLUDE-v2-reflection-horizon.md
├── .deia/                      # DEIA hive coordination
│   └── hive/
│       ├── tasks/BEE-001/
│       ├── responses/
│       └── archive/
├── runtime/                    # Implementation (Phase 2+)
├── core/                       # Implementation (Phase 2+)
├── adapters/                   # Implementation (Phase 2+)
├── kb/                         # Implementation (Phase 2+)
├── schemas/                    # Implementation (Phase 2+)
└── tests/                      # Implementation (Phase 2+)
```

---

## Core Architecture

### Four-Vector Entity Model (α,σ,π,ρ)

Any entity — human, AI, team, machine — can be profiled:

| Vector | Measures | Example |
|--------|----------|---------|
| **α (alpha)** | Autonomy per domain | Developer operates independently on code, needs approval for deploys |
| **σ (sigma)** | Strength per domain | High Python skill, low CSS skill |
| **π (pi)** | Preference per domain | Loves backend, avoids meetings |
| **ρ (rho)** | Reliability given context | Success rate varies by task + conditions + teammates |

### BOK Patterns

Four foundational simulation patterns:

1. **BOK-SIM-001: Oort Cloud Partitioning** — Synchronization strategy (gravity/light/internal signals)
2. **BOK-SIM-002: Prophecy Engine** — Predictive simulation with oracle tiers
3. **BOK-SIM-003: Alterverse Tree** — Branching simulations for what-if analysis
4. **BOK-SIM-004: Neural Feedback Circuit** — Self-improving system through prediction validation

### Three-Currency Cost Model

Every action is tracked in three economies:
- **Tokens** — Computational attention
- **Dollars** — Financial cost
- **Carbon** — Environmental impact (methodology pending)

---

## Roadmap

| Phase | Target | Status |
|-------|--------|--------|
| Phase 1: Wire the Machine | Mar 14 | ✅ Complete |
| Phase 2: Metrics & Observability | Apr 11 | ⬜ Current |
| Phase 3: Simulation Engine | May 23 | ⬜ Planned |
| Phase 4: Visual Layer | Jul 4 | ⬜ Planned |
| Phase 5: Package & Ship | Aug 1 | ⬜ Planned |

---

## Getting Started

This repo is **spec-first**. Implementation follows specs, not the other way around.

1. Read `specs/UNIFIED-VISION.md` for product context
2. Read `specs/ROADMAP-DETAILED.md` for timeline
3. Read `specs/TASK-REGISTRY.md` for current work
4. Start with TASK-009 (Event Ledger) per `specs/ADR-001-Event-Ledger-Foundation.md`

---

## Governance

SimDecisions is built on the DEIA Federalist Papers — a 20-paper governance philosophy:

- **#NOKINGS** — Human override always
- **Protocol of Grace** — Pause → listen → reflect → respond → rejoin
- **Ethics as infrastructure** — Encoded in files, not professed
- **LLH (Limited Liability Hive)** — Bounded, observable, replaceable coordination units

See `federalist/` for the full canon.

---

## Repository

| | |
|---|---|
| **URL** | https://github.com/deiasolutions/simdecisions |
| **Visibility** | Public |
| **Branch** | `main` (protected) |
| **Config** | [.github/REPO-CONFIG.md](.github/REPO-CONFIG.md) |

### Contribution Workflow

All changes go through PR with tribunal review (3 Q33N judges). See:
- `specs/BOK-REVIEW-001-GitHub-Tribunal-Pattern.md` — Review process
- `specs/SCALING-001-Growth-Governance.md` — Scaling roadmap

---

## License

TBD — Open source license pending.

---

*"The wind tunnel for organizations."*
