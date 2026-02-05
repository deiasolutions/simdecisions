# TASK-015: Spec Plan Endpoint

## Status: PENDING
## Assignee: BEE-001
## Effort: 4-6 hours
## Priority: P2

---

## Objective

Build `/api/spec/plan` endpoint to convert specs into task graphs.

---

## What to Build

### 1. Create `schemas/spec.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["title", "goals"],
  "properties": {
    "title": {"type": "string"},
    "goals": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    },
    "constraints": {
      "type": "array",
      "items": {"type": "string"}
    },
    "acceptance_criteria": {
      "type": "array",
      "items": {"type": "string"}
    },
    "scope_exclusions": {
      "type": "array",
      "items": {"type": "string"}
    },
    "context": {"type": "string"}
  }
}
```

### 2. Create `runtime/spec_parser.py`

```python
import re
import json
from pathlib import Path
from typing import Dict, List, Optional

def parse_markdown_spec(content: str) -> Dict:
    """Parse markdown spec into structured format."""
    spec = {
        "title": "",
        "goals": [],
        "constraints": [],
        "acceptance_criteria": [],
        "scope_exclusions": [],
        "context": ""
    }
    
    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        spec["title"] = title_match.group(1).strip()
    
    # Extract sections
    sections = {
        "goals": r'##\s*Goals?\s*\n(.*?)(?=\n##|\Z)',
        "constraints": r'##\s*Constraints?\s*\n(.*?)(?=\n##|\Z)',
        "acceptance_criteria": r'##\s*Acceptance\s*Criteria?\s*\n(.*?)(?=\n##|\Z)',
        "scope_exclusions": r'##\s*(?:Scope\s*)?Exclusions?\s*\n(.*?)(?=\n##|\Z)',
        "context": r'##\s*Context\s*\n(.*?)(?=\n##|\Z)'
    }
    
    for key, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1).strip()
            if key == "context":
                spec[key] = section_content
            else:
                # Parse bullet points
                items = re.findall(r'[-*]\s+(.+)', section_content)
                spec[key] = [item.strip() for item in items]
    
    return spec

def parse_json_spec(content: str) -> Dict:
    """Parse JSON spec."""
    return json.loads(content)

def parse_spec(content: str, format: str = "auto") -> Dict:
    """Parse spec from string, auto-detecting format."""
    if format == "auto":
        content_stripped = content.strip()
        if content_stripped.startswith("{"):
            format = "json"
        else:
            format = "markdown"
    
    if format == "json":
        return parse_json_spec(content)
    else:
        return parse_markdown_spec(content)
```

### 3. Create `runtime/task_graph.py`

```python
from typing import Dict, List
from datetime import datetime
import uuid

def generate_task_id() -> str:
    """Generate unique task ID."""
    return f"TASK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"

def spec_to_tasks(spec: Dict, bot_id: str = "BEE-001") -> List[Dict]:
    """Convert parsed spec into task list."""
    tasks = []
    
    # Create one task per goal
    for i, goal in enumerate(spec.get("goals", []), 1):
        task = {
            "task_id": generate_task_id(),
            "bot_id": bot_id,
            "intent": classify_intent(goal),
            "title": f"Goal {i}: {goal[:50]}...",
            "summary": goal,
            "constraints": spec.get("constraints", []),
            "acceptance_criteria": spec.get("acceptance_criteria", []),
            "dependencies": [],
            "status": "pending",
            "order": i
        }
        tasks.append(task)
    
    # Add dependency chain (sequential by default)
    for i in range(1, len(tasks)):
        tasks[i]["dependencies"] = [tasks[i-1]["task_id"]]
    
    return tasks

def classify_intent(goal: str) -> str:
    """Classify goal into intent type."""
    goal_lower = goal.lower()
    
    if any(w in goal_lower for w in ["create", "build", "implement", "code", "write"]):
        return "code"
    elif any(w in goal_lower for w in ["design", "plan", "architect", "spec"]):
        return "design"
    elif any(w in goal_lower for w in ["test", "verify", "validate", "check"]):
        return "verify"
    elif any(w in goal_lower for w in ["deploy", "release", "ship"]):
        return "deploy"
    else:
        return "code"  # Default
```

### 4. Add endpoint to `server.py`

```python
from runtime.spec_parser import parse_spec
from runtime.task_graph import spec_to_tasks

class SpecPlanRequest(BaseModel):
    content: str
    format: str = "auto"  # auto, markdown, json
    bot_id: str = "BEE-001"
    create_tasks: bool = False  # If True, write task files

@app.post("/api/spec/plan")
def plan_spec(request: SpecPlanRequest) -> Dict:
    """Parse spec and generate task plan."""
    from runtime.ledger import log_event
    
    try:
        # Parse spec
        spec = parse_spec(request.content, request.format)
        
        # Generate tasks
        tasks = spec_to_tasks(spec, request.bot_id)
        
        log_event("spec_planned", data={
            "title": spec.get("title", ""),
            "goal_count": len(spec.get("goals", [])),
            "task_count": len(tasks)
        })
        
        # Optionally create task files
        created_files = []
        if request.create_tasks:
            for task in tasks:
                from core.task_files import write_task
                path = write_task(os.getcwd(), task["bot_id"], task)
                created_files.append(str(path))
        
        return {
            "status": "ok",
            "spec": spec,
            "tasks": tasks,
            "created_files": created_files
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## Example Usage

### Input (Markdown)

```markdown
# Add User Authentication

## Goals
- Implement JWT token generation
- Add login endpoint
- Add logout endpoint
- Protect routes with auth middleware

## Constraints
- Use existing User model
- Tokens expire in 24 hours

## Acceptance Criteria
- Login returns valid JWT
- Protected routes reject invalid tokens
- Logout invalidates token
```

### Output

```json
{
  "status": "ok",
  "spec": {
    "title": "Add User Authentication",
    "goals": [
      "Implement JWT token generation",
      "Add login endpoint",
      "Add logout endpoint",
      "Protect routes with auth middleware"
    ],
    "constraints": ["Use existing User model", "Tokens expire in 24 hours"],
    "acceptance_criteria": ["Login returns valid JWT", "..."]
  },
  "tasks": [
    {"task_id": "TASK-...", "intent": "code", "title": "Goal 1: Implement JWT...", ...},
    {"task_id": "TASK-...", "intent": "code", "title": "Goal 2: Add login...", ...}
  ]
}
```

---

## Done When

- [ ] `schemas/spec.json` created
- [ ] `runtime/spec_parser.py` parses markdown and JSON
- [ ] `runtime/task_graph.py` generates task list
- [ ] `POST /api/spec/plan` returns parsed spec + tasks
- [ ] Optional: creates task files when `create_tasks=true`
