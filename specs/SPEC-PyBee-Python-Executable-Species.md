# SPEC: PyBee — Python Executable Species for SimDecisions Hive

**Status:** DRAFT — Ready for Claude Code implementation  
**Date:** 2026-02-04  
**Author:** Dave (daaaave-atx) via voice ideation  
**Context:** SimDecisions Architecture, RAGGIT Specification  

---

## 1. Overview

### 1.1 What Is a PyBee?

A **PyBee** is a new species of worker in the SimDecisions hive architecture. Unlike LLM-based bees (Claude, GPT, Gemini), PyBees are Python executables that:

- Run in the OS domain (subprocess, not API call)
- Are defined using RAGGIT-style markdown specs (self-describing, self-installing)
- Can be crowdsourced from a public package registry
- Execute deterministically (no LLM inference costs, no hallucination)

### 1.2 Why PyBees?

| LLM Bees | PyBees |
|----------|--------|
| Flexible reasoning | Deterministic execution |
| Expensive per call | Free after install |
| Can hallucinate | Predictable output |
| Slow (API latency) | Fast (local execution) |
| Good for ambiguous tasks | Good for well-defined tasks |

**Together:** LLM bees handle judgment; PyBees handle automation. The hive gains both intelligence and efficiency.

### 1.3 Naming Convention

- **PyBee** — Generic term for Python executable species
- **PYBEE-{NNN}** — Instance identifier (e.g., PYBEE-001)
- **PyBee Package** — A RAGGIT-spec markdown file that defines and installs a PyBee

---

## 2. Architecture

### 2.1 PyBee Lifecycle

```
1. DISCOVER  — Find PyBee package (local file, GitHub, RAGGIT registry)
2. INSTALL   — LLM reads spec, extracts Python code, writes to hive workspace
3. REGISTER  — PyBee added to hive bee registry with capabilities declared
4. DISPATCH  — Q33N routes tasks to PyBee based on intent/capability match
5. EXECUTE   — Python subprocess runs, captures stdout/stderr
6. REPORT    — Output written to task response, logged to event ledger
```

### 2.2 Where PyBees Live

```
.deia/
└── hive/
    ├── tasks/           # Task files (existing)
    ├── responses/       # Response files (existing)
    ├── archive/         # Completed tasks (existing)
    └── pybees/          # NEW: PyBee installation directory
        ├── registry.json    # Installed PyBees and their capabilities
        ├── PYBEE-001/       # Individual PyBee workspace
        │   ├── spec.md      # Original RAGGIT spec
        │   ├── main.py      # Extracted executable
        │   ├── requirements.txt  # Dependencies (if any)
        │   └── config.json  # Runtime configuration
        └── PYBEE-002/
            └── ...
```

### 2.3 Integration with Existing Hive

PyBees are registered in the same bee registry as LLM bees:

```json
{
  "bees": [
    {"id": "BEE-001", "type": "llm", "provider": "claude", "status": "active"},
    {"id": "BEE-002", "type": "llm", "provider": "gemini", "status": "active"},
    {"id": "PYBEE-001", "type": "pybee", "package": "manim-spec-writer", "status": "active"}
  ]
}
```

---

## 3. PyBee Package Specification (RAGGIT Format)

A PyBee package is a markdown file that contains everything needed to install and run the bot.

### 3.1 Package Structure

```markdown
# PyBee: {package-name}

**Version:** {semver}
**Author:** {creator}
**License:** {license}
**Capabilities:** {comma-separated list}

## Description

{What this PyBee does, when to use it}

## Dependencies

```requirements
{pip packages, one per line}
```

## Configuration

```json
{
  "input_format": "{json|text|file}",
  "output_format": "{json|text|file}",
  "timeout_seconds": {number},
  "requires_env": ["{env_var_names}"]
}
```

## Code

```python
#!/usr/bin/env python3
"""
{docstring}
"""

# Full executable Python code here
# Must accept input via stdin or --input flag
# Must write output to stdout
# Exit code 0 = success, non-zero = failure

def main():
    ...

if __name__ == "__main__":
    main()
```

## Usage Examples

```bash
# Example invocation
echo '{"task": "..."}' | python main.py
```

## Tests

```python
# Optional: test cases for validation
def test_basic():
    ...
```
```

### 3.2 Example: Manim Spec Writer PyBee

