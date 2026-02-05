# SimDecisions v1.0 — Informative Specification

**Brand:** SimDecisions.com  
**Tagline:** *The process is the product.*

---

## 1. Problem Statement
Organizations redesign org charts, adopt AI, change staffing, and alter processes without a controlled way to test consequences. Most tools either:
- model processes without executing them, or
- execute work without capturing how it happened.

SimDecisions exists to close this gap by providing an **executable, replayable organizational wind tunnel** that simultaneously produces **real business outputs**.

The platform answers four questions at once:
1. What happened operationally (wait times, utilization, throughput)?
2. What happened socially (communication load, coordination failure, role confusion)?
3. What happened economically (labor cost, AI cost, latency)?
4. What was produced (specs, code, research, presentations)?

---

## 2. Product Definition
SimDecisions is a **scenario‑based business simulation and production platform** where users:
1. Visually design organizations, workflows, queues, routing, and forecasts.
2. Populate those designs with **sim‑agents** (LLM‑powered people or processes).
3. Execute scenarios in multiple runtime modes.
4. Observe metrics and artifacts as they are created.
5. Pause, rewind, branch timelines, and test alternatives.
6. Export the entire simulation as a portable, shareable package.

SimDecisions is not a toy simulator—it is a **factory** that produces real deliverables while capturing the process that produced them.

---

## 3. Architectural Principles

### 3.1 Local‑first, cloud‑ready
Version 1 runs locally (browser UI + localhost services). The same contracts support future deployment to Vercel (UI) and Railway (services).

### 3.2 “Mind vs Body” split

**Server (“Mind”)**
- Authentication and session management
- Persistence of scenarios, runs, branches, artifacts, and metrics
- LLM execution (OpenAI, Claude; optional BYO keys)
- Voyage embeddings
- BABOK / PMBOK expert prompt packs

**Client (“Body”)**
- Visual designers (BPMN, org, queues)
- Simulation runtime and timeline controls
- Communication surfaces and sim‑agent avatars
- Real‑time dashboards and overlays
- Scenario builder and A/B runner

### 3.3 Event sourcing
All behavior is recorded as an append‑only **event ledger**. Replay, rewind, and branching are derived from this ledger.

---

## 4. Standard Simulation Package

### 4.1 Purpose
Simulation scenarios must be reproducible and shareable. A user should be able to send a file to someone else who can run the same simulation locally.

### 4.2 File format
A **`.simdecisions.zip`** bundle containing human‑readable files:

- `manifest.yaml` — metadata, engine version, feature flags
- `scenario.yaml` — objectives, modes, seeds
- `org.yaml` — roles, staffing, skills, costs
- `process.bpmn` — workflow definition
- `queues.yaml` — routing, priorities, SLAs
- `forecast.yaml` — arrival curves and distributions
- `schedule.yaml` — scheduled changes and interventions
- `models.yaml` — LLM provider/model per sim‑agent
- `branches/` — fork definitions and event ledgers
- `artifacts/` (optional) — produced outputs
- `metrics/` (optional) — rollups and summaries

### 4.3 Simulator‑generated packages
The simulator can generate scenario packages as outputs, enabling scenarios to produce other scenarios (baseline + variants, A/B packs, best‑branch exports).

---

## 5. Simulation Engine

### 5.1 Timing model
- Core engine: **discrete‑event simulation (DES)**
- Truth is the Future Event List
- UI uses a separate playhead clock for animation

### 5.2 Work arrival generation
Primary method: **event‑driven Poisson arrivals** with exponential inter‑arrival times, extended to time‑varying rates via interval λ(t).

### 5.3 Work items
Work items represent calls, tickets, tasks, or artifact requests. Each has arrival time, skill requirements, priority, SLA, and metadata payload.

### 5.4 Queues and routing
- FIFO, LIFO, and priority queues
- Skills‑based routing
- SLA targets and escalation rules
- Optional abandonment modeling

### 5.5 State machines (supporting role)
State machines validate lifecycle transitions (agents, work items, artifacts) but do not drive the simulation clock.

---

## 6. Sim‑Agents

### 6.1 Definition
A sim‑agent represents a person or process with:
- Role and responsibilities
- Skills and constraints
- Availability calendar
- Cost model
- LLM provider/model/version
- Layered instructions (base + scenario + user)

### 6.2 Multi‑LLM experimentation
Different sim‑agents may use different LLM providers or versions, enabling side‑by‑side quality, cost, and latency comparisons.

### 6.3 Expert packs
Server‑side BABOK and PMBOK expert agents review artifacts for governance and quality compliance.

---

## 7. Communication System

### 7.1 Channels
- Team chat
- DMs
- Email threads (to/cc)
- Meetings (agenda, transcript, decisions)

### 7.2 Delivery
Primary routing is explicit addressing. Optional embedding‑based suggestion lanes support overload realism.

### 7.3 Human participation
A human participant may join simulations to communicate, approve checkpoints, or co‑produce outputs.

---

## 8. Orchestration Strategies

1. **Comms‑led:** work emerges from conversation and PM coordination.
2. **Dependency‑aware notifier:** sim‑agents are notified when prerequisites clear (no polling).
3. **Fungible workforce:** interchangeable capacity routed via queues (contact‑center mode).

---

## 9. Runtime Modes

1. **Full Auto:** run to completion.
2. **Semi‑Auto:** pause at human checkpoints.
3. **Human‑Speed:** enforce predicted human task durations.
4. **Real‑Time:** always‑on system accepting live requests.

All modes support pause, speed control, jump‑to‑time, rewind, and branching.

---

## 10. Scheduled Changes & Scenario Builder

Scheduled changes (staffing, volume, policy) are first‑class events defined in `schedule.yaml` and editable in the UI. The Scenario Builder enables A/B testing with matched seeds and automated comparison.

---

## 11. Test‑Driven‑Gen

Artifacts are governed by tests defined first:
- Schema completeness
- Requirement coverage
- Rubric scoring
- Alignment checks

Artifacts must pass before advancing.

---

## 12. Metrics & Prediction

Metrics include queue performance, workforce utilization, process cycle times, AI cost/latency, and communication overhead. Estimated wait times and percentile bands are surfaced for routing decisions.

---

## 13. Outputs & Integrations

### v1
- Browser downloads for artifacts, run summaries, and scenario packages

### Roadmap
- GitHub, Google Drive, Apple Drive
- Discord/Slack ingestion

---

## 14. Build Order & Delivery Plan

Development proceeds in disciplined weekly sprints:

1. Foundations & schemas
2. DES engine & arrivals
3. Timeline controls & branching
4. Visual designers (BPMN/org/queues)
5. Sim‑agents & multi‑LLM
6. Communication realism
7. Orchestration strategies
8. Test‑Driven‑Gen
9. Metrics & scenario builder
10. Hardening & demo readiness

With one human lead and two AI assistants, a full v1 is achievable in ~8–10 weeks.

---

## 15. Summary
SimDecisions is not merely a simulator or an AI agent framework. It is an **executable theory of organizational work**—a system where process design, execution, measurement, and production are unified into a single, replayable reality.

*The process is the product.*

