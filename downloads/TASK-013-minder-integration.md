# TASK-013: Minder Integration

## Status: PENDING
## Assignee: BEE-001
## Effort: 1-2 hours
## Priority: P1

---

## Objective

Integrate minder with server startup so it runs automatically.

---

## Problem

`runtime/minder.py` exists but is standalone — must be run manually via `python -m deia_raqcoon.runtime.minder`. Should auto-start when server launches.

---

## Solution

### 1. Update `runtime/minder.py`

Add async version:

```python
import asyncio
import httpx
from datetime import datetime

async def minder_loop(
    api_base: str = "http://127.0.0.1:8010",
    channel_id: str = "system",
    interval_seconds: int = 300,
    author: str = "minder"
):
    """Async minder loop for integration with server."""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.post(
                    f"{api_base}/api/messages",
                    json={
                        "channel_id": channel_id,
                        "author": author,
                        "content": f"minder ping at {datetime.utcnow().isoformat()}Z",
                        "lane": "system",
                        "provider": "minder"
                    },
                    timeout=10.0
                )
            except Exception as e:
                print(f"Minder ping failed: {e}")
            
            await asyncio.sleep(interval_seconds)
```

### 2. Update `runtime/server.py`

Add lifespan context manager:

```python
from contextlib import asynccontextmanager
import asyncio

_minder_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global _minder_task
    
    # Start minder on startup
    from runtime.minder import minder_loop
    _minder_task = asyncio.create_task(minder_loop(interval_seconds=300))
    
    yield
    
    # Cancel minder on shutdown
    if _minder_task:
        _minder_task.cancel()
        try:
            await _minder_task
        except asyncio.CancelledError:
            pass

# Update app initialization
app = FastAPI(lifespan=lifespan)
```

### 3. Add config endpoint

```python
@app.post("/api/minder/config")
def configure_minder(interval: int = 300, enabled: bool = True) -> Dict:
    """Configure minder settings."""
    # Store in module-level config
    global _minder_config
    _minder_config = {"interval": interval, "enabled": enabled}
    return {"status": "configured", "interval": interval, "enabled": enabled}
```

---

## Dependencies

Add to requirements:
```
httpx>=0.25.0
```

---

## Test

```bash
# Start server
python run_server.py

# Wait 5 minutes, check messages
curl http://localhost:8010/api/messages?channel_id=system

# Should see minder pings
```

---

## Done When

- [ ] Minder starts automatically with server
- [ ] Pings appear in system channel
- [ ] Minder stops cleanly on server shutdown
- [ ] No manual process needed
