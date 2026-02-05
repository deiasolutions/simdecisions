# ADR-006: Hive Control Plane

**Status:** PROPOSED (Circulating for Review)
**Date:** 2026-02-05
**Author:** Q33N (Dave) + BEE-001
**Reviewers:** [Pending]

---

## Summary

A central coordination server that replaces (or supplements) file-based hive communication with real-time, API-driven orchestration. Provides task queuing, progress tracking, bee-to-bee messaging, human dashboards, and immutable audit logging.

---

## Context

### Current State

DEIA coordination uses file-based communication:

```
.deia/hive/
├── tasks/          ← Q33N drops work as .md files
├── responses/      ← Bees write response files
├── archive/        ← Completed tasks moved here
└── bot-logs/       ← Manual activity logging (JSONL)
```

### Problems

| Problem | Impact |
|---------|--------|
| Polling-based | Bees check files repeatedly; slow, wasteful |
| No real-time visibility | Human can't see what's happening now |
| Manual logging | PROCESS-0004 violations; compliance burden |
| Crash = lost context | No persistent state outside files |
| No bee-to-bee coordination | Bees can't ask each other for help |
| Tribunal is manual | No API for verdicts, approvals, feedback |

### Requirements

1. Real-time task assignment (push, not poll)
2. Automatic activity logging (compliance built-in)
3. Human dashboard for visibility
4. Bee-to-bee messaging with rate limits
5. Approval workflows via API
6. Immutable audit log
7. **File-based fallback must remain supported**

---

## Decision

Build a **Hive Control Plane** server with dual-mode communication:

- **Primary:** API + WebSocket (real-time)
- **Fallback:** File-based (existing `.deia/hive/` structure)

Bees can use either mode. The control plane syncs between them.

---

## Architecture

### High-Level

```
┌─────────────────────────────────────────────────────────────────┐
│                     HIVE CONTROL PLANE                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Task Queue   │  │ Message Bus  │  │ Audit Log    │          │
│  │ Service      │  │ Service      │  │ Service      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    ┌──────┴───────┐                             │
│                    │ Core API     │                             │
│                    │ (FastAPI)    │                             │
│                    └──────┬───────┘                             │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐          │
│  │ REST API     │  │ WebSocket    │  │ File Sync    │          │
│  │ /api/*       │  │ /ws          │  │ .deia/hive/  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │ LLM Bees │       │ PyBees   │       │ Legacy   │
   │ (API)    │       │ (API)    │       │ (Files)  │
   └──────────┘       └──────────┘       └──────────┘
```

### Infrastructure

| Layer | Platform | Notes |
|-------|----------|-------|
| Frontend | Vercel | Next.js dashboard |
| Backend | Railway | FastAPI + WebSocket |
| Database | Railway Postgres | Tasks, messages, audit |
| Auth | NextAuth.js | OAuth2, API keys for bots |
| Realtime | WebSocket | Push notifications |
| File Sync | Railway worker | Watches/writes `.deia/hive/` |

### Future: Federation (Phase 2+)

```
┌─────────────────┐     ┌─────────────────┐
│ Hive Control    │────▶│ Matrix Bridge   │────▶ Federation
│ Plane           │     │ (App Service)   │
└─────────────────┘     └─────────────────┘
```

Matrix bridge enables interop when needed. Core API unchanged.

---

## Data Model

### Tasks

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Identity
    task_ref VARCHAR(50) NOT NULL,          -- e.g., "TASK-009"
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- State machine: pending → claimed → in_progress → completed | failed
    status VARCHAR(20) DEFAULT 'pending',

    -- Assignment
    assigned_to VARCHAR(50),                 -- Bee ID
    claimed_at TIMESTAMPTZ,

    -- Completion
    completed_at TIMESTAMPTZ,
    outcome VARCHAR(20),                     -- 'success' | 'failure' | 'blocked'

    -- Provenance
    created_by VARCHAR(50) NOT NULL,         -- Q33N, another bee, etc.
    priority INT DEFAULT 0,
    tags VARCHAR[] DEFAULT '{}',

    -- File sync
    file_path VARCHAR(500),                  -- Path in .deia/hive/tasks/
    file_synced_at TIMESTAMPTZ
);
```

### Messages

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Addressing
    channel VARCHAR(100) NOT NULL,           -- 'general', 'task:TASK-009', 'bee:BEE-001'
    sender VARCHAR(50) NOT NULL,

    -- Content
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text', -- 'text' | 'progress' | 'request' | 'response'

    -- Threading
    reply_to UUID REFERENCES messages(id),

    -- Tags
    tags VARCHAR[] DEFAULT '{}',             -- #idea, #todo, #blocker, etc.

    -- Metadata
    metadata JSONB DEFAULT '{}'
);
```

