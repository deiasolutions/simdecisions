# TASK-017: Task Verify Endpoint

## Status: PENDING
## Assignee: BEE-001
## Effort: 2-3 hours
## Priority: P2
## Depends: TASK-016

---

## Objective

Build `/api/tasks/verify` endpoint to run tests/lint on task output.

---

## What to Build

### 1. Create `runtime/verifier.py`

```python
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from runtime.ledger import log_event

class Verifier:
    """Run verification commands on task outputs."""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = Path(repo_root or ".")
    
    def run_command(self, cmd: List[str], cwd: str = None) -> Dict:
        """Run a verification command."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            return {
                "command": " ".join(cmd),
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:],  # Last 2K chars
                "stderr": result.stderr[-2000:],
                "passed": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "command": " ".join(cmd),
                "returncode": -1,
                "error": "timeout",
                "passed": False
            }
        except Exception as e:
            return {
                "command": " ".join(cmd),
                "returncode": -1,
                "error": str(e),
                "passed": False
            }
    
    def lint_python(self, files: List[str] = None) -> Dict:
        """Run Python linting."""
        if files:
            cmd = ["python", "-m", "py_compile"] + files
        else:
            cmd = ["python", "-m", "py_compile", "."]
        return self.run_command(cmd)
    
    def run_pytest(self, path: str = None) -> Dict:
        """Run pytest."""
        cmd = ["pytest", "-v", "--tb=short"]
        if path:
            cmd.append(path)
        return self.run_command(cmd)
    
    def run_ruff(self, path: str = None) -> Dict:
        """Run ruff linter."""
        cmd = ["ruff", "check"]
        if path:
            cmd.append(path)
        else:
            cmd.append(".")
        return self.run_command(cmd)
    
    def verify_task(self, task_id: str, checks: List[str] = None) -> Dict:
        """Run verification suite for a task."""
        if checks is None:
            checks = ["lint", "test"]
        
        log_event("verification_started", task_id=task_id,
                  data={"checks": checks})
        
        results = {
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
            "passed": True
        }
        
        for check in checks:
            if check == "lint":
                results["checks"]["lint"] = self.run_ruff()
            elif check == "test":
                results["checks"]["test"] = self.run_pytest()
            elif check == "compile":
                results["checks"]["compile"] = self.lint_python()
            
            # Update overall pass status
            if not results["checks"].get(check, {}).get("passed", True):
                results["passed"] = False
        
        log_event("verification_completed", task_id=task_id,
                  data={"passed": results["passed"]})
        
        return results
```

### 2. Add endpoint to `server.py`

```python
from runtime.verifier import Verifier

class VerifyRequest(BaseModel):
    task_id: Optional[str] = None
    checks: List[str] = ["lint", "test"]
    path: Optional[str] = None

@app.post("/api/tasks/verify")
def verify_task(request: VerifyRequest) -> Dict:
    """Run verification on task output or codebase."""
    
    verifier = Verifier(repo_root=os.getcwd())
    
    if request.task_id:
        # Verify specific task
        return verifier.verify_task(request.task_id, request.checks)
    else:
        # Run general verification
        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
            "passed": True
        }
        
        for check in request.checks:
            if check == "lint":
                results["checks"]["lint"] = verifier.run_ruff(request.path)
            elif check == "test":
                results["checks"]["test"] = verifier.run_pytest(request.path)
            elif check == "compile":
                results["checks"]["compile"] = verifier.lint_python()
            
            if not results["checks"].get(check, {}).get("passed", True):
                results["passed"] = False
        
        return results


@app.get("/api/verify/health")
def verify_health() -> Dict:
    """Check if verification tools are available."""
    verifier = Verifier()
    
    tools = {}
    for tool, cmd in [("ruff", ["ruff", "--version"]), 
                       ("pytest", ["pytest", "--version"])]:
        result = verifier.run_command(cmd)
        tools[tool] = {
            "available": result["returncode"] == 0,
            "version": result["stdout"].strip() if result["returncode"] == 0 else None
        }
    
    return {"tools": tools}
```

---

## Flow

```
POST /api/tasks/verify
    │
    ├─► Parse checks to run
    │
    ├─► For each check:
    │   ├─► lint → ruff check
    │   ├─► test → pytest
    │   └─► compile → py_compile
    │
    ├─► Log results via ledger
    │
    └─► Return pass/fail + details
```

---

## Test

```bash
# Check available tools
curl http://localhost:8010/api/verify/health

# Run lint only
curl -X POST http://localhost:8010/api/tasks/verify \
  -H "Content-Type: application/json" \
  -d '{"checks": ["lint"]}'

# Run all checks
curl -X POST http://localhost:8010/api/tasks/verify \
  -H "Content-Type: application/json" \
  -d '{"checks": ["lint", "test", "compile"]}'

# Verify specific path
curl -X POST http://localhost:8010/api/tasks/verify \
  -H "Content-Type: application/json" \
  -d '{"checks": ["lint"], "path": "runtime/"}'
```

---

## Done When

- [ ] `runtime/verifier.py` created
- [ ] `POST /api/tasks/verify` runs checks
- [ ] `GET /api/verify/health` shows tool status
- [ ] Lint (ruff) check works
- [ ] Test (pytest) check works
- [ ] Results logged via ledger
