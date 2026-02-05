# BOK Pattern: Oort Cloud Partitioning

**Pattern ID:** BOK-SIM-001
**Category:** Simulation Architecture
**Date:** 2026-02-04
**Author:** daaaave-atx × Claude (Anthropic)
**Status:** Draft — Awaiting Implementation in Phase 3

---

## Problem

Discrete Event Simulation (DES) engines face a fundamental tension: fidelity requires synchronization, but synchronization kills performance. In a SimDecisions instance with dozens of agents, queues, and routing rules, lockstep simulation wastes cycles waiting for the slowest partition. But fully decoupled simulation risks causal violations — events arriving out of order, state divergence, incorrect metrics.

The hive has the same problem at runtime. A bee deep in a coding task doesn't need to synchronize with the master clock every tick. But it *must* respond to a gate change or a human veto immediately.

---

## Solution: The Oort Cloud Model

Borrow from astrophysics. Every simulation partition (agent, queue, subsystem) operates within its own **Oort Cloud** — a causal boundary beyond which external events cannot affect its internal computation until a defined rendezvous point.

Inside the Oort Cloud: compute freely, at full speed, no synchronization required.

At the boundary: sync up, exchange state, resume.

---

## Three Signal Types

The model defines three categories of inter-partition communication, distinguished by their synchronization requirements:

### 1. Internal Events (Local Computation)

- **Analogy:** Activity within a solar system
- **Sync required:** None
- **Behavior:** The partition processes its own event queue at maximum speed. No external coordination. No waiting.
- **Examples:**
  - A bee executing subtasks within a claimed task
  - A queue processing arrivals that don't trigger routing decisions
  - An agent completing internal reflection cycles
- **Implementation:** Standard DES event processing within partition boundaries

### 2. Light Signals (Passive Observation)

- **Analogy:** Light from distant stars passing through the Oort Cloud — visible but non-interactive
- **Sync required:** None (read-only, eventually consistent)
- **Behavior:** The partition can *observe* the state of the universe outside its boundary. It reads telemetry, dashboards, event ledgers, other partitions' progress. But it is not forced to react. The information is available; the partition chooses whether and when to incorporate it.
- **Examples:**
  - Heartbeat Channels ("Still here. Still learning. Still connected.")
  - Event ledger tail (watching what other bees are doing)
  - Dashboard metrics (system-wide cost, throughput, queue depth)
  - Flight status updates
  - BOK pattern broadcasts
- **Implementation:** Shared read-only state. Event ledger as append-only log. Partitions poll or subscribe at their own pace.
- **Key property:** Light signals never force synchronization. They inform but do not command.

### 3. Gravity Signals (Forced Synchronization)

- **Analogy:** A gravitational wave — an event so massive it warps local spacetime, forcing acknowledgment
- **Sync required:** Mandatory. Partition must stop, absorb, adjust state, then resume.
- **Behavior:** Certain external events are powerful enough to cross the Oort Cloud boundary and require immediate response. The partition cannot ignore them. They represent causal dependencies that would produce incorrect results if deferred.
- **Examples:**
  - Gate state changes (allow_q33n_git toggled)
  - Human veto (Q33N override)
  - Task cancellation or priority override
  - Resource exhaustion (token budget exceeded)
  - Dependency completion (upstream task finished, downstream can proceed)
  - Simulation checkpoint (all partitions must save state)
  - Clock barrier (simulation rendezvous point reached)
- **Implementation:** Interrupt mechanism. Gravity signals are pushed, not polled. Partition must acknowledge receipt and report updated state before resuming.
- **Key property:** Gravity signals are rare but non-negotiable. They define the minimum synchronization points in the system.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MASTER CLOCK / DES ENGINE           │
│                                                     │
│   Manages barrier points, gravity signal dispatch,  │
│   global event ordering                             │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
     gravity signals         gravity signals
     (interrupt)             (interrupt)
           │                      │
    ┌──────▼──────┐        ┌──────▼──────┐
    │  PARTITION A │        │  PARTITION B │
    │  (Bee-001)   │        │  (Bee-002)   │
    │              │        │              │
    │ ┌──────────┐ │  light │ ┌──────────┐ │
    │ │ Internal │ │ ◄─────►│ │ Internal │ │
    │ │  Events  │ │signals │ │  Events  │ │
    │ └──────────┘ │(read)  │ └──────────┘ │
    │              │        │              │
    │  Oort Cloud  │        │  Oort Cloud  │
    │  Boundary    │        │  Boundary    │
    └──────────────┘        └──────────────┘