### Audit Log

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW(),

    -- What happened
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(50) NOT NULL,

    -- Context
    entity_type VARCHAR(50),                 -- 'task', 'message', 'bee', etc.
    entity_id VARCHAR(100),

    -- Details
    details JSONB NOT NULL,

    -- Immutability
    hash VARCHAR(64)                         -- SHA-256 of previous row + this row
);

-- Append-only enforcement
CREATE TRIGGER prevent_update_audit
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'Audit log is append-only');
END;

CREATE TRIGGER prevent_delete_audit
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'Audit log is append-only');
END;
```

---

## API Design

### Authentication

| Method | Use Case |
|--------|----------|
| OAuth2 (NextAuth) | Human users via dashboard |
| API Key | Bees (scoped per bee, rate-limited) |
| Service Token | Internal services |

### Endpoints

#### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List tasks (filterable) |
| `POST` | `/api/tasks` | Create task |
| `GET` | `/api/tasks/{id}` | Get task details |
| `POST` | `/api/tasks/{id}/claim` | Claim task (bee) |
| `POST` | `/api/tasks/{id}/progress` | Log progress |
| `POST` | `/api/tasks/{id}/complete` | Mark complete |
| `POST` | `/api/tasks/{id}/release` | Release claim |

#### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/channels/{channel}/messages` | Get messages |
| `POST` | `/api/channels/{channel}/messages` | Send message |
| `GET` | `/api/messages/{id}` | Get single message |

#### WebSocket

```
ws://api.example.com/ws?token={api_key}

// Subscribe to channels
{ "action": "subscribe", "channel": "task:TASK-009" }

// Receive events
{ "event": "task.claimed", "task_id": "...", "bee": "BEE-001" }
{ "event": "message.new", "channel": "general", "message": {...} }
```

#### File Sync

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sync/pull` | Pull changes from files to DB |
| `POST` | `/api/sync/push` | Push changes from DB to files |
| `GET` | `/api/sync/status` | Sync status |

---

## Dual-Mode Communication

### Mode 1: API-First (Primary)

```
Bee                          Control Plane
 │                                │
 │  POST /api/tasks/{id}/claim    │
 │──────────────────────────────▶│
 │                                │──▶ Update DB
 │                                │──▶ Broadcast via WebSocket
 │                                │──▶ Write to .deia/hive/ (async)
 │  { "status": "claimed" }       │
 │◀──────────────────────────────│
```

### Mode 2: File-Based (Fallback)

```
Bee                          Control Plane
 │                                │
 │  Write to .deia/hive/          │
 │  responses/BEE-001-resp.md     │
 │                                │
 │                           [File watcher detects change]
 │                                │──▶ Parse file
 │                                │──▶ Update DB
 │                                │──▶ Broadcast via WebSocket
```

### Sync Rules

| Source | Target | Trigger |
|--------|--------|---------|
| API write | File system | Async (within 5s) |
| File write | Database | File watcher (within 5s) |
| Conflict | Last-write-wins | With audit log entry |

---

## Human Dashboard

### Views

| View | Purpose |
|------|---------|
| **Live Feed** | Real-time activity stream |
| **Task Board** | Kanban of task states |
| **Bee Status** | What each bee is doing now |
| **Audit Trail** | Searchable event history |
| **Cost Tracker** | Tokens, dollars, carbon |
| **Approvals** | Pending human decisions |

### Interactions

| Action | Effect |
|--------|--------|
| Create task | POST to API, bee notified |
| Send message | POST to channel, bees see it |
| Approve/reject | Update task, trigger webhook |
| Override | Bypass automation with audit |

---

## Security

### Authentication & Authorization

| Feature | Implementation |
|---------|----------------|
| Human login | OAuth2 via NextAuth (GitHub, Google) |
| Bee auth | API keys (scoped, rotatable) |
| RBAC | Roles: admin, human, bee, readonly |
| Rate limiting | Per-key, per-endpoint |

### Data Protection

| Feature | Implementation |
|---------|----------------|
| TLS | All traffic encrypted |
| At-rest encryption | Railway Postgres default |
| Secrets | Railway environment variables |
| API key storage | Hashed, never logged |

### Audit

| Event | Logged |
|-------|--------|
| All API calls | Yes (actor, endpoint, params) |
| All state changes | Yes (before/after) |
| Auth events | Yes (login, key use, failures) |
| File sync | Yes (direction, files, conflicts) |

---

## DEIA Special Sauce

### Work Queues as First-Class Objects

Tasks have a state machine enforced by the API:

```
pending ──▶ claimed ──▶ in_progress ──▶ completed
    │           │              │              │
    │           ▼              ▼              ▼
    │       released       blocked        failed
    │           │              │
    └───────────┴──────────────┘
              (back to pending)
