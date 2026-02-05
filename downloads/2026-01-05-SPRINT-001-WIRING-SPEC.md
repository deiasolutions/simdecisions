# SPRINT-001: RAQCOON Integration Wiring

**Sprint ID:** SPRINT-001
**Created:** 2026-01-05
**Target Duration:** 1 day (8 working hours)
**Goal:** Connect existing but disconnected components to achieve functional MVP

---

## 1. Sprint Overview

### 1.1 Problem Statement
BEE3 Gap Analysis identified that core orchestration logic exists but isn't wired into the main request flow. The router, KB injection, WebSocket, and minder are all implemented but disconnected.

### 1.2 Success Criteria
- Tasks are routed by intent using `decide_route()`
- KB entities are injected into task payloads (not just IDs stored)
- WebSocket broadcasts messages to connected clients
- Minder runs automatically when server starts
- All 3 gate flags are enforced on git operations

### 1.3 Out of Scope
- New endpoints (Phase 1-2 spec intake)
- UI changes
- New KB entity types
- Schema changes to task_file.json

---

## 2. Hive Structure

### 2.1 Q33N (Queen Bee) — Orchestrator

**Role:** Coordination, task sequencing, code review, integration testing

**Responsibilities:**
1. Assign tasks to worker bees based on dependencies
2. Review PRs/patches before marking complete
3. Run integration tests after each task completion
4. Manage gate flags during sprint
5. Write flight recap at sprint end

**Tools:** 
- Git status monitoring
- Task file creation/completion
- Gate management (`POST /api/gates`)
- Flight management (`POST /api/flights/*`)

**Constraints:**
- Cannot modify code directly
- Must wait for worker bee task completion before integration test
- Must enforce pre_sprint_review gate before any commits

---

### 2.2 BEE-W1 (Worker 1) — Request Flow Specialist

**Role:** Router integration + Gate enforcement

**Assigned Tasks:**
- TASK-001: Wire router into task creation
- TASK-002: Complete gate enforcement

**Files to Modify:**
- `runtime/server.py`
- `core/router.py` (if enhancement needed)

**Estimated Time:** 2 hours

---

### 2.3 BEE-W2 (Worker 2) — Knowledge Base Specialist

**Role:** KB injection implementation

**Assigned Tasks:**
- TASK-003: Implement KB injection into tasks

**Files to Modify:**
- `runtime/server.py`
- `core/task_files.py`
- `kb/store.py` (if enhancement needed)

**Estimated Time:** 3 hours

---

### 2.4 BEE-W3 (Worker 3) — Real-Time Systems Specialist

**Role:** WebSocket functionality + Background processes

**Assigned Tasks:**
- TASK-004: Make WebSocket functional
- TASK-005: Integrate minder with server startup

**Files to Modify:**
- `runtime/server.py`
- `runtime/minder.py`
- `runtime/store.py` (if broadcast hooks needed)

**Estimated Time:** 4 hours

---

## 3. Task Specifications

### TASK-001: Wire Router into Task Creation

**Assignee:** BEE-W1
**Priority:** Critical
**Depends On:** None
**Estimated:** 1.5 hours

#### 3.1.1 Current State
```python
# server.py:279-291 (approximate)
@app.post("/api/tasks")
def create_task(request: TaskRequest) -> Dict:
    payload = {
        "task_id": task_id,
        "intent": request.intent,  # Captured but ignored
        # ... rest of payload
    }
    path = write_task(repo_root, request.bot_id, payload)
```

#### 3.1.2 Required Changes

1. Import router in server.py:
```python
from core.router import decide_route
```

2. Call router before writing task:
```python
routing = decide_route({"intent": request.intent})
payload["routing"] = {
    "lane": routing.lane,
    "provider": routing.provider,
    "delivery": routing.delivery
}
```

3. Use routing.delivery to determine task file vs cache_prompt behavior

#### 3.1.3 Acceptance Criteria
- [ ] `decide_route()` called for every `POST /api/tasks`
- [ ] Routing decision stored in task payload
- [ ] Intent "code" routes to lane=terminal
- [ ] Intent "design" routes to lane=llm
- [ ] Unit test: create task with intent="code", verify routing.lane="terminal"

