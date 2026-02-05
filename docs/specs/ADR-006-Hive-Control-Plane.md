# ADR-006: Hive Control Plane

**Status:** PROPOSED (Circulating for Review)
**Date:** 2026-02-05
**Author:** Q33N (Dave) + BEE-001
**Reviewers:** [Pending]

---

## Summary

A central coordination server designed to seamlessly integrate **both real-time, API-driven orchestration AND robust file-driven communication** for the hive. File-based interactions are a **first-class citizen** alongside the API + WebSocket interface. Provides task queuing, progress tracking, bee-to-bee messaging, human dashboards, and immutable audit logging — ensuring all bees can communicate effectively via their preferred method.

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
7. **File-based communication as first-class mode**

---

## Decision

Build a **Hive Control Plane** server with **first-class support for both communication modes**:

- **API-Driven:** Real-time orchestration via REST API + WebSocket
- **File-Driven:** Communication via direct manipulation of `.deia/hive/` files

Both modes are equal peers. Bees choose their preferred method. The control plane ensures seamless, bidirectional synchronization and maintains unified state across both paradigms.

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

## Communication Modes: API-Driven and File-Driven

### API-Driven Communication

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

### File-Driven Communication

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
| Conflict | **LLM Conflict Resolver** | See below |

---

## LLM Conflict Resolution

When both API and file writes occur within the sync window, an LLM resolves the conflict intelligently rather than blindly choosing "last write wins."

### Conflict Resolution Flow

```
Conflict detected (API + file both changed within sync window)
                    │
                    ▼
           ┌───────────────────┐
           │ Auto-Resolvable?  │
           │                   │
           │ - Identical?      │──▶ Yes ──▶ No conflict
           │ - Superset?       │──▶ Yes ──▶ Take superset
           │ - Disjoint fields?│──▶ Yes ──▶ Auto-merge
           └─────────┬─────────┘
                     │ No
                     ▼
         ┌─────────────────────┐
         │ LLM Conflict Resolver│
         │                      │
         │ Inputs:              │
         │ - Version A (API)    │
         │ - Version B (file)   │
         │ - Entity schema      │
         │ - Relevant specs     │
         │ - Process rules      │
         └──────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Merge   │ │ Pick A  │ │ Escalate│
   │ (smart) │ │ or B    │ │ (human) │
   └─────────┘ └─────────┘ └─────────┘
```

### Resolution Strategies

| Scenario | Resolution | Method |
|----------|------------|--------|
| Identical content | No conflict | Auto |
| One is strict superset | Take superset | Auto |
| Different fields changed | Merge both | Auto |
| Same field, different values | LLM decides | LLM |
| Semantic conflict detected | LLM analyzes | LLM |
| Violation detected | Escalate | Human |
| LLM returns "uncertain" | Escalate | Human |
| Critical entity (task, permissions) | Escalate | Human |

### Violation Checking

The LLM checks for process and spec violations:

```yaml
conflict_resolution:
  version_a: { status: "in_progress", assigned_to: "BEE-001" }
  version_b: { status: "completed", assigned_to: "BEE-002" }

  llm_analysis:
    conflict_type: "state_and_assignment"
    violations_detected:
      - rule: "PROCESS-0002"
        detail: "Task claimed by BEE-001 but BEE-002 attempting completion"
    resolution: "escalate"
    reason: "Potential task ownership violation - human review required"
```

### Model Selection

| Tier | Model | Use Case |
|------|-------|----------|
| **Local (preferred)** | Ollama (Llama 3, Mistral, etc.) | Cost-free, private, low-latency |
| **Cloud (fallback)** | Claude Haiku / GPT-4o-mini | When local unavailable or complex |
| **Escalation** | Human | When LLM uncertain or violation detected |

### Ollama Integration

```python
# Conflict resolver with Ollama preference
class ConflictResolver:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.fallback_model = "claude-3-haiku"  # Cloud fallback

    async def resolve(self, version_a: dict, version_b: dict, context: dict) -> Resolution:
        # Try auto-resolution first
        auto = self.try_auto_resolve(version_a, version_b)
        if auto:
            return auto

        # Try Ollama (local, free)
        try:
            return await self.resolve_with_ollama(version_a, version_b, context)
        except OllamaUnavailable:
            # Fall back to cloud
            return await self.resolve_with_cloud(version_a, version_b, context)

    async def resolve_with_ollama(self, a, b, ctx) -> Resolution:
        prompt = self.build_conflict_prompt(a, b, ctx)
        response = await ollama.chat(
            model=self.ollama_model,
            messages=[{"role": "user", "content": prompt}]
        )
        return self.parse_resolution(response)
```

### Configuration

