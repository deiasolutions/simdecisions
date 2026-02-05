# ADR-003: Entity ID Convention

**Status:** PROPOSED — awaiting Dave's review
**Date:** 2026-02-04
**Context:** SimDecisions Architecture — Universal entity identification
**Scope:** ID format for all actors, targets, and entities in the system

---

## Why This ADR Exists

The four-vector entity model (α,σ,π,ρ) profiles ANY entity — human, AI, team, machine, process. The event ledger must record WHO did WHAT without special-casing entity types.

Legacy code uses `bot_id` for AI agents. This breaks when:
- A human performs an action (no `bot_id`)
- A team owns a task (not a single bot)
- A system process triggers an event (not user-initiated)
- Future entity types emerge (IoT devices, external APIs)

This ADR establishes a universal entity ID scheme that handles all cases.

---

## Decision: Universal Entity IDs

All entities use the format:

```
{type}:{identifier}
```

### Type Prefixes

| Prefix | Entity Type | Example |
|--------|-------------|---------|
| `agent` | AI agent (bee, queen, any LLM-powered actor) | `agent:BEE-001` |
| `human` | Human user | `human:dave` |
| `team` | Team or group | `team:frontend` |
| `process` | Automated process or pipeline | `process:deploy-pipeline` |
| `system` | Internal system service | `system:minder` |
| `task` | Task entity | `task:TASK-009` |
| `flight` | Flight entity | `flight:FLT-20260204-001` |
| `gate` | Gate entity | `gate:allow_q33n_git` |
| `kb` | Knowledge base entity | `kb:BOK-SIM-001` |
| `org` | Organization | `org:deiasolutions` |
| `external` | External system or API | `external:github-api` |

### Identifier Rules

1. **Alphanumeric + hyphens + underscores:** `[a-zA-Z0-9_-]+`
2. **Case-sensitive:** `agent:BEE-001` ≠ `agent:bee-001`
3. **No colons in identifier:** The colon is the type separator
4. **No spaces:** Use hyphens or underscores
5. **Max length:** 128 characters total (type + colon + identifier)

### Valid Examples

```
agent:BEE-001
agent:Q33N-001
human:dave
human:daaaave-atx
team:backend-engineering
process:nightly-backup
system:gate-check
system:minder
task:TASK-009
flight:FLT-20260204-001
gate:allow_flight_commits
kb:BOK-SIM-001
org:deiasolutions
external:anthropic-api
```

### Invalid Examples

```
BEE-001              # Missing type prefix
agent:BEE:001        # Colon in identifier
agent:BEE 001        # Space in identifier
agent:               # Empty identifier
:BEE-001             # Empty type
```

---

## Event Ledger Usage

In the event ledger (ADR-001), the `actor` and `target` fields use universal entity IDs:

```sql
-- Example events
INSERT INTO events (event_type, actor, target, domain, signal_type)
VALUES
  ('task_created', 'human:dave', 'task:TASK-009', 'coding', 'gravity'),
  ('task_claimed', 'agent:BEE-001', 'task:TASK-009', 'coding', 'gravity'),
  ('kb_injected', 'system:router', 'task:TASK-009', 'kb', 'internal'),
  ('gate_checked', 'system:gate-check', 'gate:allow_q33n_git', 'gate', 'gravity'),
  ('task_completed', 'agent:BEE-001', 'task:TASK-009', 'coding', 'gravity');
```

---

## Entity Profile Usage

In the entity_profiles table (ADR-001, Decision 5), the `entity_id` uses the same scheme:

```sql
-- Example profiles
INSERT INTO entity_profiles (entity_id, domain, vector_type, value, measured_at)
VALUES
  ('agent:BEE-001', 'coding', 'sigma', 0.85, '2026-02-04T15:00:00Z'),
  ('agent:BEE-001', 'design', 'sigma', 0.42, '2026-02-04T15:00:00Z'),
  ('human:dave', 'review', 'sigma', 0.95, '2026-02-04T15:00:00Z'),
  ('team:backend', 'coding', 'sigma', 0.78, '2026-02-04T15:00:00Z');
```

---

## Migration from bot_id

### Current State

Legacy code uses `bot_id` in:
- Task file YAML (`assigned_to: BOT-001`)
- Some API endpoints (`/api/bots/{bot_id}`)
- Internal references

### Migration Strategy

| Context | Action |
|---------|--------|
| Task file `assigned_to` | Keep as-is. This is assignment notation, not event logging. |
| Event ledger `actor`/`target` | Always use universal ID: `agent:BOT-001` |
| API endpoints | Gradual migration. New endpoints use universal IDs. |
| Internal code | Map at boundary: `bot_id_to_entity_id(bot_id)` → `agent:{bot_id}` |

### Mapping Function

```python
def bot_id_to_entity_id(bot_id: str) -> str:
    """Convert legacy bot_id to universal entity ID."""
    # Strip any existing prefix
    if bot_id.startswith("BOT-") or bot_id.startswith("BEE-"):
        return f"agent:{bot_id}"
    if bot_id.startswith("Q33N"):
        return f"agent:{bot_id}"
    # Default: assume it's an agent
    return f"agent:{bot_id}"

def entity_id_to_bot_id(entity_id: str) -> str | None:
    """Extract bot_id from universal entity ID, if applicable."""
    if entity_id.startswith("agent:"):
        return entity_id[6:]  # Remove "agent:" prefix
    return None  # Not a bot
```

---

## Querying by Entity Type

Universal IDs enable type-based queries:

```sql
-- All events by AI agents
SELECT * FROM events WHERE actor LIKE 'agent:%';

-- All events by humans
SELECT * FROM events WHERE actor LIKE 'human:%';

-- All events targeting tasks
SELECT * FROM events WHERE target LIKE 'task:%';

-- Events where system acted
SELECT * FROM events WHERE actor LIKE 'system:%';
```

---

## Entity Resolution

For display and reporting, entity IDs can be resolved to human-readable names:

| Entity ID | Display Name |
|-----------|--------------|
| `agent:BEE-001` | BEE-001 |
| `human:dave` | Dave |
| `team:frontend` | Frontend Team |
| `system:minder` | Minder Service |
| `task:TASK-009` | TASK-009: Event Ledger |

Resolution is a UI/reporting concern, not a storage concern. The event ledger stores the ID; display layers resolve it.

---

## Special Entity IDs

| Entity ID | Purpose |
|-----------|---------|
| `system:unknown` | Actor could not be determined |
| `system:bootstrap` | System initialization events |
| `system:migration` | Data migration events |
| `human:anonymous` | Unauthenticated user (post-v1) |

---

## Validation

Entity ID validation function:

```python
import re

ENTITY_ID_PATTERN = re.compile(r'^[a-z]+:[a-zA-Z0-9_-]+$')

VALID_TYPES = {
    'agent', 'human', 'team', 'process', 'system',
    'task', 'flight', 'gate', 'kb', 'org', 'external'
}

def validate_entity_id(entity_id: str) -> bool:
    """Validate universal entity ID format."""
    if not entity_id or len(entity_id) > 128:
        return False
    if not ENTITY_ID_PATTERN.match(entity_id):
        return False
    type_prefix = entity_id.split(':')[0]
    return type_prefix in VALID_TYPES
```

---

## Approval

- [ ] Dave reviewed
- [ ] ADR-001 updated to reference this convention
- [ ] Migration plan validated against existing codebase

---

*"One ID scheme to identify them all."*