#### 3.1.4 Test Command
```bash
curl -X POST http://127.0.0.1:8010/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"TEST-001","intent":"code","title":"Test","summary":"Test routing","kb_entities":[],"delivery_mode":"task_file"}'
# Verify response includes routing.lane = "terminal"
```

---

### TASK-002: Complete Gate Enforcement

**Assignee:** BEE-W1
**Priority:** High
**Depends On:** None
**Estimated:** 30 minutes

#### 3.2.1 Current State
```python
# server.py:348-370
@app.post("/api/git/commit")
def git_commit(request: GitCommitRequest) -> Dict:
    if not _gates.get("allow_q33n_git", False):
        raise HTTPException(403, "Q33N git disabled")
    if not _gates.get("pre_sprint_review", False):
        raise HTTPException(403, "Pre-sprint review required")
    # MISSING: allow_flight_commits check
```

#### 3.2.2 Required Changes

Add missing gate check:
```python
if not _gates.get("allow_flight_commits", False):
    raise HTTPException(403, "Flight commits not enabled")
```

#### 3.2.3 Acceptance Criteria
- [ ] `allow_flight_commits` gate checked in `git_commit`
- [ ] Returns 403 with clear message when gate is False
- [ ] All 3 gates must be True for commit to proceed

#### 3.2.4 Test Command
```bash
# With allow_flight_commits = False (default)
curl -X POST http://127.0.0.1:8010/api/git/commit \
  -H "Content-Type: application/json" \
  -d '{"message":"test commit"}'
# Expected: 403 "Flight commits not enabled"
```

---

### TASK-003: Implement KB Injection into Tasks

**Assignee:** BEE-W2
**Priority:** Critical
**Depends On:** None
**Estimated:** 2.5 hours

#### 3.3.1 Current State
```python
# server.py - create_task()
payload = {
    "kb_entities": request.kb_entities,  # Just stores IDs!
    # ...
}
```

KB content is never retrieved or injected.

#### 3.3.2 Required Changes

1. In `create_task()`, after building base payload:
```python
if request.kb_entities:
    from kb.store import preview_injection
    kb_content = preview_injection(request.kb_entities)
    payload["kb_injection"] = kb_content
```

2. Respect delivery_mode:
```python
if request.delivery_mode == "cache_prompt":
    # Store in separate field for LLM prompt injection
    payload["cache_prompt_content"] = kb_content
elif request.delivery_mode == "task_file":
    # Include in task file body
    payload["kb_injection"] = kb_content
elif request.delivery_mode == "both":
    payload["cache_prompt_content"] = kb_content
    payload["kb_injection"] = kb_content
```

3. Update `write_task()` in task_files.py to include kb_injection in written file

#### 3.3.3 Acceptance Criteria
- [ ] `preview_injection()` called when kb_entities provided
- [ ] KB content included in task file (not just IDs)
- [ ] delivery_mode respected (cache_prompt vs task_file vs both)
- [ ] Empty kb_entities list handled gracefully

#### 3.3.4 Test Command
```bash
# First create a KB entity
curl -X POST http://127.0.0.1:8010/api/kb/entities \
  -H "Content-Type: application/json" \
  -d '{"id":"RULE-TEST","type":"RULE","title":"Test Rule","summary":"Never do X","tags":["test"],"delivery_mode":"task_file","load_mode":"always"}'

# Then create task with that entity
curl -X POST http://127.0.0.1:8010/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"TEST-001","intent":"code","title":"Test KB","summary":"Test injection","kb_entities":["RULE-TEST"],"delivery_mode":"task_file"}'

# Verify task file contains actual rule content, not just "RULE-TEST" ID
```

---

### TASK-004: Make WebSocket Functional

**Assignee:** BEE-W3
**Priority:** Critical
**Depends On:** None
**Estimated:** 3 hours

#### 3.4.1 Current State
```python
# server.py:424-432
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)  # Echo only!
    except WebSocketDisconnect:
        return
```

#### 3.4.2 Required Changes

