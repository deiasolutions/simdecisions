# TASK-018: PTY Auto-Cleanup

## Status: PENDING
## Assignee: BEE-001
## Effort: 1-2 hours
## Priority: P2

---

## Objective

Auto-cleanup PTY sessions that disconnect without explicit stop.

---

## Problem

From BEE3 audit:
> Sessions are cleaned up when `stop()` is called explicitly. But if client disconnects without calling stop, session stays in memory with `alive=False`.

---

## Solution

### 1. Update `runtime/pty_bridge.py`

Add cleanup loop and TTL:

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict

SESSION_TTL_SECONDS = 300  # 5 minutes inactive = cleanup

@dataclass
class PTYSession:
    session_id: str
    process: PtyProcess
    buffer: str
    lock: threading.Lock
    alive: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def touch(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def is_stale(self, ttl_seconds: int = SESSION_TTL_SECONDS) -> bool:
        """Check if session is stale."""
        if self.alive:
            return False
        return datetime.utcnow() - self.last_activity > timedelta(seconds=ttl_seconds)


class PTYBridge:
    def __init__(self):
        self.sessions: Dict[str, PTYSession] = {}
        self._cleanup_task = None
    
    def start_cleanup_loop(self):
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Periodically cleanup stale sessions."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            self._cleanup_stale_sessions()
    
    def _cleanup_stale_sessions(self):
        """Remove stale sessions."""
        stale = [sid for sid, session in self.sessions.items() 
                 if session.is_stale()]
        
        for sid in stale:
            session = self.sessions.pop(sid, None)
            if session and session.process:
                try:
                    session.process.terminate()
                except:
                    pass
            
            # Log cleanup
            from runtime.ledger import log_event
            log_event("pty_session_cleaned", data={
                "session_id": sid,
                "reason": "stale"
            })
    
    def send(self, session_id: str, data: str) -> bool:
        """Send data to PTY (updates activity)."""
        session = self.sessions.get(session_id)
        if not session or not session.alive:
            return False
        
        session.touch()  # Update activity
        session.process.write(data)
        return True
    
    def read(self, session_id: str, max_chars: int = 4000) -> str:
        """Read from PTY (updates activity)."""
        session = self.sessions.get(session_id)
        if not session:
            return ""
        
        session.touch()  # Update activity
        return session.read_buffer(max_chars)
    
    def stop(self, session_id: str) -> bool:
        """Stop PTY session explicitly."""
        session = self.sessions.pop(session_id, None)
        if not session:
            return False
        
        session.alive = False
        if session.process:
            try:
                session.process.terminate()
            except:
                pass
        
        from runtime.ledger import log_event
        log_event("pty_session_stopped", data={"session_id": session_id})
        
        return True
    
    def get_stats(self) -> Dict:
        """Get session statistics."""
        return {
            "total_sessions": len(self.sessions),
            "active": sum(1 for s in self.sessions.values() if s.alive),
            "stale": sum(1 for s in self.sessions.values() if s.is_stale()),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "alive": s.alive,
                    "age_seconds": (datetime.utcnow() - s.created_at).total_seconds(),
                    "idle_seconds": (datetime.utcnow() - s.last_activity).total_seconds()
                }
                for s in self.sessions.values()
            ]
        }
```

### 2. Update `server.py`

Start cleanup loop on startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start PTY cleanup loop
    _pty_bridge.start_cleanup_loop()
    
    # Start minder
    # ... existing minder code ...
    
    yield
    
    # Cleanup all PTY sessions on shutdown
    for session_id in list(_pty_bridge.sessions.keys()):
        _pty_bridge.stop(session_id)
```

### 3. Add stats endpoint

```python
@app.get("/api/pty/stats")
def get_pty_stats() -> Dict:
    """Get PTY session statistics."""
    return _pty_bridge.get_stats()
```

---

## Test

```bash
# Start a PTY session
curl -X POST http://localhost:8010/api/pty/start \
  -H "Content-Type: application/json" \
  -d '{"tool": "claude-code", "repo_root": "."}'

# Get stats
curl http://localhost:8010/api/pty/stats

# Wait 5+ minutes without activity, check stats again
# Session should be marked stale and cleaned up
```

---

## Done When

- [ ] Sessions track `last_activity` timestamp
- [ ] `is_stale()` method detects inactive sessions
- [ ] Background cleanup loop runs every 60s
- [ ] Stale sessions auto-terminated after 5 min
- [ ] `GET /api/pty/stats` shows session health
- [ ] Cleanup events logged via ledger