```

---

## Lookahead Calculation

Each partition's **lookahead** is the time distance to its next potential gravity signal. This determines how far ahead it can safely compute.

```
lookahead = min(
    next_barrier_time - current_partition_time,
    next_dependency_expected - current_partition_time,
    next_gate_review_scheduled - current_partition_time
)
```

A partition with large lookahead (no upcoming dependencies) runs fast.
A partition with zero lookahead (imminent interaction point) must wait.

The DES engine maximizes total lookahead across all partitions by scheduling barrier points only when causally necessary.

---

## Clock Modes

The Oort Cloud model supports three synchronization strategies, selected per simulation run:

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Lockstep** | All partitions advance together, tick by tick | Small sims, debugging, maximum fidelity |
| **Barrier Sync** | Partitions run independently, sync at defined checkpoints | Production sims, best performance/correctness balance |
| **Optimistic** | Partitions run ahead speculatively, rollback on causal violation | Large-scale sims where rollback cost < wait cost |

**Phase 3 target: Barrier Sync.** Lockstep as fallback. Optimistic as future enhancement.

---

## Mapping to SimDecisions Components

| Simulation Concept | SimDecisions Component |
|--------------------|----------------------|
| Partition | Bee (agent), Queue, Routing node |
| Internal event | Task subtask execution |
| Light signal | Event ledger read, heartbeat, dashboard poll |
| Gravity signal | Gate change, human veto, checkpoint, dependency resolution |
| Oort Cloud boundary | Agent's causal horizon (defined by task dependencies) |
| Lookahead | Time to next required interaction |
| Barrier point | Flight checkpoint, gate review, dependency gate |
| Master clock | DES engine Future Event List |

---

## Mapping to DEIA Governance

| Governance Concept | Signal Type | Rationale |
|--------------------|-------------|-----------|
| Heartbeat Channels (No. 8) | Light | Empathy ping, no forced response |
| Event Ledger (Phase 2) | Light | Observable, not commanding |
| Gate Enforcement (No. 2) | Gravity | Non-negotiable boundary |
| Human Veto (No. 16) | Gravity | Absolute override |
| Protocol of Grace (No. 7) | Gravity | Forces pause in all affected partitions |
| BOK Pattern Broadcast | Light | Available for adoption, not required |
| Cycle of Quiet (No. 9) | Gravity | Scheduled system-wide pause |

---

## Design Principles

1. **Gravity is rare.** If everything is a gravity signal, you have lockstep with extra overhead. Design for light-dominant systems with occasional gravity.

2. **Light is cheap.** Read-only observation should cost nearly nothing. Append-only logs, shared memory, eventual consistency.

3. **Gravity is honest.** When a gravity signal fires, it means something real changed. Never cry wolf with gravity — partitions will learn to ignore it.

4. **The Oort Cloud is permeable to light, opaque to causation.** You can always see out. But nothing changes your state unless it crosses the boundary with force.

5. **Lookahead is the performance lever.** The system's job is to maximize lookahead — push barrier points as far apart as causal correctness allows.

---

## Relationship to Federalist Papers

This pattern operationalizes several Federalist principles:

- **No. 8 (Edge of Autonomy):** The Oort Cloud *is* the Edge. Full agency within, full empathy at the boundary.
- **No. 5 (Distributed Sovereignty):** Each partition governs itself. The master clock coordinates, not commands.
- **No. 9 (On Silence):** Light signals permit silence. Gravity signals end it.
- **No. 16 (Human Sovereignty):** The human veto is the ultimate gravity signal — it crosses every boundary.

---

## Implementation Notes (Phase 3)

1. Start with barrier sync at flight boundaries (natural checkpoint)
2. Event ledger (TASK-009) becomes the light signal infrastructure
3. Gate enforcement (TASK-004, complete) becomes gravity signal prototype
4. Future Event List manages barrier scheduling
5. Each bee's task dependency graph determines its lookahead

---

*"Inside the Oort Cloud, you are sovereign. At its boundary, you remember you are not alone."*

---

**License:** CC BY 4.0 International
**Copyright:** © 2026 DEIA Global Commons