1. Create connection manager:
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # channel_id -> connections
    
    async def connect(self, websocket: WebSocket, channel_id: str):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, channel_id: str):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].remove(websocket)
    
    async def broadcast(self, channel_id: str, message: dict):
        if channel_id in self.active_connections:
            for connection in self.active_connections[channel_id]:
                await connection.send_json(message)

_ws_manager = ConnectionManager()
```

2. Update WebSocket endpoint:
```python
@app.websocket("/api/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: str):
    await _ws_manager.connect(websocket, channel_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming message
            if data.get("type") == "message":
                # Store and broadcast
                msg = _message_store.add_message(
                    channel_id=channel_id,
                    author=data.get("author", "unknown"),
                    content=data.get("content", ""),
                    lane=data.get("lane"),
                    provider=data.get("provider"),
                    token_count=data.get("token_count")
                )
                await _ws_manager.broadcast(channel_id, {"type": "message", "data": msg})
    except WebSocketDisconnect:
        _ws_manager.disconnect(websocket, channel_id)
```

3. Add broadcast hook to `post_message()`:
```python
@app.post("/api/messages")
async def post_message(request: MessageRequest) -> Dict:
    msg = _message_store.add_message(...)
    # Broadcast to WebSocket clients
    await _ws_manager.broadcast(request.channel_id, {"type": "message", "data": msg})
    return msg
```

#### 3.4.3 Acceptance Criteria
- [ ] WebSocket accepts channel_id parameter
- [ ] Multiple clients can connect to same channel
- [ ] Messages broadcast to all clients in channel
- [ ] REST `POST /api/messages` triggers WebSocket broadcast
- [ ] Disconnection handled cleanly

#### 3.4.4 Test Approach
1. Open two browser tabs to WebSocket test page
2. Connect both to channel "test-channel"
3. Send message from tab 1
4. Verify tab 2 receives broadcast
5. POST to `/api/messages` with channel_id="test-channel"
6. Verify both tabs receive broadcast

---

### TASK-005: Integrate Minder with Server Startup

**Assignee:** BEE-W3
**Priority:** High
**Depends On:** TASK-004 (uses message broadcast)
**Estimated:** 1 hour

#### 3.5.1 Current State
```python
# minder.py - standalone script
if __name__ == "__main__":
    run_minder()
```
Must be run separately: `python -m deia_raqcoon.runtime.minder`

#### 3.5.2 Required Changes

1. Modify minder.py for thread-safe operation:
```python
import threading

_minder_thread: Optional[threading.Thread] = None
_minder_stop_event = threading.Event()

def run_minder(api_base, channel_id, interval_seconds, author, message):
    while not _minder_stop_event.is_set():
        try:
            requests.post(f"{api_base}/api/messages", json={...})
        except Exception as e:
            print(f"Minder ping failed: {e}")
        _minder_stop_event.wait(interval_seconds)

def start_minder_thread(api_base="http://127.0.0.1:8010", interval=600):
    global _minder_thread
    if _minder_thread is not None:
        return  # Already running
    _minder_stop_event.clear()
    _minder_thread = threading.Thread(
        target=run_minder,
        args=(api_base, "system", interval, "minder", "ping"),
        daemon=True
    )
    _minder_thread.start()

def stop_minder_thread():
    global _minder_thread
    _minder_stop_event.set()
    if _minder_thread:
        _minder_thread.join(timeout=5)
        _minder_thread = None
```

2. Add startup hook in server.py:
```python
from runtime.minder import start_minder_thread, stop_minder_thread

@app.on_event("startup")
async def startup_event():
    start_minder_thread()

@app.on_event("shutdown")
async def shutdown_event():
    stop_minder_thread()
```

3. Make interval configurable via environment:
```python
import os
MINDER_INTERVAL = int(os.getenv("DEIA_MINDER_INTERVAL", "600"))
```

#### 3.5.3 Acceptance Criteria
- [ ] Minder starts automatically when server starts
- [ ] Minder stops cleanly on server shutdown
- [ ] Interval configurable via DEIA_MINDER_INTERVAL env var
- [ ] Minder pings visible in `/api/messages` with author="minder"
- [ ] No orphan threads on restart

#### 3.5.4 Test Command
```bash
# Start server
python run_server.py &

# Wait for minder interval (or set DEIA_MINDER_INTERVAL=10 for faster test)
sleep 15

# Check for minder messages
curl http://127.0.0.1:8010/api/messages | grep minder
# Expected: message with author="minder"
```

---

## 4. Task Dependencies & Sequencing

```
TASK-001 (Router) ──────────────────────┐
                                        │
TASK-002 (Gates) ───────────────────────┼──► Q33N Integration Test
                                        │
TASK-003 (KB Injection) ────────────────┤
                                        │
TASK-004 (WebSocket) ───┬───────────────┤
                        │               │
                        ▼               │
TASK-005 (Minder) ──────────────────────┘
```

**Parallel Execution:**
- TASK-001, TASK-002 can run in parallel (both BEE-W1)
- TASK-003 can run in parallel with all others (BEE-W2)
- TASK-004 must complete before TASK-005 (both BEE-W3)

**Critical Path:** TASK-004 → TASK-005 → Integration Test

---

## 5. Q33N Workflow

### 5.1 Sprint Initialization

```bash
# 1. Start flight
curl -X POST http://127.0.0.1:8010/api/flights/start \
  -d '{"flight_id":"SPRINT-001","title":"Integration Wiring Sprint"}'

# 2. Enable pre_sprint_review gate (after reviewing this spec)
curl -X POST http://127.0.0.1:8010/api/gates \
  -d '{"pre_sprint_review": true}'

# 3. Create task files for each worker bee
# (Using POST /api/tasks for TASK-001 through TASK-005)
```

### 5.2 During Sprint

1. Monitor task completion via `/api/tasks/response`
2. Review patches before approving
3. Run integration tests after each task
4. Update gate flags as needed

### 5.3 Sprint Completion

```bash
# 1. Run full integration test suite
# 2. Enable remaining gates for final commit
curl -X POST http://127.0.0.1:8010/api/gates \
  -d '{"allow_q33n_git": true, "allow_flight_commits": true}'

# 3. Commit all changes
curl -X POST http://127.0.0.1:8010/api/git/commit \
  -d '{"message":"SPRINT-001: Complete integration wiring"}'

# 4. End flight with recap
curl -X POST http://127.0.0.1:8010/api/flights/recap \
  -d '{"flight_id":"SPRINT-001","recap_text":"Completed router, KB injection, WebSocket, minder integration. All gates enforced."}'

curl -X POST http://127.0.0.1:8010/api/flights/end \
  -d '{"flight_id":"SPRINT-001"}'
```

---

## 6. Integration Test Checklist

After all tasks complete, Q33N runs:

| # | Test | Command/Action | Expected |
|---|------|----------------|----------|
| 6.1 | Router wired | POST /api/tasks with intent="code" | Response includes routing.lane="terminal" |
| 6.2 | All gates enforced | POST /api/git/commit with gates=false | 403 for each gate |
| 6.3 | KB injection works | POST /api/tasks with kb_entities | Task file contains rule content |
| 6.4 | WebSocket broadcasts | Connect 2 clients, post message | Both receive broadcast |
| 6.5 | Minder auto-starts | Start server, wait, check messages | Minder ping present |
| 6.6 | Full round-trip | Create task → Bee responds → Complete task | Archive contains completed task |

---

## 7. Rollback Plan

If integration fails:

1. Revert to pre-sprint commit
2. End flight with failure recap
3. Create BEE-POSTMORTEM analysis task
4. Re-plan with smaller increments

---

## 8. Files Modified Summary

| File | Tasks | Changes |
|------|-------|---------|
| runtime/server.py | 001, 002, 003, 004, 005 | Router import, gate check, KB injection, WebSocket manager, minder startup |
| core/router.py | 001 | No changes expected (already implemented) |
| core/task_files.py | 003 | Include kb_injection in written file |
| kb/store.py | 003 | No changes expected (preview_injection exists) |
| runtime/minder.py | 005 | Thread-safe start/stop functions |

---

*End of Sprint Specification*
