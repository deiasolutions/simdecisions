# ADR-001: Event Ledger as Architectural Foundation

**Status:** PROPOSED — awaiting Dave's review  
**Date:** 2026-02-04  
**Context:** SimDecisions Architecture Session (Feb 4, 2026)  
**Scope:** Schema decisions that must be right BEFORE TASK-009 coding begins  

---

## Why This ADR Exists

The Feb 4 architecture session revealed that the event ledger is not an observability feature — it's the substrate from which the entire four-vector entity model, oracle tier economics, sensitivity analysis, and fraud detection derive. Getting the schema wrong now means rebuilding foundations later. Getting it right costs almost nothing extra today.

Six decisions are load-bearing. Each one is cheap to include now and expensive to retrofit later.

---

## Decision 1: Full Schema From Day One

### The Decision

The event ledger table includes ALL fields from the architecture session at creation time, even if most are nullable and unused for months.

### The Schema

```sql
CREATE TABLE events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    event_type          TEXT NOT NULL,
    actor               TEXT NOT NULL,
    target              TEXT,
    domain              TEXT,
    signal_type         TEXT CHECK(signal_type IN ('gravity','light','internal')),
    oracle_tier         INTEGER CHECK(oracle_tier BETWEEN 0 AND 4),
    random_seed         INTEGER,
    completion_promise  TEXT,
    verification_method TEXT,
    payload_json        TEXT,
    cost_tokens         INTEGER,
    cost_usd            REAL,
    cost_carbon         REAL
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_actor ON events(actor);
CREATE INDEX idx_events_domain ON events(domain);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_signal ON events(signal_type);
CREATE INDEX idx_events_oracle ON events(oracle_tier);
```

### Why

Adding columns later means either ALTER TABLE migrations (breaking append-only semantics conceptually) or losing the ability to compute vectors from historical data. A null `cost_carbon` column costs zero storage. A missing `domain` column costs a full replay of history.

### What's Nullable Now, Required Later

| Field | v1 Status | When It Becomes Required |
|-------|-----------|------------------------|
| domain | Recommended | Required when α computation ships |
| signal_type | Recommended | Required when α computation ships |
| oracle_tier | Optional (default 3) | Required when Prophecy Engine ships |
| random_seed | Optional | Required when simulation/ensemble ships |
| completion_promise | Optional | Required when Ralph-style loops ship |
| verification_method | Optional | Required when quality gates ship |
| cost_tokens | Recommended | Required when cost dashboard ships |
| cost_usd | Recommended | Required when cost dashboard ships |
| cost_carbon | Optional (null OK) | When carbon methodology exists |

---

## Decision 2: Universal Entity IDs

### The Decision

All actors and targets use a universal entity ID scheme. No field is named `bot_id` in the event ledger. The `actor` and `target` fields accept any entity type.

### The Convention

```
{type_prefix}:{identifier}

Examples:
  agent:BEE-001          — AI agent
  agent:Q33N-001         — Queen orchestrator
  human:dave             — Human operator
  team:frontend          — Team entity
  process:deploy-pipeline — Automated process
  system:minder          — System service
  system:gate-check      — Internal mechanism
```

### Why

The four-vector model (α,σ,π,ρ) profiles ANY entity — human, AI, team, machine, process. If the event ledger hardcodes `bot_id`, every query that computes vectors must special-case entity types. Universal IDs mean one query pattern for all entity types, now and future.

### Migration Note

Existing code uses `bot_id` in task files and some API endpoints. Those remain as-is — they describe task ASSIGNMENT. The event ledger uses the universal scheme for recording WHO DID WHAT. A simple mapping (`bot_id: "BOT-001"` → `actor: "agent:BOT-001"`) handles the bridge.

---

## Decision 3: Signal Type Taxonomy

### The Decision

Every event SHOULD carry a `signal_type` classification from the start. The taxonomy is fixed at three values.

### The Taxonomy

| Signal Type | Meaning | α Implication |
|------------|---------|---------------|
| `gravity` | Mandatory, blocking — cannot proceed without this | Low α (dependent) |
| `light` | Informational, non-blocking — FYI, no response required | Neutral |
| `internal` | Autonomous — entity decided/acted without external input | High α (independent) |

### How α Is Computed (Future, But Schema Must Support)

```
α_domain = count(internal signals in domain) / count(all signals in domain)
```

This is why both `domain` AND `signal_type` must exist on every event. Without either field, α computation requires retroactive classification — which is either impossible (the context is lost) or unreliable (reinterpretation introduces bias).

### Classification Guidelines for v1

| Event Type | Typical Signal Type |
|-----------|-------------------|
| task_created | gravity (assigns work) |
| task_routed | internal (system decision) |
| task_completed | gravity (reports completion) |
| gate_checked | gravity (blocks on approval) |
| gate_passed | gravity (approval granted) |
| message_sent | light (informational) |
| message_broadcast | light (informational) |
| flight_started | gravity (coordination) |
| flight_ended | gravity (coordination) |
| kb_injected | internal (system action) |
| cost_recorded | internal (telemetry) |

---

## Decision 4: Domain Field Semantics

