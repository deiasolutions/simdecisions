# ADR-002: API Endpoint Registry

**Status:** PROPOSED — awaiting Dave's review
**Date:** 2026-02-04
**Context:** SimDecisions Architecture — Canonical endpoint reference
**Scope:** All API endpoints for v1, authentication model, request/response schemas

---

## Why This ADR Exists

Multiple specs reference API endpoints without a single source of truth. TASK-009 adds event ledger endpoints; TASK-010 adds cost endpoints; TASK-011 expects them to exist. Without a registry, implementations diverge.

This ADR establishes the canonical list of all endpoints, their purposes, authentication requirements, and schemas.

---

## Authentication Model (v1)

**v1 is single-user, local-first.** No authentication required for MVP.

| Phase | Auth Model |
|-------|------------|
| v1 (MVP) | None — localhost only |
| v1.1 | API key (single user) |
| v2+ | OAuth2 / JWT (multi-user) |

All endpoints below assume no auth for v1. Auth header requirements will be added when auth ships.

---

## Endpoint Registry

### Core System

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/health` | Health check | Exists |
| GET | `/api/summary` | System summary (tasks, flights, costs) | Exists |
| GET | `/api/config` | Current configuration | Exists |
| POST | `/api/config` | Update configuration | Exists |

### Tasks

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/tasks` | List all tasks | Exists |
| GET | `/api/tasks/{task_id}` | Get single task | Exists |
| POST | `/api/tasks` | Create new task | Exists |
| PUT | `/api/tasks/{task_id}` | Update task | Exists |
| DELETE | `/api/tasks/{task_id}` | Delete task | Exists |
| POST | `/api/tasks/{task_id}/claim` | Claim task for execution | Exists |
| POST | `/api/tasks/{task_id}/complete` | Mark task complete | Exists |

### Flights

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/flights` | List all flights | Exists |
| GET | `/api/flights/{flight_id}` | Get single flight | Exists |
| POST | `/api/flights` | Start new flight | Exists |
| POST | `/api/flights/{flight_id}/end` | End flight | Exists |

### Event Ledger (TASK-009)

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/events` | Query events with filters | Phase 2 |
| POST | `/api/events` | Record new event (internal) | Phase 2 |
| GET | `/api/events/export` | Export events (JSON/CSV) | Phase 2 |

**Query Parameters for GET /api/events:**

| Param | Type | Description |
|-------|------|-------------|
| `event_type` | string | Filter by event type |
| `actor` | string | Filter by actor (universal entity ID) |
| `target` | string | Filter by target |
| `domain` | string | Filter by domain |
| `signal_type` | string | Filter by signal_type (gravity/light/internal) |
| `oracle_tier` | int | Filter by oracle tier (0-4) |
| `start` | datetime | Start of time range |
| `end` | datetime | End of time range |
| `limit` | int | Max results (default 100) |
| `offset` | int | Pagination offset |

**Request Body for POST /api/events:**

```json
{
  "event_type": "task_created",
  "actor": "human:dave",
  "target": "task:TASK-009",
  "domain": "coding",
  "signal_type": "gravity",
  "oracle_tier": null,
  "random_seed": null,
  "completion_promise": null,
  "verification_method": null,
  "payload_json": {"description": "Event ledger implementation"},
  "cost_tokens": null,
  "cost_usd": null,
  "cost_carbon": null
}
```

### Cost Tracking (TASK-010)

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/costs` | Aggregated cost data | Phase 2 |
| GET | `/api/costs/export` | Export costs (JSON/CSV) | Phase 2 |

**Query Parameters for GET /api/costs:**

| Param | Type | Description |
|-------|------|-------------|
| `group_by` | string | Aggregation: task, agent, flight, domain, oracle_tier |
| `start` | datetime | Start of time range |
| `end` | datetime | End of time range |

**Response Schema:**

```json
{
  "group_by": "agent",
  "start": "2026-02-01T00:00:00Z",
  "end": "2026-02-04T23:59:59Z",
  "aggregations": [
    {
      "key": "agent:BEE-001",
      "cost_tokens": 147832,
      "cost_usd": 2.96,
      "cost_carbon": null,
      "event_count": 47
    }
  ],
  "totals": {
    "cost_tokens": 312847,
    "cost_usd": 6.26,
    "cost_carbon": null
  }
}
```

### Gates

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/gates` | Get all gate states | Exists |
| PUT | `/api/gates/{gate_name}` | Update gate state | Exists |

### Knowledge Base

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/kb/patterns` | List BOK patterns | Exists |
| GET | `/api/kb/patterns/{id}` | Get single pattern | Exists |
| POST | `/api/kb/inject` | Inject KB content into task | Exists |

### WebSocket

| Path | Purpose | Phase |
|------|---------|-------|
| `/ws` | Real-time event stream | Exists |

**WebSocket Message Types:**

| Type | Direction | Purpose |
|------|-----------|---------|
| `task_created` | Server→Client | New task created |
| `task_updated` | Server→Client | Task state changed |
| `task_completed` | Server→Client | Task finished |
| `flight_started` | Server→Client | Flight began |
| `flight_ended` | Server→Client | Flight ended |
| `gate_changed` | Server→Client | Gate state toggled |
| `event_recorded` | Server→Client | New event in ledger |
| `cost_update` | Server→Client | Cost totals changed |

---

## Response Formats

### Success Response

```json
{
  "status": "ok",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id 'TASK-999' not found"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | State conflict (e.g., task already claimed) |
| `GATE_BLOCKED` | 403 | Operation blocked by gate |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Future Endpoints (Post-v1)

| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
| GET | `/api/entities` | List entity profiles | Phase 3 |
| GET | `/api/entities/{id}/vectors` | Get entity's α,σ,π,ρ vectors | Phase 3 |
| POST | `/api/simulation/checkpoint` | Save simulation state | Phase 3 |
| POST | `/api/simulation/branch` | Fork simulation | Phase 3 |
| GET | `/api/prophecies` | List generated prophecies | Phase 3+ |
| GET | `/api/voi` | Value of Information report | Phase 3+ |

---

## Implementation Notes

1. All timestamps are ISO 8601 UTC
2. Universal entity IDs per ADR-003
3. Event ledger is append-only — no PUT/DELETE on `/api/events`
4. Export endpoints support `?format=json` (default) or `?format=csv`

---

## Approval

- [ ] Dave reviewed
- [ ] Endpoint list validated against existing code
- [ ] TASK-009/010/011 updated to reference this ADR

---

*"The API is the contract."*
