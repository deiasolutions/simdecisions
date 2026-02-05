# TASK-014: Complete Gate Enforcement

## Status: PENDING
## Assignee: BEE-001
## Effort: 30-60 min
## Priority: P1

---

## Objective

Add missing `allow_flight_commits` gate check to git_commit endpoint.

---

## Problem

From BEE3 audit:
```python
# server.py:348-370
@app.post("/api/git/commit")
def git_commit(request: GitCommitRequest) -> Dict:
    # Checks these:
    if not _gates.get("allow_q33n_git", False): ...
    if not _gates.get("pre_sprint_review", False): ...
    # BUT NOT this:
    # if not _gates.get("allow_flight_commits", False): ...
```

---

## Solution

### Update `git_commit` in `server.py`

```python
@app.post("/api/git/commit")
def git_commit(request: GitCommitRequest) -> Dict:
    """Gate-protected git commit."""
    
    # Log gate check
    from runtime.ledger import log_event
    log_event("gate_checked", data={"gate": "git_commit", "gates": _gates.copy()})
    
    # Check all required gates
    if not _gates.get("allow_q33n_git", False):
        return {"status": "blocked", "reason": "allow_q33n_git gate is closed"}
    
    if not _gates.get("pre_sprint_review", False):
        return {"status": "blocked", "reason": "pre_sprint_review gate is closed"}
    
    if not _gates.get("allow_flight_commits", False):
        return {"status": "blocked", "reason": "allow_flight_commits gate is closed"}
    
    # Proceed with commit...
    repo_root = request.repo_root or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "commit", "-am", request.message],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        
        log_event("git_commit", data={
            "message": request.message,
            "returncode": result.returncode
        })
        
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### Document gate meanings

Add to README or docs:

| Gate | Purpose | Default |
|------|---------|---------|
| `allow_q33n_git` | Master switch for Q33N git operations | False |
| `pre_sprint_review` | Human reviewed sprint before start | False |
| `allow_flight_commits` | Commits allowed during active flight | False |

### Gate check order

1. `allow_q33n_git` — Must be enabled for any git ops
2. `pre_sprint_review` — Human must review before sprint
3. `allow_flight_commits` — Per-flight commit permission

All three must be True for commit to proceed.

---

## Test

```bash
# All gates closed (default)
curl -X POST http://localhost:8010/api/git/commit \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' 
# Returns: blocked, allow_q33n_git

# Open first gate
curl -X POST http://localhost:8010/api/gates \
  -H "Content-Type: application/json" \
  -d '{"allow_q33n_git": true}'

# Try again
curl -X POST http://localhost:8010/api/git/commit \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
# Returns: blocked, pre_sprint_review

# Open all gates
curl -X POST http://localhost:8010/api/gates \
  -H "Content-Type: application/json" \
  -d '{"allow_q33n_git": true, "pre_sprint_review": true, "allow_flight_commits": true}'

# Now commit works
```

---

## Done When

- [ ] `allow_flight_commits` check added to git_commit
- [ ] Gate check logged via ledger
- [ ] All three gates required for commit
- [ ] Clear error messages for each blocked gate