### The Decision

The `domain` field uses a flat, human-readable string taxonomy. No hierarchy, no namespacing, no versioning. Keep it simple and extensible.

### Initial Domain Values

```
coding, design, planning, review, testing, deployment,
communication, coordination, documentation, research,
git, kb, flight, gate, system
```

### Why Flat

Hierarchical domain taxonomies (e.g., `engineering.backend.python`) create classification paralysis and fragile queries. Flat domains can be grouped ad-hoc in analysis:

```sql
-- "engineering" = coding + testing + review + deployment
WHERE domain IN ('coding', 'testing', 'review', 'deployment')
```

New domains are added by using them. No schema migration, no enum updates. The CHECK constraint is deliberately ABSENT on domain — it's a free-text field indexed for performance.

---

## Decision 5: Entity Profiles — Design Now, Build Later

### The Decision

The `entity_profiles` table schema is SPECIFIED in this ADR but NOT created in TASK-009. It will be created when four-vector computation ships (likely Phase 3). Specifying it now constrains the event ledger design to ensure compatibility.

### The Schema (Future)

```sql
CREATE TABLE entity_profiles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id       TEXT NOT NULL,
    domain          TEXT NOT NULL,
    vector_type     TEXT NOT NULL CHECK(vector_type IN ('alpha','sigma','pi','rho')),
    value           REAL NOT NULL,
    measured_at     TEXT NOT NULL,
    confidence      REAL,
    sample_size     INTEGER,
    conditions_json TEXT,
    source          TEXT CHECK(source IN ('computed','observed','declared','imported'))
);

CREATE INDEX idx_profiles_entity ON entity_profiles(entity_id, domain);
CREATE INDEX idx_profiles_vector ON entity_profiles(vector_type);
CREATE INDEX idx_profiles_time ON entity_profiles(measured_at);
```

### Why Specify Now

The event ledger's `domain` values must MATCH the entity profile's `domain` values. If we define event domains as one taxonomy and profile domains as another, the bridge breaks. Specifying both schemas together ensures alignment.

### The `source` Field

| Source | Meaning |
|--------|---------|
| computed | Derived from event ledger aggregation |
| observed | Measured from actual task outcomes |
| declared | Self-reported (personality tests, preferences) |
| imported | Ingested from external systems |

This matters because π (preference) measured under high-α conditions (`source: observed`) is more trustworthy than π from a personality test (`source: declared`). The Gemini peer review caught this distinction.

---

## Decision 6: Three-Currency Cost Model From Day One

### The Decision

Every cost-bearing event records cost in three currencies: tokens, dollars, and carbon. All three columns exist from day one. Carbon is nullable until methodology exists.

### Why Three Currencies

Per Federalist No. 12 (Energy and Entropy), the Republic's moral economy tracks three intertwined economies. But the practical reason is simpler: the competitive landscape shows NOBODY tracks three currencies. Gas Town burns $100-200/hour with zero visibility. This is differentiation that ships in Phase 2.

### Cost Recording Pattern

```python
# Every LLM call records:
{
    "cost_tokens": 1847,        # Always available from API response
    "cost_usd": 0.037,          # Computed from token count × model pricing
    "cost_carbon": None          # Null until we have methodology
}
```

### Token-to-Dollar Mapping (v1, Hardcoded)

| Model | Input $/1K tokens | Output $/1K tokens |
|-------|-------------------|-------------------|
| Claude Sonnet | 0.003 | 0.015 |
| Claude Opus | 0.015 | 0.075 |
| Claude Haiku | 0.00025 | 0.00125 |
| GPT-4o | 0.0025 | 0.01 |

Stored in config, not in schema. Updated manually as pricing changes. Good enough for v1.

---

## What This ADR Does NOT Decide

These are explicitly deferred:

1. **Entity profile computation logic** — how α,σ,π,ρ are actually calculated from events. That's Phase 3 work.
2. **Oracle tier selection logic** — VOI computation, tier graduation/demotion. Phase 3.
3. **Plugin/ingestion architecture** — how external data enters the ledger. Post-v1.
4. **Carbon methodology** — how to estimate per-operation carbon. Research needed.
5. **Simulation seeding strategy** — how random_seed is assigned for ensemble runs. Phase 3.
6. **Event retention policy** — how long events are kept, archival strategy. Post-v1.
7. **Alterverse branching** — how forked simulations relate to the main ledger. Phase 3.

---

## Implementation Impact on TASK-009

TASK-009 (Event Ledger v1) now has a richer schema but the same scope:

1. Create the table with all columns per Decision 1
2. Use universal entity IDs per Decision 2
3. Classify signal types per Decision 3 (best-effort, not mandatory)
4. Use flat domain taxonomy per Decision 4
5. DO NOT build entity_profiles table — only reference this ADR
6. Include all three cost columns per Decision 6

**Estimated effort change:** +1-2 hours over original estimate (schema is wider, but logic is the same).

---

## Approval

- [ ] Dave reviewed
- [ ] Schema validated against architecture session document
- [ ] TASK-009 updated in TASK-REGISTRY.md

---

*"The foundation remembers what the building forgets."*