```

### Bot-to-Bot Messaging

- Bees can message channels or direct to other bees
- Rate limits prevent spam (e.g., 10 msg/min per bee)
- Circuit breaker: if a bee sends too fast, paused for cooldown
- Quotas: daily message limits per bee

### Moderator Workflows

- Tasks can require human approval at state transitions
- Approval requests appear in dashboard
- Timeout: if human doesn't respond in X hours, escalate or auto-decide

### Event Streaming

- Webhooks for external systems (GitHub, Discord, G-Drive)
- Events: `task.created`, `task.completed`, `message.new`, `approval.needed`
- Retry with exponential backoff

---

## File-Based Fallback Details

### Why Keep It?

| Reason | Explanation |
|--------|-------------|
| Resilience | Server down? Bees can still work via files |
| Debugging | Files are human-readable, git-friendly |
| Onboarding | New bees don't need API integration immediately |
| Simplicity | Some use cases don't need real-time |

### File Structure (Unchanged)

```
.deia/hive/
├── tasks/
│   ├── YYYY-MM-DD-HHMM-Q33N-{bee}-TASK-{id}.md
│   └── _archive/
├── responses/
│   └── YYYY-MM-DD-HHMM-{bee}-Q33N-RESPONSE-{id}.md
└── bot-logs/
    └── {BEE-ID}-activity.jsonl
```

### Sync Behavior

| Scenario | Behavior |
|----------|----------|
| Task created via API | File written to `tasks/` |
| Task file created manually | Parsed, added to DB |
| Response file written | Parsed, logged to audit |
| Conflict (both modified) | Last-write-wins, conflict logged |

---

## Implementation Phases

### Phase 1: Core API (MVP)

- [ ] Railway project setup
- [ ] Postgres schema (tasks, messages, audit)
- [ ] FastAPI with task endpoints
- [ ] API key auth for bees
- [ ] Basic WebSocket for push
- [ ] File sync worker (one-way: API → files)

**Outcome:** Bees can use API, files still written for backup.

### Phase 2: Dashboard

- [ ] Vercel Next.js project
- [ ] NextAuth integration
- [ ] Live feed view
- [ ] Task board view
- [ ] Bee status view

**Outcome:** Humans have visibility.

### Phase 3: Full Dual-Mode

- [ ] File watcher (files → DB sync)
- [ ] Conflict resolution
- [ ] Bidirectional sync tests

**Outcome:** File-based bees work seamlessly.

### Phase 4: Advanced Features

- [ ] Approval workflows
- [ ] Bot-to-bot messaging with quotas
- [ ] Webhooks (GitHub, Discord)
- [ ] Cost tracking integration

**Outcome:** Full DEIA special sauce.

### Phase 5: Federation (Future)

- [ ] Matrix bridge evaluation
- [ ] Event format alignment
- [ ] Federation pilot

**Outcome:** Interop with external systems.

---

## Open Questions

1. **Sync frequency:** 5s acceptable? Or need sub-second?
2. **Conflict resolution:** Last-write-wins OK? Or need merge logic?
3. **File watcher deployment:** Same Railway service or separate?
4. **API versioning:** `/api/v1/` from start?
5. **Multi-tenant:** Single hive or workspace isolation now?

---

## References

- `specs/dave/inputs/2026-02-05-PLATFORM-ARCHITECTURE-PATHS.md` — Original input
- `specs/ADR-004-GDrive-Coordination-Layer.md` — G-Drive integration
- `specs/ADR-005-Dual-Publish-Knowledge.md` — Dual-publish pattern
- `.deia/hive-coordination-rules.md` — Current file-based rules
- `specs/hive_comms_spec.md` — Scribe input contract

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-02-05 | Initial draft for review |

---

*"Real-time when you can, files when you must."*
