# SimDecisions Architecture — Feb 4, 2026 Session Capture
## "The Wind Tunnel for Organizations"

**Status:** Active ideation — nothing final, everything captured  
**Authors:** Dave (daaaave-atx) × Claude (Anthropic)  
**Purpose:** Preserve every insight from today's session for broader sharing  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Four BOK Patterns](#2-four-bok-patterns)
3. [Four-Vector Entity Model](#3-four-vector-entity-model)
4. [α as Vector, Not Scalar](#4-α-as-vector-not-scalar)
5. [Oracle Tier Spectrum](#5-oracle-tier-spectrum)
6. [Validation Framework](#6-validation-framework)
7. [Fraud & Anomaly Detection](#7-fraud--anomaly-detection)
8. [Event Ledger Schema](#8-event-ledger-schema)
9. [Applications](#9-applications)
10. [Competitive Positioning](#10-competitive-positioning)
11. [The Burning Library](#11-the-burning-library)
12. [Connection to DEIA Federalist Papers](#12-connection-to-deia-federalist-papers)
13. [Roadmap Connection](#13-roadmap-connection)
14. [Data Ingestion: Observation as Requirements](#14-data-ingestion-observation-as-requirements)
15. [Interface Layer: Beyond Text](#15-interface-layer-beyond-text)
16. [The Organizational Intelligence Thesis](#16-the-organizational-intelligence-thesis)
17. [Policy Experimentation: Tweaking Core Beliefs](#17-policy-experimentation-tweaking-core-beliefs)
18. [LLM Experimentation Lab](#18-llm-experimentation-lab)

---

## 1. Executive Summary

SimDecisions is a simulation and execution platform with one pitch:

> **Design any system of interacting agents, run it, measure results.**

Two modes:
- **Production** — Real AI agents produce real outputs
- **Simulation** — Statistical work arrivals for capacity planning, what-if analysis

The architecture rests on four foundational BOK (Book of Knowledge) patterns and a universal four-vector entity profiling framework. Together they enable organizations to test workforce dynamics, optimize team composition, detect fraud, and validate predictions — all before committing real resources.

Think of it as a **wind tunnel for organizations**. Aerospace doesn't fly untested planes. Why do organizations restructure untested?

---

## 2. Four BOK Patterns

### BOK-SIM-001: Oort Cloud Partitioning

**The problem:** You can't simulate everything at full fidelity. Too expensive, too slow.

**The pattern:** Partition any system into two zones:
- **Core** — Tightly coupled elements. Must simulate at full fidelity.
- **Cloud** — Loosely coupled elements. Can be approximated, sampled, or abstracted.

**Three signal types determine coupling:**

| Signal | Meaning | Example |
|--------|---------|---------|
| **Gravity** | Mandatory, blocking | Manager must approve before work proceeds |
| **Light** | Informational, non-blocking | CC on an email, dashboard update |
| **Internal** | Autonomous, no external dependency | Developer choosing their IDE |

**How to partition:** Count signal ratios. High gravity signal density = core. High internal signal density = cloud. The boundary isn't fixed — it shifts based on what question you're asking.

**Why it matters:** A 1,000-person org doesn't need 1,000 fully simulated agents. Maybe 50 are core to the question you're asking. The other 950 are cloud — approximated by statistical distributions. This makes simulation tractable.

---

### BOK-SIM-002: Prophecy Engine

**The problem:** Every simulation requires predictions. How do you handle uncertainty honestly?

**The pattern:** Five oracle tiers representing information quality:

| Tier | Name | Cost | Example |
|------|------|------|---------|
| 0 | Lookup/Rule | Free | "If weekend, office is closed" |
| 1 | Statistical model | ~$0.001 | "Average processing time is 4.2 hours" |
| 2 | ML classifier | ~$0.01 | "This ticket is 73% likely priority-high" |
| 3 | LLM reasoning | ~$0.10 | "Given these factors, the customer will likely..." |
| 4 | Human judgment | ~$50/hr | "Call the domain expert" |

**Key mechanism: Value of Information (VOI)**

Before escalating to a more expensive oracle, ask: "Would a better answer actually change the outcome?" If the decision is the same whether the probability is 60% or 80%, don't pay for precision you won't use.

**Seeded randomness:** Every random decision uses a reproducible seed. Run the same scenario twice with the same seed → identical results. Change one variable → see exactly what changes. This is the foundation of sensitivity analysis.

---

### BOK-SIM-003: Alterverse Tree

**The problem:** You want to optimize, but you don't know what "better" looks like until you explore alternatives.

**The pattern:** Branch simulations into parallel futures (alterverses). Three optimization levels:

| Level | Question | Example |
|-------|----------|---------|
| **Path** | Same goal, faster? | "Can we deliver in 3 weeks instead of 4?" |
| **Resource** | Same goal, cheaper? | "Can we do it with 2 engineers instead of 3?" |
| **Goal** | Better goal entirely? | "Should we build feature A at all, or pivot to B?" |

**Mechanics:**
- Checkpoint a simulation state
- Fork into multiple branches
- Each branch changes one variable (or a set)
- Compare outcomes
- Prune losing branches, explore promising ones

**The insight:** Traditional optimization tools (Gurobi, OR-Tools) optimize equations. SimDecisions puts intelligent agents at decision nodes. An LLM can evaluate "should we escalate this customer?" in ways a linear program cannot.

---

### BOK-SIM-004: Neural Feedback Circuit

**The problem:** How does the system learn from its own predictions?

**The pattern:** A self-improvement loop:

1. **Predict** — Oracle makes a prediction at some tier
2. **Observe** — Actual outcome is recorded
3. **Score** — Compare prediction to reality
4. **Update** — Adjust oracle skill score
5. **Graduate/Demote** — Promote accurate oracles to handle harder problems; demote inaccurate ones

**Oracle skill scores** track accuracy over time. A Tier 1 statistical model that consistently outperforms expectations might graduate to handle cases previously sent to Tier 2. A Tier 3 LLM that keeps getting it wrong on a specific domain gets demoted.

**Seeded randomness enables controlled experiments:** Run 1,000 ensemble simulations with different seeds. The spread of outcomes IS the uncertainty. Narrow spread = high confidence. Wide spread = sensitive system, needs better oracles or more data.

---

## 3. Four-Vector Entity Model

The core insight: **any entity** — human, AI, animal, machine, team, organization — can be profiled through four measurable vector dimensions.

### α — Autonomy Vectors
**How independently the entity operates, per domain.**

Not a single number. A vector across domains. Computed from event ledger signal ratios:

```
α_domain = internal_signals / total_signals
```

High α = operates independently in that domain. Low α = depends on external input.

### σ — Strength Vectors
**How well the entity performs, per domain.**

Measured from outcomes, not self-report.

| Entity | σ_python | σ_css | σ_sprint | σ_endurance |
|--------|----------|-------|----------|-------------|
| Developer A | 0.9 | 0.2 | — | — |
| Cheetah | — | — | 0.99 | 0.3 |

### π — Preference Vectors
**What the entity wants to do.**

Measured from choices when unconstrained. This is the crucial distinction from strength:

> A developer can be brilliant at CSS (σ_css = 0.9) but hate doing it (π_css = 0.1).

Assign them CSS work and you get technically correct output with declining engagement, rising attrition risk.

### ρ — Reliability Vectors
**Will the entity succeed under THESE specific conditions?**

The most complex vector. It's a function of:
- The entity
- The task
- The conditions
- **The other entities involved**

**Cheetah example:**
- Cheetah vs. juvenile gazelle, open savanna: ρ ≈ 0.5–0.6
- Same cheetah, adult gazelle: ρ ≈ 0.15
- Add hunting partner: ρ rises
- Change terrain to dense brush: ρ drops
- Cheetah is exhausted (just sprinted): ρ drops further

ρ is context-dependent, relational, and temporal. It's the vector that makes SimDecisions a simulation engine, not a spreadsheet.

---

## 4. α as Vector, Not Scalar

**This is one of the session's most important insights.**

A single relationship — between a person and their manager, between a drone and its operator, between a Mars rover and ground control — has MULTIPLE autonomy values across domains.

### Mars Rover Example

| Domain | α | Why |
|--------|---|-----|
| Navigation | 0.9 | Operates independently between waypoints |
| Drilling site selection | 0.1 | Ground control decides |
| Emergency response | 1.0 | Communication delay forces full autonomy |
| Science instrument selection | 0.5 | Shared decision |

### Battlefield Drone Example

| Domain | α | Why |
|--------|---|-----|
| Route planning | 0.95 | Full autonomy |
| Target identification | 0.8 | Mostly autonomous |
| Weapon release | 0.0 | Human required — always |
| Return-to-base | 1.0 | Autonomous |

### Personal Relationship Example

| Domain | α | Why |
|--------|---|-----|
| Finances | 0.0 | Joint decisions required |
| Laundry | 1.0 | Fully independent |
| Cooking | 0.7 | Mostly independent, some coordination |
| Vacation planning | 0.3 | Mostly joint |

### Why This Matters

**Competence is domain-specific.** Autonomy must be too. A single α number (like "this employee has 70% autonomy") is meaningless. It hides the reality that they might have 95% autonomy in code reviews and 5% autonomy in client communication.

**Event ledger implication:** The event ledger MUST include a `domain` field. Without it, you can't compute per-domain α values. With it, α computation becomes automatic from signal data.

---

## 5. Oracle Tier Spectrum

The five tiers represent a cost-intelligence tradeoff:

```
Tier 0: Lookup/Rule ————————— Free, instant, rigid
Tier 1: Statistical model ——— ~$0.001, fast, limited
Tier 2: ML classifier ———————— ~$0.01, good, needs training data
Tier 3: LLM reasoning ————————— ~$0.10, flexible, expensive
Tier 4: Human judgment ————————— ~$50/hr, best for novel situations
```

### Selection Logic

The system uses **Value of Information (VOI)** to decide which tier to invoke:

1. What decision does this oracle support?
2. How sensitive is the outcome to this prediction?
3. Would a more expensive oracle change the decision?

If a $0.001 statistical model says "processing time ≈ 4 hours" and a $0.10 LLM would say "processing time ≈ 4.2 hours" — and the downstream decision is the same either way — use the cheap oracle.

High-stakes, high-sensitivity nodes justify expensive oracles. Low-stakes nodes stay cheap. The Neural Feedback Circuit learns which nodes need which tiers.

---

## 6. Validation Framework

Three interlocking measurements, all derived from the event ledger:

### 6.1 Sensitivity Analysis

**Method:** Perturb seeds, observe outcome spread.

Run the same scenario 1,000 times with different random seeds. The spread of outcomes IS the system's sensitivity. Where the spread is widest = where the system is most fragile = where you need better oracles or lower autonomy.

**Key output:** An **expected outcome envelope** — the range of plausible outcomes given the model's assumptions.

### 6.2 Distribution Fitting

**Method:** Compare model output distributions against known reality.

If your simulation says customer arrivals follow a Poisson distribution with λ=12, but historical data shows λ=8 with overdispersion — your model is wrong.

Statistical tests: Kolmogorov-Smirnov, chi-square, Anderson-Darling.

Detects systematic bias at every scale.

### 6.3 Historical Backtesting

**Method:** Replay history through the model. Compare predictions to actual outcomes.

Feed the model January's inputs. Does it produce January's outputs? Where it diverges = where the model is wrong. The error distribution reveals systematic bias.

Works at every scale: from fruit fly genetics to military logistics.

---

## 7. Fraud & Anomaly Detection

**The insight:** The same sensitivity analysis that validates models also detects fraud.

### How It Works

Sensitivity analysis produces an **expected outcome envelope** — the range of outcomes consistent with the model's understanding of the system.

Actual outcomes **outside** this envelope (4+ sigma) indicate one of two things:
1. The model is wrong (update the model)
2. Something external is manipulating the system (investigate)

### Applications

| Domain | Signal | What It Catches |
|--------|--------|-----------------|
| Financial markets | Returns outside plausible envelope | Insider trading, market manipulation |
| Crypto | Volume spikes inconsistent with fundamentals | Pump-and-dump schemes |
| Corporate reporting | Numbers outside plausible range | Fraudulent financials |
| Social platforms | Coordinated behavior anomalies | Influence campaigns, bot networks |
| Insurance | Claim patterns outside expected distribution | Fraudulent claims |

### The Moltbook Example

The MOLT token surged 1,800% in 24 hours after a single social media follow from a prominent VC. Run this through SimDecisions:

- Model the token's expected price range given fundamentals, volume, and market conditions
- Actual price: 18x outside the envelope
- Conclusion: This is not organic price discovery. Something external is driving it.

**Same engine validates your models AND detects fraud.** One architecture, two capabilities.

---

## 8. Event Ledger Schema

The event ledger is the foundation of everything. Four fields are critical beyond the basics:

```
events(
    id              INTEGER PRIMARY KEY,
    timestamp       TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    actor           TEXT NOT NULL,
    target          TEXT,
    domain          TEXT,           -- ← Enables per-domain α
    signal_type     TEXT,           -- ← gravity/light/internal → α computation
    oracle_tier     INTEGER,        -- ← 0-4, enables cost tracking + graduation
    random_seed     INTEGER,        -- ← Reproducibility, sensitivity, ensemble
    payload_json    TEXT,
    cost_tokens     INTEGER,
    cost_usd        REAL,
    cost_carbon     REAL            -- ← Three-currency model (Federalist No. 12)
)
```

### Why Each Field Matters

| Field | Enables |
|-------|---------|
| `domain` | Per-domain α computation, domain-specific σ/π/ρ |
| `signal_type` | Autonomy ratio calculation (internal / total) |
| `oracle_tier` | Cost tracking, tier graduation, VOI analysis |
| `random_seed` | Reproducibility, sensitivity analysis, ensemble runs |
| `cost_carbon` | Environmental impact tracking, three-currency cost model |

### Entity Profiles as First-Class Objects

```
entity_profiles(
    entity_id       TEXT NOT NULL,
    domain          TEXT NOT NULL,
    vector_type     TEXT NOT NULL,   -- α, σ, π, ρ
    value           REAL,
    measured_at     TEXT NOT NULL,
    confidence      REAL,
    sample_size     INTEGER,
    conditions_json TEXT             -- For ρ: what context was this measured in
)
```

Profiles are **temporal** — they change over time. A developer's σ_python in January vs. June tells a growth story.

---

## 9. Applications

### 9.1 Team Composition

**Problem:** Given a mission with known demands, select the optimal team.

**Method:** The mission has a demand vector across domains:

```
mission_demands = {
    python: 0.9,
    ml_ops: 0.7,
    frontend: 0.5,
    client_communication: 0.8
}
```

Each candidate has σ vectors. Select the team whose combined σ vectors cover the demand vector with maximum coverage and minimum redundancy.

But don't stop at σ. Check π (will they WANT to do it?) and α (can they operate at the required autonomy level?). A candidate with σ_ml_ops = 0.9 but π_ml_ops = 0.1 will burn out.

### 9.2 Assignment Optimization

Uses ALL four vectors simultaneously:

> Assign the task to the person who **CAN** do it (σ high), **WANTS** to do it (π high), can do it **INDEPENDENTLY** at the required level (α matches supervision available), and **WILL SUCCEED** under current conditions (ρ high given context).

This is the complete assignment function. Most tools optimize on one dimension. SimDecisions optimizes on four.

### 9.3 Personality Test Integration

Myers-Briggs, DISC, StrengthsFinder, Big Five — these are all **pre-measured vectors**.

SimDecisions ingests them as initial priors, then updates from actual performance data. Self-report says "I'm great at communication" (σ_communication = 0.9). Event ledger shows meetings you lead have 2x the escalation rate. Data corrects self-report.

### 9.4 Relationship Compatibility

Compatibility is NOT identical profiles. It's **complementary** ones.

A couple where one has σ_finances = 0.9 and the other has σ_home_maintenance = 0.9 covers more combined space than two people who are both good at finances and bad at everything else.

SimDecisions can compute coverage, identify gaps, and suggest where relationships (personal or professional) need reinforcement.

### 9.5 Biological Validation

The cheetah doesn't take a personality test, but it has a measurable four-vector profile:

- **α:** Hunts alone (α_hunting = 1.0 for males; 0.5 for coalition males)
- **σ:** Sprint speed 0.99, endurance 0.3, night hunting ~0.1
- **π:** Prefers open savanna (π_open_terrain = 0.9), avoids dense forest
- **ρ:** Success rate varies dramatically by prey, terrain, fatigue, competition

Same framework describes cheetah, developer, drone, Mars rover, married couple. Only the domain labels change.

Biology provides clean, well-studied validation data. If SimDecisions can replicate known predator-prey dynamics, the engine is validated before applying it to less-studied human organizational dynamics.

---

## 10. Competitive Positioning

| Category | They Do | SimDecisions Does |
|----------|---------|-------------------|
| Process simulators (Arena, Simio) | Model | Model + Execute + Optimize |
| AI frameworks (AutoGen, CrewAI) | Execute | Execute + Measure + Optimize |
| Workflow tools (n8n, Zapier) | Coordinate | Coordinate + Simulate + Optimize |
| Optimization tools (Gurobi, OR-Tools) | Optimize (math only) | Optimize with intelligent agents at decision nodes |
| Org design (Figma, Miro) | Visualize | Visualize + Run + Measure |
| Personality/Assessment tools | Measure traits | Measure + Simulate + Validate against outcomes |

**Gurobi optimizes equations. SimDecisions optimizes organizations.**

The moat: nobody else combines discrete event simulation with live AI agent execution with four-vector entity profiling with seeded reproducibility with oracle tier management. Each piece exists somewhere. The combination is novel.

---

## 11. The Burning Library

> 10,000 Boomers retire daily. Each one is a library burning.

The institutional knowledge walking out the door isn't in documents. It's in **relationships** — who calls whom, who trusts whom, who knows which workaround for which system.

SimDecisions reveals this. Run the simulation with Pat (retiring in 6 months). Then run it without Pat. The delta IS Pat's institutional value.

**Mirror Before Guillotine:** Simulate before eliminating roles. Discover the hidden dependency networks before they snap.

Three paths for every role:
1. **Retain + Augment** — Keep the human, add AI assistance
2. **Redeploy** — Move the human to higher-value work
3. **Extract** — Capture the knowledge before the human leaves

Never eliminate without extracting. The library burns only if you let it.

---

## 12. Connection to DEIA Federalist Papers

The 20-paper DEIA Federalist Papers series establishes the governance philosophy. SimDecisions is the execution engine.

| Federalist Principle | SimDecisions Implementation |
|---------------------|---------------------------|
| #NOKINGS — human override always | Human as Tier 4 oracle, always available |
| Protocol of Grace — structured conflict resolution | Sensitivity analysis identifies where conflicts will emerge |
| Ethics as infrastructure | Four-vector profiling encodes values, not just capabilities |
| Bounded scope per agent | Oort Cloud Partitioning defines boundaries |
| Observable, auditable | Event ledger captures every action with seed |
| Evolutionary governance | Neural Feedback Circuit enables continuous improvement |
| Multi-vendor diversity | Oracle tiers support any model provider |
| The Commons | Shared event ledger = shared truth |

The Federalist Papers answer "why govern?" SimDecisions answers "how, concretely?"

---

## 13. Roadmap Connection

### Current Phase: Phase 2 — Metrics & Observability

| Task | Status | Relevance |
|------|--------|-----------|
| TASK-009: Event Ledger v1 | PENDING | Foundation for ALL of the above |
| TASK-010: Cost Tracking | PENDING | Oracle tier cost management |
| TASK-011: Dashboard v1 | PENDING | Visibility into system state |
| TASK-012: Export Formats | PENDING | Data portability |

### What This Session Adds to TASK-009

The event ledger schema MUST include:
- `domain` field (enables per-domain α)
- `signal_type` field (gravity/light/internal → α computation)
- `oracle_tier` field (0-4 → cost tracking + graduation)
- `random_seed` field (reproducibility → sensitivity → validation → fraud detection)

Without these four fields, none of the architecture described in this document is possible. With them, everything is.

### Future: Entity Profile Schema (New Task Needed)

An `entity_profiles` table with temporal four-vector measurements. This is the bridge between the event ledger (raw data) and the simulation engine (decisions). Suggest: **TASK-009B or TASK-013** (new).

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **Alterverse** | A branched simulation exploring an alternative future |
| **Core** | Tightly coupled elements requiring full simulation fidelity |
| **Cloud** | Loosely coupled elements that can be approximated |
| **Gravity signal** | Mandatory, blocking communication between entities |
| **Light signal** | Informational, non-blocking communication |
| **Internal signal** | Autonomous action with no external dependency |
| **Oracle** | Any source of prediction, rated by tier (0-4) |
| **VOI** | Value of Information — whether a better prediction would change the decision |
| **α (alpha)** | Autonomy vector — how independently an entity operates per domain |
| **σ (sigma)** | Strength vector — how well an entity performs per domain |
| **π (pi)** | Preference vector — what an entity wants to do per domain |
| **ρ (rho)** | Reliability vector — probability of success given entity + task + conditions + others |
| **Seed** | Random number seed enabling reproducible simulation runs |
| **Envelope** | Expected outcome range from sensitivity analysis |

## Appendix B: Files Generated This Session

| File | Content |
|------|---------|
| BOK-PATTERN-oort-cloud-partitioning.md | Full BOK-SIM-001 pattern |
| BOK-PATTERN-prophecy-engine.md | Full BOK-SIM-002 pattern |
| BOK-PATTERN-alterverse-tree.md | Full BOK-SIM-003 pattern |
| BOK-PATTERN-autonomy-ratio-neural-feedback.md | Full BOK-SIM-004 pattern |
| The-Wind-Tunnel-SimDecisions-Think-Piece.docx | Marketing/vision piece |
| **This file** | Complete session capture |

---

---

## 14. Data Ingestion: Observation as Requirements

### The Inversion

Traditional approach: Interview stakeholders → write requirements → build system. The spec is declared by authority.

SimDecisions approach: Ingest behavioral data → observe patterns → infer requirements. The spec is discovered from reality.

**Requirements are just high-confidence patterns.** If something happens 100% of the time, it's a rule. If 80%, it's a strong tendency. If context-dependent, it's complex. The oracle tier spectrum applies here too — Tier 0 requirements are deterministic ("the sun comes up"), Tier 3 requirements are probabilistic and nuanced.

### What Ingestion Reveals

| Data Source | What It Reveals | Vector It Populates |
|-------------|----------------|-------------------|
| Calendar/meeting data | Who coordinates with whom, frequency | Gravity signals → α |
| Email/Slack metadata (graph, not content) | Communication patterns, response times | Signal types → α, σ |
| Ticket/task systems | Who works on what, speed, escalation paths | σ, ρ |
| Git/version control logs | Who changes what, who reviews whom | σ, α |
| Voluntary task selection | What people choose when unconstrained | π (high-α choices only) |
| Badge/presence data | Physical coordination patterns | Gravity signals |
| Financial transaction logs | Flow patterns, timing, dependencies | All vectors |

### The Gap That Breaks Organizations

Every organization has two realities:
- **Declared** — the org chart, policy manual, job descriptions
- **Observed** — what actually happens in the data

The gap between these is where organizations break when restructured. Pat calls the supplier every Tuesday and has for 3 years. Nobody wrote it down. Remove Pat, supply chain breaks.

**Data ingestion is how SimDecisions discovers observed requirements.** Mirror before guillotine means ingesting before restructuring.

### First Domain: Crypto

Starting small and data-rich. Crypto is the ideal first ingestion target:
- **Public data** — blockchain, exchange APIs, social signals all accessible
- **Real-time** — high-frequency, streaming data
- **Well-structured** — standard APIs, known schemas
- **Lucrative** — clear monetization path
- **Fraud-ready** — the sensitivity analysis / outcome envelope work maps directly to market manipulation detection
- **Recent** — Moltbook, MOLT token, pump-and-dump patterns all current

Build the ingestion layer where data is abundant and the payoff is immediate. Generalize from there.

---

## 15. Interface Layer: Beyond Text

### The Current Limitation

Right now SimDecisions is text in, text out. That's one sensory organ. A general hive needs many.

### The Problem

Any general hive should be able to run inference on research, observations, and real-world data streams. But the input surface is limited to text prompts and file-based task exchange. This constrains what the system can observe and therefore what requirements it can discover.

### What's Needed: Standard Modes of Entry

**Plugins** — modular connectors that give the hive new senses:
- API connectors (exchange data, social platforms, enterprise systems)
- File watchers (git repos, shared drives, document stores)
- Stream consumers (websockets, event buses, message queues)
- Structured data readers (CSV, JSON, databases, spreadsheets)
- Future: image/video/audio analysis pipelines

**Standard interfaces** — consistent contracts so any plugin can feed any hive:
- Common event format (maps to event ledger schema)
- Common entity format (maps to four-vector profile schema)
- Common signal format (gravity/light/internal classification)

**The principle:** Each plugin translates a foreign data source into the hive's native language — events with domains, signal types, actors, and seeds. The hive doesn't care where the data came from. It cares about the pattern.

### Phasing

| Phase | Interface | Priority |
|-------|-----------|----------|
| Now | Text/file-based task exchange | Working |
| Phase 2-3 | REST API connectors, JSON/CSV ingestion | Next |
| Phase 4+ | Streaming data, webhooks, real-time feeds | Future |
| Post-v1 | Multi-modal (image, audio, sensor) | Later |

**Start text. Prove the model. Add senses.**

---

## 16. The Organizational Intelligence Thesis

### The Claim

Organizational intelligence is the key to unlocking general intelligence.

### The Argument

1. **What "general" actually means.** Not "good at everything." It's "can handle novel situations by recombining capabilities." A chess engine is narrow. A human is general — not because every neuron is smart, but because the *organization* of neurons recruits the right capability for the situation.

2. **Intelligence is an organizational property, not an individual one.** No single neuron is general. No single ant is general. Your visual cortex can't do language. Your language centers can't do spatial reasoning. But the organization — routing, inhibition, feedback, autonomy gradients — produces general intelligence from specialized components.

3. **The AI industry has this backwards.** They're building bigger neurons. More parameters, longer context, more reasoning tokens. One brain to rule them all. But biology solved general intelligence through organization of specialists, not through one universal specialist.

4. **The four-vector model IS the intelligence framework:**
   - σ = what each node can do (specialization)
   - π = what each node wants to do (energy/motivation)
   - α = how independently each node operates (autonomy structure)
   - ρ = how reliably the system performs given the configuration (emergence)

   That's not HR analytics. That's a theory of mind for multi-agent systems.

5. **Testable prediction:** Five mediocre models, properly organized (right α vectors, signal routing, oracle tier selection, neural feedback) will outperform a single frontier model on complex multi-domain problems. Not because any one is smarter — because the *system* is smarter.

6. **The oracle tiers prove it.** No single tier is general. Tier 0 can't reason. Tier 3 can't be cheap. Tier 4 can't scale. But organized across tiers with VOI routing, the system is general even though no component is.

7. **Data ingestion completes the picture.** General intelligence isn't just producing outputs — it's ingesting reality and inferring requirements. A baby doesn't read a requirements doc about gravity. It drops things, observes they fall, infers the rule. The AI giants produce content without ever truly observing reality as a system.

8. **SimDecisions is the first tool that models, tests, and optimizes the organization itself.** Not the individual agents. The arrangement of agents. The governance. The signal structure. The autonomy gradients. The thing that makes a collection of specialists into a generally intelligent system.

9. **The Federalist Papers aren't philosophy — they're an AGI governance specification.** Conscience, coordination, grace, bounded scope, evolutionary governance — these are the missing layer between "collection of smart agents" and "actual general intelligence."

### Status: Thesis, not proof. Explore further.

---

## 17. Policy Experimentation: Tweaking Core Beliefs

### The Idea

Don't just simulate different team structures. Simulate different *rules*. What happens when you change the definition of "done"? When you relax quality gates? When you tighten them?

### Mechanism

This is the Alterverse Tree applied to organizational policy:

1. **Checkpoint** current simulation state
2. **Fork** into branches with different policy parameters
3. **Run** identical workloads under each policy
4. **Compare** outcomes across quality, speed, cost, carbon

### Example Experiments

| Policy Variable | Branch A | Branch B | What You Learn |
|----------------|----------|----------|---------------|
| Code review required | Yes (strict) | No (trust-based) | Speed gain vs. defect cost |
| Spec adherence tolerance | ±5% deviation | ±25% deviation | When sloppiness enables creativity |
| Escalation threshold | Escalate at 80% confidence | Escalate at 50% | Cost of caution vs. cost of errors |
| Human gate on deploy | Always | Only for critical paths | Where human oversight pays for itself |

### Hallucination as Variable

The industry treats hallucination as failure. But creativity and hallucination are the same mechanism at different confidence thresholds.

Lower the quality gate on early-stage brainstorming: you might get garbage or a novel approach nobody would have spec'd. **SimDecisions can measure which.**

Run 100 alterverses: 50 with tight spec adherence, 50 with loose. Compare outcomes. Now you have DATA on when divergence pays and when it costs.

This reframes the conversation from "hallucination is bad" to "what's the optimal creativity tolerance for THIS task type?"

---

## 18. LLM Experimentation Lab

### The Realization

SimDecisions already has CLI plugins for Claude, Codex, and Gemini. That's not just an execution layer — it's an experimentation platform.

### What You Can Test Right Now

**Configuration experiments:**

| Experiment | Setup | Measures |
|-----------|-------|----------|
| 1 agent × 60 min vs. 4 agents × 15 min | Same task, two org designs | σ (quality), ρ (reliability), cost, time |
| Claude vs. Gemini on spec-heavy tasks | Same prompt, different models | σ per domain, cost per quality unit |
| Single-model deep pass vs. two-model review chain | One agent writes, vs. one writes + one reviews | Defect rate, total cost, wall-clock time |
| Prompt structure A vs. B vs. C | Same task, different instruction formats | Output quality, token efficiency |
| Temperature/creativity settings | Same task, dial up divergence | When hallucination becomes innovation |

**What makes this different from standard benchmarking:**
- Not abstract (MMLU scores). Measured on YOUR tasks, YOUR standards, YOUR context.
- Not one-shot. Run 100 times with different seeds. Statistical significance, not anecdotes.
- Not isolated. Measures how models perform WITHIN an organizational structure, not in a vacuum.
- Captures cost in three currencies simultaneously.

### The Three-Currency Cost Model

Every action in SimDecisions has a price in three economies (per Federalist No. 12 — Energy and Entropy):

| Currency | What It Measures | Event Ledger Field |
|----------|-----------------|-------------------|
| **Tokens** | Computational attention | `cost_tokens` |
| **Dollars** | Financial cost | `cost_usd` |
| **Carbon** | Environmental impact | `cost_carbon` |

An experiment result isn't "Branch A is better." It's "Branch A produces 15% higher σ at 2x token cost, 1.8x dollar cost, and 2.1x carbon cost. Is that trade worth it?"

Carbon tracking has been in the protocol since Federalist No. 12. It needs to be in the event ledger schema alongside tokens and dollars. **Add `cost_carbon` to the event ledger.**

### The Bootstrap Loop, Fully Realized

SimDecisions uses AI agents → to run experiments on AI agents → to optimize how AI agents are organized → to improve SimDecisions.

The wind tunnel optimizes the wind tunnel. Every experiment you run improves the system that runs experiments. This is the self-improving loop the roadmap describes, but applied to LLM orchestration itself.

### Immediate Application

No new infrastructure needed. Today's setup can already:
1. Define a task
2. Dispatch to Claude CLI, Codex, or Gemini
3. Capture results in event ledger
4. Compare outcomes

The experimentation framework is the EXISTING hive architecture used intentionally. Design experiment → configure alterverses → run → measure → learn.

---

## Addendum: Peer Review Notes (Gemini, Feb 4 2026)

The architecture was reviewed by Gemini. Three suggestions were raised. Disposition below, plus one original insight triggered by the review.

### A.1 Measuring π: Constrained vs. Unconstrained Choice

**The problem:** π (preference) is hard to measure because entities often don't have free choice. A developer who writes only Python may love Python — or may never have been offered Rust tickets.

**Attempts alone are insufficient.** They tell you effort, but effort is gated by opportunity AND pressure. The missing denominator is `choices_available`, and even that is polluted by authority.

**Three measurement conditions for π:**

| Condition | α Level | What You're Measuring | π Signal Quality |
|-----------|---------|----------------------|-----------------|
| **Constrained** | Low α | Compliance — entity does what it's told | None. This measures σ, not π. |
| **Semi-constrained** | Medium α | Partial preference, partial compliance | Noisy. Useful in aggregate over time. |
| **Unconstrained** | High α | True preference — entity chose freely | High. This is real π data. |

**Implication:** π accuracy is a function of α. You can only trust π measurements taken under high-α conditions. Low-α "choices" are assignments, not preferences.

**Practical application:** To measure π for an entity, filter their event ledger to high-α events only. What do they do when nobody's telling them what to do? That's π.

**Alterverse application:** You can deliberately raise α in a simulation branch (give the entity full autonomy) specifically to observe what they choose. This is a controlled experiment for π, not a special mode — just an alterverse with one variable changed.

### A.2 ρ Relational Matrix — Future Optimization

Gemini suggested a dedicated `relational_matrix` table for tracking pairwise ρ between entities. This is valid as a future optimization but not required for v1. The event ledger already captures actor + target + domain + outcome. Pairwise ρ can be computed by filtering events where both entities participate and measuring outcomes. A materialized view or dedicated table becomes worthwhile when query performance demands it — likely at scale, not at MVP.

**Status:** Noted for post-v1 optimization. No schema change needed now.

### A.3 Ethics Gate in Neural Feedback Circuit

Gemini raised the concern that the Neural Feedback Circuit could optimize for σ (strength) at the expense of π (preference/well-being) — essentially grinding entities into high-performance misery.

This is already addressed architecturally: the Tier 4 human oracle provides an override at every decision point (Federalist No. 16, Human Sovereignty). The system cannot autonomously optimize π to zero because human review gates exist at the governance layer.

**To make this explicit:** The Neural Feedback Circuit's graduation/demotion logic must include π as a constraint, not just σ. An oracle configuration that improves σ outcomes while degrading π scores should flag for human review, not auto-graduate. One line in the graduation criteria: **"No graduation if π trend is negative."**

**Status:** One-line addition to BOK-SIM-004 graduation criteria. No structural change.

---

## 19. Competitive Landscape: AI Agent Orchestration (Feb 2026)

### Market Segmentation

The market has split into two tiers:

**Conductor tools** (single agent, interactive): Cursor, Claude Code, Gemini CLI, Windsurf, Kiro. These are sophisticated pair programmers. Most teams are here today. The agent helps you code; you remain in the loop for every decision.

**Orchestrator tools** (multi-agent, parallel): Roo Code, Gas Town, Claude-Flow, Code Conductor, Claude Squad. These manage fleets of agents working simultaneously. This is frontier territory forming RIGHT NOW — January/February 2026 is the inflection point.

SimDecisions operates at a third level: **Organizational Intelligence** — not just orchestrating agents, but measuring, governing, simulating, and optimizing how agents are organized.

### 19.1 Roo Code

Open-source VS Code extension (22k+ GitHub stars). Multi-agent orchestration via specialized **Modes**: Architect, Code, Debug, Ask, Orchestrator, plus custom modes.

**Architecture:** Orchestrator mode decides which specialized mode handles which subtask. Each mode has tool restrictions and custom system prompts. Model-agnostic BYOK — works with OpenAI, Anthropic, Gemini, Ollama, local models. Sticky model preferences per mode.

**Key features:**
- Mode-based delegation with tool restrictions per role
- Permission-based control (approve file changes/commands)
- Auto-approval for streamlined workflows
- Roomote Control (remote task delegation from web/Slack/GitHub)
- MCP protocol support
- Community mode gallery for sharing configurations

**What it lacks:** No measurement layer. No entity profiling over time. No three-currency cost model. No simulation. No governance policies. No quality tracking (σ). Orchestrates modes but doesn't learn from organizational patterns.

**User sentiment:** "Best AI coding agent extension." "Beats Cursor hands down." "Fantastic for large projects that would take weeks or months." More expensive than alternatives but more effective.

**Cost model:** Free extension, pay for API usage.

### 19.2 Claude Code Tasks (now Claude Agent SDK)

Anthropic's native multi-session coordination system. Released v2.1.16 (Jan 2026). Replaced ephemeral "To-dos" with persistent "Tasks."

**Architecture:**
- Dependency graphs (DAGs) vs linear task lists — tasks can block other tasks
- Disk-backed persistence — survives crashes, context compaction, session restarts
- Cross-session coordination — multiple Claude instances share task state
- Subagent spawning via Task tool (specialized agents: Explore, Plan, general-purpose)
- Background execution — long-running tasks don't block workflow
- Aggressive context management — /clear or /compact without losing project roadmap

**Subagent types:**
- Explore (read-only, fast codebase search)
- Plan (software architect, implementation planning)
- General-purpose (full tool access, complex multi-step tasks)
- claude-code-guide (documentation lookup)

**Key capability:** Headless mode (`claude -p`) for CI/CD integration. Fan out work across files using scripts. Loop through tasks calling Claude in parallel.

**What it lacks:** No measurement framework. No quality gates beyond pass/fail. No organizational governance policies. No entity capability tracking. No cost visibility beyond raw token count. No simulation layer.

**Strategic note:** Renamed to Claude Agent SDK (Sept 2025) — reflects broader use beyond coding (deep research, video creation, note-taking). MCP server integration for pre-built capabilities (Slack, Asana, Playwright).

### 19.3 Ralph Wiggum

Self-referential AI loop technique, now native plugin for Claude Code. Pioneered by Geoffrey Huntley.

**Core concept:** Feed same prompt to AI agent repeatedly, allowing it to see and improve previous work. Started as bash one-liner, evolved to plugin.

**Mechanism:**
1. Strong prompt with clear "done" criteria (completion promise)
2. Iteration limit (prevents infinite loops)
3. Each iteration: agent sees previous work, improves/fixes/adds features
4. Loop continues until completion promise output or limit reached
5. Work persists in files, Git history accumulates

**Key insight:** "Deterministically bad in an undeterministic world." Embraces iteration and honest self-assessment. Works because it mirrors how humans solve complex problems — try, observe, adjust, repeat. Ralph automates the loop.

**Use cases:** Mechanical tasks (add JSDoc to every function). Tasks with tests (self-verifying). Overnight sessions ("define work, start loop, go to bed, wake to finished code"). Examples: "Cursed" programming language built over 3 months; 1,000 workflows fixed in under 40 minutes.

**Limitations:** Each iteration consumes API tokens. 50-iteration loop on complex task = significant cost. Requires clear completion criteria — vague prompts waste iterations. Not infallible — always review generated code.

**What it lacks:** No learning from organizational patterns. No vector tracking across agents. No cost visibility. No governance. No simulation. Iterates but doesn't measure what worked or why.

**Anthropic response:** Made Ralph native. Tasks system provides persistent state, dependencies, cross-session coordination that the Ralph community was building manually. "Anthropic saw what developers needed and shipped it."

### 19.4 Gas Town (Steve Yegge)

Most ambitious orchestration system. Coordinates 20-30+ concurrent Claude Code agents. Built on Beads (Git + SQLite backend for version control of structured data). Released January 1, 2026.

**Seven operational roles:**
- **Mayor** — Primary coordinator. Claude Code instance with full workspace context. Your main interface.
- **Crew** — Per-rig coding agents with long-lived identities, named by user. Great for design work with back-and-forth.
- **Polecats** — Ephemeral worker agents. Spawn, complete task, disappear.
- **Refinery** — Manages merge queue.
- **Witness** — Monitors system health.
- **Deacon** — Monitors system health (secondary).
- **Dogs** — Additional monitoring.

**Architecture:**
- Town (HQ directory, contains all project rigs)
- Rigs (project containers, each wraps git repository)
- Hooks (git worktree-based persistent storage, survives crashes)
- Beads (atomic work units, JSON-based issue tracking in Git)
- Convoys (bundle multiple beads assigned to agents)
- GUPP principle: "If there is work on your hook, YOU MUST RUN IT."

**Key differentiator:** External state management. State lives in Git, not bloated context windows. Each worker gets git worktree, task from Beads, runs until completion. Parallel execution at scale. Graceful degradation — every worker can operate independently.

**Cost reality:** $100-200/hour in API fees. Users report $60k/year burn rate. Steve Yegge on third $200/month Claude Pro Max plan, first two maxed out weekly limits. "Murderous rampaging Deacon" and auto-merged failing tests reported. Two weeks old at launch, "100% vibe coded."

**What it lacks:** No measurement layer. No entity profiles. No three-currency cost model. No governance policies. No simulation. No quality tracking. No alterverse branching. Coordinates execution brilliantly but doesn't learn from organizational patterns or optimize agent configuration.

**Expert opinion (Justin Abrahms, 60k LOC/month):** "Gastown is too complex, but with refinement, very big unlock." Hardest problem: "keeping it fed — churns through implementation plans so quickly you need extensive design/planning roadmap."

### 19.5 Claude-Flow

Multi-agent orchestration framework by ruvnet. Claims "#1 in agent-based frameworks."

**Architecture:** User → Claude-Flow (CLI/MCP) → Router → Swarm → Agents → Memory → LLM Providers, with learning loop feedback. Swarms led by "queens" that coordinate work. Vector memory stores successful patterns. Neural networks learn from outcomes. Adaptive routing based on what works best.

**Key claims:** Smart routing skips expensive LLM calls when possible (simple edits use WebAssembly transforms for free). Token compression reduces API costs 30-50%. Self-learning neural capabilities. Interesting but largely unvalidated claims at this point.

### 19.6 Other Notable Tools

- **Cline** — Model-agnostic, stepwise planning, enterprise governance focus (.clinerules for permissions, SSO/RBAC, audit trails, SOC 2/GDPR alignment)
- **Code Conductor** — GitHub-native orchestration (tasks are GitHub Issues, agents claim them, work in branches, open PRs)
- **Conductor Build (Melty Labs)** — Each agent gets isolated Git worktree, dashboard showing "who's working on what"
- **Claude Squad** — Spawns multiple Claude Code instances in tmux panes. Dead simple.
- **Goose** — Local autonomous agent, multi-step tasks, works offline with local models
- **Aider** — Command-line AI coding assistant, works with Git repositories
- **LangGraph** — Multi-step workflow orchestration framework
- **BMAD/SpecKit** — Simulate org charts (Analyst → PM → Architect → Dev → QA). Sequential handoffs, phase gates, role confusion. The 19-agent trap — cargo cult SDLC.

### 19.7 The Trap: Persona Simulation vs Operational Roles

Critical architectural distinction discovered in research:

**Persona simulation (BMAD/SpecKit):** Simulate human org structure with SDLC personas. Analyst → PM → Architect → Dev → QA. Sequential handoffs recreating human coordination friction. Optimizing for explainability over effectiveness. **This is the wrong approach.**

**Operational roles (Gas Town, SimDecisions):** Mayor orchestrates, Polecats execute in parallel, Witness monitors. Each worker gets task and runs. External state via Git. Parallel execution with coordination. **This is the correct pattern.**

SimDecisions should use operational roles for hive agents, not persona simulation. The hive architecture already reflects this — Q33N coordinates, bees execute — but this distinction should be made explicit in positioning.

---

## 20. Critical Strategic Finding: Anthropic Is Productizing the Community

### The Pattern

3 confirmed instances of community innovation → Anthropic native feature:

1. **Beads** (Yegge's Git+SQLite task memory) → **Tasks system** in Claude Code v2.1.16. Anthropic credited Yegge explicitly.
2. **Gas Town** (Yegge's multi-agent orchestrator) → **TeammateTool** discovered feature-flagged in Claude Code binary. 13 operations, directory structures, environment variables. Patterns: Leader, Swarm, Pipeline, Watchdog. Nearly identical to Gas Town architecture. "Anthropic productizing Yegge twice."
3. **Ralph Wiggum** (iteration loops) → **Native plugin** support in Claude Code. Completion promises, persistence, cross-session state.

### Implication for SimDecisions

The window for differentiation on orchestration alone is closing. Anthropic will ship native multi-agent orchestration (TeammateTool) that handles the basic coordination layer — Mayor/Polecats/Witness patterns.

**SimDecisions must differentiate on what Anthropic will NOT build:**
- Organizational intelligence (four-vector entity model)
- Three-currency cost optimization
- Policy experimentation (Alterverse Tree)
- Risk-based autonomy governance
- Simulation before deployment
- Cross-vendor orchestration (not just Claude agents)
- Requirements discovery from behavioral data

**Anthropic builds better tools. SimDecisions builds the brain that decides how to use them.**

---

## 21. YouTube Transcript Analysis: Capability Overhang

Source: YouTube analysis of Sam Altman hiring slowdown, GDP-VAL benchmarks, and power-user agent workflows.

### What It Confirms

1. **The overhang thesis validates our product category.** GPT 5.2 Pro hitting 74% preferred over human experts on scoped tasks. But most people use AI as chatbot. Gap is organizational, not capability. That's our thesis.

2. **"Assign tasks, don't ask questions" = our task file loop.** Shift from prompting to declarative specification — describe end state, provide success criteria, let AI figure out how.

3. **1×60 vs 4×15 explicitly called out.** Speaker describes running 5-6 Claude Code windows simultaneously. We designed this experiment yesterday. Market is asking this question; we built framework to answer it.

4. **"Specification > implementation" confirms skill shift.** New skill: defining what you want precisely enough that AI builds it, then writing tests capturing success criteria, then reviewing for conceptual errors. That's σ measurement. That's our quality gates.

5. **Cost tracking is table stakes.** Every agent loop has economics. Three-currency tracking is not optional.

### What Challenges Our Assumptions

1. **Speed of adoption faster than planned.** Developers running multi-agent overnight loops NOW, not 2027. Phase 3-4 timelines may be too leisurely.

2. **Over-indexing on simulation, under-indexing on production orchestration.** Immediate market demand is "help me manage 6 Claude Code windows." Production mode may need to ship before simulation mode.

3. **"Ralph" and Gas Town are live competition.** Simpler versions of our hive without governance/measurement/simulation layers. But they exist and people use them.

### New Ideas

1. **Risk-based autonomy policies = killer feature.** α vectors applied as organizational policy. High-risk code = low α (tight supervision). Prototype code = high α (let it run). Enterprise sale positioning.

2. **The "eval" problem = our σ measurement.** Most teams don't know how to measure agent quality beyond "does it work?" SimDecisions provides the framework.

3. **"Agents make junior developer errors" reframes oracle tiers.** Current models: Tier 1-2 oracle behaviors. The upgrade isn't making them Tier 3 — it's organizational structure around Tier 1-2 agents so errors get caught. Supervision as a service.

4. **"Stale assumptions" as ongoing risk.** Entity profiles must be temporal. What Claude could do in January isn't what it can do in February. Already designed for, but reinforces importance.

---

## 22. Revised Implementation Priorities

Based on competitive landscape research and market timing analysis:

### URGENT (Ship for Production Orchestration — Market Forming NOW)

| Task | Why | Competitive Gap |
|------|-----|-----------------|
| TASK-011: Dashboard | Market wants agent fleet management NOW | Gas Town: zero visibility. Roo Code: no metrics. |
| TASK-010: Cost tracking | $60k/year burn rates with zero visibility | Nobody tracks three currencies (tokens, $, carbon) |
| TASK-009: Event Ledger | Foundation for all measurement | No competitor has append-only decision audit trail |

### HIGH (Competitive Differentiation)

| Capability | Why | Who Lacks It |
|-----------|-----|--------------|
| Risk-based autonomy policy framework | Engineering leaders need supervision policies per codebase | Everyone — unmet market need |
| Competitive positioning document | Must articulate "they execute, we measure" | Marketing prerequisite |
| MCP protocol integration | Standard for data ingestion plugins | Gas Town, Roo Code have it; we need parity |
| Quality gate framework (σ measurement) | Teams can't evaluate agent output quality | Nobody does this systematically |

### MEDIUM (Core Differentiators)

| Capability | Why |
|-----------|-----|
| Temporal Entity Profile Schema | Track agent capabilities over time (σ drift detection) |
| Data ingestion layer | Passive observation vs active probing for requirements discovery |
| Plugin architecture | Standard interfaces for data sources (MCP-compatible) |
| Policy experimentation framework | Alterverse Tree for A/B testing organizational policies |
| Carbon measurement methodology | Per-model, per-operation carbon tracking |

### REVISED PHASING

**Original:** Phase 2 (Metrics) → Phase 3 (Simulation) → Phase 4 (Visual) → Phase 5 (Ship)

**Revised:** Phase 2 (Metrics + Production Dashboard) → Phase 2.5 (Governance Policies + Cost Optimization) → Phase 3 (Simulation) → Phase 4 (Visual) → Phase 5 (Ship)

**Rationale:** Market wants production orchestration NOW. Simulation is moat but not door. Ship dashboard, cost tracking, policy enforcement first. Prove value in production. Add simulation layer after establishing production foothold.

---

## 23. Competitive Positioning Summary

### The One-Line Differentiator

**"They execute. We measure, govern, and optimize."**

### Comparison Matrix

| Capability | Roo Code | Gas Town | Claude Tasks | Ralph | SimDecisions |
|-----------|----------|----------|-------------|-------|-------------|
| Multi-agent execution | ✅ Modes | ✅ 20-30 agents | ✅ Subagents | ✅ Iteration | ✅ Hive |
| Parallel coordination | ✅ | ✅ | ✅ | ❌ | ✅ |
| Persistent state | Partial | ✅ Git-backed | ✅ Disk-backed | ❌ | ✅ File-based |
| Entity profiling (α,σ,π,ρ) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Three-currency cost | ❌ | ❌ | ❌ | ❌ | ✅ |
| Quality measurement (σ) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Risk-based autonomy (α) | ❌ | ❌ | ❌ | ❌ | ✅ |
| Governance policies | ❌ | ❌ | ❌ | ❌ | ✅ |
| Simulation/branching | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cross-vendor | ✅ | ❌ Claude only | ❌ Claude only | ❌ Claude only | ✅ |
| Data ingestion | ❌ | ❌ | ❌ | ❌ | ✅ (planned) |
| Requirements discovery | ❌ | ❌ | ❌ | ❌ | ✅ (planned) |

### Go-to-Market Angles

1. **Enterprise policy:** "Production code requires α=0.2. Prototype code allows α=0.8. SimDecisions enforces the policy and measures outcomes."
2. **Cost optimization:** "Gas Town burns $100-200/hour with zero visibility. SimDecisions tracks every token, dollar, and carbon unit."
3. **Overhang arbitrage:** "Don't guess which agent configuration works best. Measure it."
4. **Governance layer:** "Every multi-agent deployment will eventually need what Moltbook lacked — conscience, gates, sovereignty, grace. We built it."

### Event Ledger Schema Update

Based on Ralph Wiggum's completion promise pattern and Gas Town's coordination needs, two fields added:

```
completion_promise  TEXT    -- Ralph-style "done" criteria for autonomous loops
verification_method TEXT    -- How to validate task completion (test command, human review, σ threshold)
```

These join existing fields: domain, signal_type, oracle_tier, random_seed, cost_tokens, cost_usd, cost_carbon.

---

*This document captures working ideas, not final architecture. Everything is subject to revision. The point is: don't lose a thing.*

**— Dave × Claude, Feb 4, 2026**
**Addendum: Dave × Claude, with Gemini peer review, Feb 4, 2026**
**Addendum: Competitive landscape research and market analysis, Feb 4, 2026**
