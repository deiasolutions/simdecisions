# TASK-009: Event Ledger

## Status: PENDING
## Assignee: BEE-001
## Effort: 4-6 hours
## Priority: P0

---

## Objective

Create append-only event log capturing every significant action.

---

## Create `runtime/ledger.py`

```python
from pathlib import Path
from datetime import datetime
import json

EVENTS_DIR = Path(".deia/events")

def _ensure_dir():
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

def log_event(event: str, task_id: str = None, bot_id: str = None, data: dict = None):
    """Append event to daily JSONL file."""
    _ensure_dir()
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    filepath = EVENTS_DIR / f"{today}.jsonl"
    
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "task_id": task_id,
        "bot_id": bot_id,
        "data": data or {}
    }
    
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return record  # Return for WebSocket broadcast

def read_events(date: str = None, limit: int = 100) -> list:
    """Read events for a date (default: today)."""
    _ensure_dir()
    
    if date is None:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    
    filepath = EVENTS_DIR / f"{date}.jsonl"
    
    if not filepath.exists():
        return []
    
    events = []
    with open(filepath, "r") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    
    return events[-limit:] if limit else events
```

---

## Wire into `server.py`

```python
from runtime.ledger import log_event, read_events

# In create_task():
log_event("task_created", task_id=task_id, bot_id=request.bot_id, 
          data={"intent": request.intent, "title": request.title})

# After routing:
log_event("task_routed", task_id=task_id, 
          data={"lane": routing.lane, "provider": routing.provider})

# In complete_task_endpoint():
log_event("task_completed", task_id=task_id, 
          data={"path": str(archive_path)})

# In start_flight() / end_flight():
log_event("flight_started", data={"flight_id": request.flight_id})
log_event("flight_ended", data={"flight_id": request.flight_id})
```

---

## Add endpoint

```python
@app.get("/api/events")
def get_events(date: str = None, limit: int = 100) -> Dict:
    events = read_events(date, limit)
    return {
        "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
        "count": len(events),
        "events": events
    }
```

---

## Event Types

| Event | When |
|-------|------|
| `task_created` | Task POST |
| `task_routed` | After routing |
| `kb_injected` | After KB lookup |
| `task_completed` | Task archived |
| `gate_checked` | Any gate check |
| `flight_started` | Flight begins |
| `flight_ended` | Flight ends |

---

## Done When

- [ ] `runtime/ledger.py` exists
- [ ] Events logged on task create/complete
- [ ] Events logged on flight start/end
- [ ] `GET /api/events` returns events
- [ ] JSONL files in `.deia/events/`