```yaml
# config/conflict_resolution.yaml
conflict_resolution:
  enabled: true

  auto_resolve:
    identical: true
    superset: true
    disjoint_fields: true

  llm:
    primary: "ollama"
    fallback: "claude-haiku"

  ollama:
    url: "${OLLAMA_URL:-http://localhost:11434}"
    model: "${OLLAMA_MODEL:-llama3}"
    timeout_seconds: 30

  # Explicit escalation triggers (no arbitrary confidence %)
  escalate_to_human_when:
    - violation_detected: true        # Any spec/process violation found
    - llm_resolution: "uncertain"     # LLM explicitly says it can't decide
    - conflict_type: "semantic"       # Same field, ambiguous meaning
    - entity_type_in:                 # Critical entities always escalate
        - "task"
        - "permission"
        - "api_key"
        - "audit_entry"

  notify_channel: "#conflicts"
```

### Audit Trail

All conflict resolutions are logged:

```sql
INSERT INTO audit_log (event_type, actor, entity_type, entity_id, details)
VALUES (
    'conflict_resolved',
    'system:conflict_resolver',
    'task',
    'task-uuid-here',
    '{
        "version_a": {...},
        "version_b": {...},
        "resolution": "merge",
        "resolution_method": "llm",
        "model_used": "ollama:llama3",
        "escalation_triggers_checked": {
            "violation_detected": false,
            "llm_uncertain": false,
            "semantic_conflict": false,
            "critical_entity": false
        },
        "violations_checked": ["PROCESS-0002", "PROCESS-0004"],
        "violations_found": []
    }'
);
```

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
| Bee auth | API keys (scoped, rotatable, revocable) |
| RBAC | Roles: admin, human, bee, readonly |
| Rate limiting | Per-key, per-endpoint |

### API Key Management

| Operation | Endpoint | Who Can |
|-----------|----------|---------|
| Generate key | `POST /api/keys` | Admin |
| List keys | `GET /api/keys` | Admin |
| Rotate key | `POST /api/keys/{id}/rotate` | Admin, Key owner |
| Revoke key | `DELETE /api/keys/{id}` | Admin |
| View key metadata | `GET /api/keys/{id}` | Admin, Key owner |

**Key properties:**
- Scoped to specific bee ID
- Optional expiration date
- Optional IP allowlist
- Usage tracked (last used, call count)
- Hashed in database (plaintext shown once on creation)

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

## File-Driven Communication Details

### Rationale for File-Driven as Primary Mode

| Reason | Explanation |
|--------|-------------|
| **Resilience** | Control Plane down? Bees continue working via files |
| **Git-native** | Files are version-controlled, diffable, reviewable |
| **CLI-friendly** | Agents can use standard file tools (cat, echo, etc.) |
| **Debuggable** | Human-readable, no special tools needed |
| **Onboarding** | New bees don't need API integration immediately |
| **Local-first** | Works offline, syncs when connected |

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
| Conflict (both modified) | **LLM Conflict Resolver** decides (see above) |

### Migration of Existing Files

On initial deployment, existing `.deia/hive/` files are ingested:

1. Scan all task files → create DB records
2. Scan all response files → create DB records + audit entries
3. Scan bot-logs → import into audit_log
4. Mark migration complete in DB
5. Enable bidirectional sync

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

## Resolved Questions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Sync frequency | 5s for file-sync; API is real-time | File-sync doesn't need sub-second; API handles real-time |
| Conflict resolution | **LLM Conflict Resolver** (Ollama preferred) | Smarter than last-write-wins; checks for violations |
| File watcher deployment | **Separate Railway worker** | Better resilience, resource isolation |
| API versioning | **Yes, `/api/v1/` from start** | Standard practice, easier to evolve |
| Multi-tenant | Design for it (add `workspace_id`) | Easier to add now than retrofit later |

---

## Open Questions

1. **Ollama model selection:** Which model for conflict resolution? (Llama 3, Mistral, CodeLlama?)
2. **Rollback strategy:** How to recover from bad sync state?

---

## References

- `specs/dave/inputs/2026-02-05-PLATFORM-ARCHITECTURE-PATHS.md` — Original input
- `specs/ADR-004-GDrive-Coordination-Layer.md` — G-Drive integration
- `specs/ADR-005-Dual-Publish-Knowledge.md` — Dual-publish pattern
- `specs/ADR-006-Hive-Control-Plane_feedback_gemini.md` — Gemini review feedback
- `.deia/hive-coordination-rules.md` — Current file-based rules
- `specs/hive_comms_spec.md` — Scribe input contract

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.2.1 | 2026-02-05 | Replaced arbitrary 80% confidence threshold with explicit escalation triggers |
| 0.2.0 | 2026-02-05 | Applied Gemini feedback: file-driven as first-class, LLM conflict resolution with Ollama, resolved open questions |
| 0.1.0 | 2026-02-05 | Initial draft for review |

---

*"Real-time when you can, files when you must. Smart merge when they collide."*