```markdown
# PyBee: manim-spec-writer

**Version:** 0.1.0
**Author:** daaaave-atx
**License:** MIT
**Capabilities:** animation-spec, manim, visualization

## Description

Generates Manim animation specifications from natural language descriptions.
Use this PyBee when you need to create mathematical animations without 
learning Manim's API directly.

Input: JSON with `description` field describing desired animation
Output: JSON with `manim_code` field containing executable Manim script

## Dependencies

```requirements
manim>=0.18.0
```

## Configuration

```json
{
  "input_format": "json",
  "output_format": "json",
  "timeout_seconds": 30,
  "requires_env": []
}
```

## Code

```python
#!/usr/bin/env python3
"""
Manim Spec Writer — Generates Manim code from descriptions.
"""
import sys
import json

TEMPLATES = {
    "circle": "Circle()",
    "square": "Square()",
    "text": "Text('{text}')",
    # ... more templates
}

def generate_manim_code(description: str) -> str:
    # Pattern matching and code generation logic
    # This is deterministic template-based generation
    code = f'''
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Generated from: {description}
        shape = {TEMPLATES.get('circle')}
        self.play(Create(shape))
        self.wait()
'''
    return code

def main():
    input_data = json.load(sys.stdin)
    description = input_data.get("description", "")
    
    manim_code = generate_manim_code(description)
    
    output = {
        "status": "success",
        "manim_code": manim_code,
        "render_command": "manim -pql main.py GeneratedScene"
    }
    
    json.dump(output, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
```
```

---

## 4. Installation Flow

### 4.1 LLM-Assisted Installation

When a PyBee package is provided to the hive:

1. **Q33N or human** provides the RAGGIT spec (file path, URL, or inline)
2. **LLM bee** reads the spec and extracts:
   - Package metadata
   - Dependencies list
   - Python code block
   - Configuration
3. **LLM bee** writes extracted components to `.deia/hive/pybees/{PYBEE-NNN}/`
4. **LLM bee** runs `pip install -r requirements.txt` (if dependencies exist)
5. **LLM bee** validates by running test cases (if provided)
6. **LLM bee** updates `registry.json` with new PyBee entry

### 4.2 Installation API

```
POST /api/pybees/install
{
  "source": "file" | "url" | "inline",
  "spec": "{path or URL or markdown content}",
  "pybee_id": "PYBEE-{NNN}"  // optional, auto-generated if omitted
}

Response:
{
  "status": "installed" | "failed",
  "pybee_id": "PYBEE-001",
  "capabilities": ["animation-spec", "manim"],
  "error": null | "{error message}"
}
```

### 4.3 Remote Package Registry (Future)

```
GET https://registry.simdecisions.com/pybees/{package-name}
GET https://raw.githubusercontent.com/deiasolutions/pybee-packages/main/{package-name}.md
```

---

## 5. Execution Flow

### 5.1 Task Routing

When a task arrives with an intent that matches a PyBee's capabilities:

```python
# In router.py (extended)
def decide_route(task: Dict) -> RouteDecision:
    intent = task.get("intent", "")
    
    # Check PyBee capabilities first (cheaper than LLM)
    for pybee in load_pybee_registry():
        if intent_matches_capabilities(intent, pybee["capabilities"]):
            return RouteDecision(
                lane="pybee",
                provider=pybee["id"],
                delivery="subprocess"
            )
    
    # Fall back to existing LLM routing
    if intent in ("design", "planning"):
        return RouteDecision(lane="llm", provider="default", delivery="cache_prompt")
    ...
```

### 5.2 Subprocess Execution

```python
# In runtime/pybee_executor.py (new)
import subprocess
import json
from pathlib import Path

def execute_pybee(pybee_id: str, task_payload: Dict) -> Dict:
    pybee_dir = Path(f".deia/hive/pybees/{pybee_id}")
    main_py = pybee_dir / "main.py"
    config = json.loads((pybee_dir / "config.json").read_text())
    
    # Prepare input
    input_data = json.dumps(task_payload)
    
    # Execute
    result = subprocess.run(
        ["python", str(main_py)],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=config.get("timeout_seconds", 60),
        cwd=str(pybee_dir)
    )
    
    # Capture output
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None,
        "exit_code": result.returncode
    }
```

### 5.3 Event Ledger Integration

PyBee executions are logged like any other bee action:

```json
{
  "event_type": "task_executed",
  "actor": "pybee:PYBEE-001",
  "domain": "animation",
  "signal_type": "internal",
  "oracle_tier": 0,
  "cost_tokens": 0,
  "cost_usd": 0.0,
  "cost_carbon": 0.0001,
  "payload_json": "{\"input\": ..., \"output\": ...}"
}
```

**Note:** PyBees are Tier 0 oracles — deterministic, free, instant.

---

## 6. API Interface Layer

### 6.1 External API → Hive Communication

PyBees can serve as the interface between external systems and the hive:

```
External API Request
        ↓
    PyBee (PYBEE-API-001)
        ↓
    Translates to hive task format
        ↓
    Q33N routes to appropriate bee
        ↓
    Response flows back through PyBee
        ↓
External API Response
```

### 6.2 Example: REST-to-Hive Bridge PyBee

A PyBee that accepts REST requests and dispatches to the hive:

```python
# In a PyBee package: rest-hive-bridge
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
HIVE_API = "http://127.0.0.1:8010"

@app.route("/api/v1/tasks", methods=["POST"])
def create_task():
    external_request = request.json
    
    # Translate to hive format
    hive_task = {
        "bot_id": "BEE-001",
        "intent": external_request.get("type", "code"),
        "title": external_request.get("title"),
        "summary": external_request.get("description"),
        "kb_entities": [],
        "delivery_mode": "task_file"
    }
    
    # Dispatch to hive
    response = requests.post(f"{HIVE_API}/api/tasks", json=hive_task)
    
    # Return translated response
    return jsonify({"task_id": response.json().get("task_id")})
```

---

## 7. Output Mechanism: RAGGIT Egg Format

### 7.1 PyBee Output as Egg

When a PyBee produces output, it can be wrapped as a RAGGIT egg for transport:

```json
{
  "uri": "simdecisions://pybee/PYBEE-001/output/2026-02-04-123456",
  "label": "Manim Animation Spec",
  "type": "application/x-pybee-output",
  "content": {
    "manim_code": "...",
    "render_command": "..."
  },
  "caps": ["view", "execute", "share"],
  "action": "share"
}
```

### 7.2 Egg-to-Egg Workflows

```
Input Egg (task description)
        ↓
    PyBee processes
        ↓
Output Egg (result)
        ↓
    Next bee consumes output egg
        ↓
    ...
```

---

## 8. Implementation Tasks

### Phase 1: Foundation (TASK-020 series)

| Task | Description | Effort |
|------|-------------|--------|
| TASK-020 | Create `.deia/hive/pybees/` directory structure | 1 hr |
| TASK-021 | Implement `registry.json` schema and CRUD | 2 hrs |
| TASK-022 | Build PyBee package parser (extract code/deps from markdown) | 3 hrs |
| TASK-023 | Implement `pybee_executor.py` subprocess runner | 2 hrs |
| TASK-024 | Add `/api/pybees/install` endpoint | 2 hrs |
| TASK-025 | Extend router.py to check PyBee capabilities | 2 hrs |

### Phase 2: Integration (TASK-026 series)

| Task | Description | Effort |
|------|-------------|--------|
| TASK-026 | Event ledger logging for PyBee executions | 1 hr |
| TASK-027 | PyBee output → RAGGIT egg wrapper | 2 hrs |
| TASK-028 | Create example PyBee: `echo-bot` (minimal test) | 1 hr |
| TASK-029 | Create example PyBee: `json-transform` (utility) | 2 hrs |

### Phase 3: Ecosystem (Post-v1)

| Task | Description |
|------|-------------|
| Remote registry client | Fetch packages from GitHub/registry |
| PyBee versioning | Upgrade/rollback installed packages |
| Dependency isolation | venv per PyBee to avoid conflicts |
| Security sandbox | Restrict filesystem/network access |

---

## 9. Crowdsourcing Vision

### 9.1 Public Package Repository

```
github.com/deiasolutions/pybee-packages/
├── README.md
├── packages/
│   ├── manim-spec-writer.md
│   ├── csv-analyzer.md
│   ├── json-transformer.md
│   ├── pdf-extractor.md
│   └── ...
└── CONTRIBUTING.md
```

### 9.2 Contribution Flow

1. Developer writes PyBee package in RAGGIT markdown format
2. PR to `pybee-packages` repo
3. Automated validation (syntax, tests, security scan)
4. Review by maintainers
5. Merge → available to all SimDecisions hives

### 9.3 Package Discovery

```
GET /api/pybees/search?capability=manim
GET /api/pybees/search?author=daaaave-atx
GET /api/pybees/popular
```

---

## 10. Security Considerations

### 10.1 Risks

| Risk | Mitigation |
|------|------------|
| Malicious code execution | Sandbox with restricted permissions |
| Dependency vulnerabilities | Pin versions, scan with safety/pip-audit |
| Resource exhaustion | Timeout, memory limits, CPU quotas |
| Data exfiltration | Network isolation for untrusted packages |

### 10.2 Trust Levels

| Level | Source | Permissions |
|-------|--------|-------------|
| Trusted | Local file, verified author | Full access |
| Community | Public registry, reviewed | Sandboxed |
| Untrusted | Unknown source | Reject or manual review |

---

## 11. Success Criteria

### 11.1 MVP (Phase 1 Complete)

- [ ] Can install a PyBee from local markdown file
- [ ] PyBee appears in registry
- [ ] Task routes to PyBee based on capability match
- [ ] PyBee executes and returns output
- [ ] Execution logged to event ledger with Tier 0 oracle

### 11.2 Full Feature (Phase 2 Complete)

- [ ] Output wrapped as RAGGIT egg
- [ ] Multiple PyBees can chain (egg-to-egg)
- [ ] Example packages: echo-bot, json-transform
- [ ] Documentation for writing PyBee packages

---

*"Determinism is the worker bee of intelligence. Judgment is the queen."*

---

## Addendum A: Adherence to Practice (Mandatory)

**Date:** 2026-02-04
**Authority:** Q33N

PyBees are bees. All DEIA processes apply.

### A.1 Mandatory Process Compliance

| Process | Requirement |
|---------|-------------|
| **PROCESS-0001** | Check for existing process before creating new behavior |
| **PROCESS-0002** | Follow task state machine: queue→claimed→buzz→archive |
| **PROCESS-0004** | Log activity to `.deia/bot-logs/{PYBEE-ID}-activity.jsonl` |

### A.2 Activity Logging for PyBees

Every PyBee execution MUST log:

```python
# In pybee_executor.py - wrap all executions

def execute_pybee(pybee_id: str, task_payload: Dict) -> Dict:
    task_id = task_payload.get("task_id", "unknown")

    # ADHERENCE: Log start
    log_activity(pybee_id, "task_started", task_id,
                 f"Executing {pybee_id} for {task_id}")

    try:
        result = _run_subprocess(pybee_id, task_payload)

        # ADHERENCE: Log completion
        log_activity(pybee_id, "task_completed", task_id,
                     f"Completed with exit code {result['exit_code']}")
        return result

    except Exception as e:
        # ADHERENCE: Log error
        log_activity(pybee_id, "error", task_id, str(e))
        raise


def log_activity(bee_id: str, event: str, task: str, msg: str):
    """Append to JSONL activity log per PROCESS-0004."""
    import json
    from datetime import datetime, timezone

    log_path = f".deia/bot-logs/{bee_id}-activity.jsonl"
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "bee": bee_id,
        "event": event,
        "task": task,
        "msg": msg
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

### A.3 Task Ownership Rules

PyBees MUST NOT take work from other bees:

```python
def can_claim_task(task_path: str, pybee_id: str) -> bool:
    """Check if task is available per PROCESS-0002."""

    # Task must be in queue/, not claimed/
    if "/claimed/" in task_path:
        return False  # Already owned by another bee

    if "/queue/" not in task_path:
        return False  # Not in claimable state

    return True
```

### A.4 Response Format

PyBee output MUST follow standard response format:

```json
{
  "status": "success" | "failed" | "blocked",
  "pybee_id": "PYBEE-001",
  "task_id": "TASK-XXX",
  "timestamp": "2026-02-04T17:00:00Z",
  "output": { ... },
  "error": null | "error message",
  "files_modified": ["path/to/file.py"],
  "adherence": {
    "logged": true,
    "claimed": true,
    "process_checked": true
  }
}
```

### A.5 Enforcement

| Violation | Consequence |
|-----------|-------------|
| No activity log entry | Warning, output flagged |
| Taking claimed task | Execution rejected, escalation |
| Skipping claim protocol | Task not counted as complete |
| Fabricated logs | PyBee disabled, integrity review |

### A.6 Why This Matters

> **"The processes exist. They're LLM-agnostic. PyBees are not exempt because they're 'just code'. A bee is a bee. Follow the rules."**
>
> — Q33N

---

**— End of Spec —**
