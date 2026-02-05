# TASK-016: Task Run Endpoint

## Status: PENDING
## Assignee: BEE-001
## Effort: 3-4 hours
## Priority: P2
## Depends: TASK-015

---

## Objective

Build `/api/tasks/run` endpoint to execute tasks via routing.

---

## What to Build

### 1. Create `runtime/executor.py`

```python
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

from core.router import decide_route
from core.task_files import write_task, complete_task
from runtime.ledger import log_event

class TaskExecutor:
    """Execute tasks by routing to appropriate lane."""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = repo_root or "."
    
    def execute(self, task: Dict) -> Dict:
        """Execute a single task."""
        task_id = task.get("task_id", "unknown")
        
        log_event("task_execution_started", task_id=task_id, 
                  data={"intent": task.get("intent")})
        
        # Route the task
        routing = decide_route(task)
        task["lane"] = routing.lane
        task["provider"] = routing.provider
        task["delivery_mode"] = routing.delivery
        task["status"] = "active"
        task["started_at"] = datetime.utcnow().isoformat() + "Z"
        
        log_event("task_routed", task_id=task_id,
                  data={"lane": routing.lane, "provider": routing.provider})
        
        # Write task file for bot pickup
        bot_id = task.get("bot_id", "BEE-001")
        task_path = write_task(self.repo_root, bot_id, task)
        
        return {
            "status": "dispatched",
            "task_id": task_id,
            "lane": routing.lane,
            "provider": routing.provider,
            "task_path": str(task_path)
        }
    
    def check_response(self, task_id: str) -> Optional[Dict]:
        """Check if response exists for task."""
        from core.task_files import latest_response
        
        response_path = latest_response(self.repo_root, task_id)
        if response_path and response_path.exists():
            return {
                "status": "completed",
                "response_path": str(response_path),
                "content": response_path.read_text()[:1000]  # First 1K chars
            }
        return None
    
    def poll_until_complete(self, task_id: str, timeout_seconds: int = 300) -> Dict:
        """Poll for task completion."""
        import time
        start = time.time()
        
        while time.time() - start < timeout_seconds:
            response = self.check_response(task_id)
            if response:
                log_event("task_completed", task_id=task_id)
                return response
            time.sleep(5)  # Poll every 5 seconds
        
        return {"status": "timeout", "task_id": task_id}
```

### 2. Add endpoint to `server.py`

```python
from runtime.executor import TaskExecutor

class TaskRunRequest(BaseModel):
    task_id: Optional[str] = None
    bot_id: str = "BEE-001"
    intent: str
    title: str
    summary: str
    kb_entities: List[str] = []
    wait_for_response: bool = False
    timeout_seconds: int = 300

@app.post("/api/tasks/run")
def run_task(request: TaskRunRequest) -> Dict:
    """Execute a task through the routing system."""
    
    task = {
        "task_id": request.task_id or f"TASK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "bot_id": request.bot_id,
        "intent": request.intent,
        "title": request.title,
        "summary": request.summary,
        "kb_entities": request.kb_entities,
        "status": "pending"
    }
    
    executor = TaskExecutor(repo_root=os.getcwd())
    result = executor.execute(task)
    
    # Optionally wait for response
    if request.wait_for_response:
        response = executor.poll_until_complete(
            task["task_id"], 
            timeout_seconds=request.timeout_seconds
        )
        result["response"] = response
    
    return result


class TaskStatusRequest(BaseModel):
    task_id: str

@app.get("/api/tasks/status/{task_id}")
def get_task_status(task_id: str) -> Dict:
    """Check status of a running task."""
    executor = TaskExecutor(repo_root=os.getcwd())
    
    response = executor.check_response(task_id)
    if response:
        return {"status": "completed", **response}
    
    # Check if task file exists
    from pathlib import Path
    for bot_dir in Path(".deia/hive/tasks").glob("*"):
        for task_file in bot_dir.glob(f"*{task_id}*.json"):
            with open(task_file) as f:
                task = json.load(f)
            return {"status": task.get("status", "pending"), "task": task}
    
    return {"status": "not_found", "task_id": task_id}
```

---

## Flow

```
POST /api/tasks/run
    │
    ├─► Parse request into task dict
    │
    ├─► decide_route() → lane, provider
    │
    ├─► write_task() → .deia/hive/tasks/{bot}/
    │
    ├─► (optional) poll for response
    │
    └─► Return dispatch result
```

---

## Test

```bash
# Run task (fire and forget)
curl -X POST http://localhost:8010/api/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "code",
    "title": "Create hello.py",
    "summary": "Write a hello world script"
  }'

# Check status
curl http://localhost:8010/api/tasks/status/TASK-20260201...

# Run and wait
curl -X POST http://localhost:8010/api/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "code",
    "title": "Create hello.py",
    "summary": "Write a hello world script",
    "wait_for_response": true,
    "timeout_seconds": 60
  }'
```

---

## Done When

- [ ] `runtime/executor.py` created
- [ ] `POST /api/tasks/run` dispatches tasks
- [ ] `GET /api/tasks/status/{task_id}` returns status
- [ ] Routing applied to dispatched tasks
- [ ] Optional wait-for-response works
