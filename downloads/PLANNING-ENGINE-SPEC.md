# RAQCOON Planning Engine Specification

**Version**: 1.0  
**Date**: 2026-01-23  
**Timeline**: 1 week  
**Status**: Draft  

---

## 1. Overview & Goals

### 1.1 Purpose

Build a Planning Engine that transforms specifications (PRDs) into executable task graphs, coordinates AI agents via skills, and orchestrates multi-step workflows—enabling "spec in → code out" automation.

### 1.2 Goals

| ID | Goal | Success Metric |
|----|------|----------------|
| G1 | Accept specs in markdown or JSON format | Both formats parse to same internal structure |
| G2 | Generate task graphs with dependencies | Tasks created with correct ordering and routing |
| G3 | Deliver skills to bees via KB injection | Skills appear in task context |
| G4 | Execute workflows with pause/resume capability | Human gates halt and resume execution |
| G5 | Parallel frontend/backend development | Both tracks work from shared contracts |

### 1.3 Non-Goals (Out of Scope)

- Canvas UI for visual workflow editing (Phase 2)
- Real-time WebSocket updates (defer)
- Minder auto-integration (defer)
- Local LLM lane support (future)

### 1.4 Dependencies

These existing gaps must be fixed as prerequisites:

| Gap | Why Needed |
|-----|------------|
| Router wiring | Workflow engine routes tasks by intent |
| KB injection | Skills delivered to bees via KB system |
| Gate enforcement | Pause/resume requires working gates |

---

## 2. Architecture

### 2.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW ENGINE                          │
│  Orchestrates multi-step flows, manages execution state      │
│  Storage: .deia/hive/workflows/                              │
├─────────────────────────────────────────────────────────────┤
│                      SPEC ENGINE                             │
│  Parses PRDs (md/json) → generates task graphs               │
│  Storage: .deia/hive/specs/                                  │
├─────────────────────────────────────────────────────────────┤
│                     SKILL LIBRARY                            │
│  KB entities (type=SKILL) defining agent behaviors           │
│  Storage: kb/kb.json (existing)                              │
├─────────────────────────────────────────────────────────────┤
│                    HIVE RUNTIME                              │
│  Existing: router, task files, bees, flights, gates          │
│  Storage: .deia/hive/tasks/, SQLite stores                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
[Spec Input (md/json)]
        │
        ▼
[Spec Parser] ──validates──▶ [Spec Storage]
        │
        ▼
[Task Graph Generator]
        │
        ▼
[Workflow Engine] ◀──selects──▶ [Skill Library]
        │
        ├──▶ [Router] ──▶ lane assignment
        │
        ├──▶ [KB Injection] ──▶ skill + rules + snippets
        │
        ├──▶ [Task Creation] ──▶ .deia/hive/tasks/{bot}/
        │
        ├──▶ [Gate Check] ──▶ pause if gate closed
        │
        ▼
[Bee Execution] ──▶ [Response Collection] ──▶ [Next Step or Complete]
```

### 2.3 File Structure (New)

```
deia_raqcoon/
├── core/
│   ├── router.py          # EXISTS - needs wiring
│   ├── task_files.py      # EXISTS
│   └── skill_selector.py  # NEW - matches intent to skill
├── runtime/
│   ├── server.py          # EXISTS - add new endpoints
│   ├── spec_parser.py     # NEW - md/json to internal format
│   ├── task_graph.py      # NEW - spec to task DAG
│   └── workflow_engine.py # NEW - execution orchestration
├── schemas/
│   ├── task_file.json     # EXISTS
│   ├── spec.json          # NEW - spec schema
│   └── workflow.json      # NEW - workflow schema
└── kb/
    ├── store.py           # EXISTS - add SKILL type
    ├── kb.json            # EXISTS - stores skills
    └── skills/            # NEW - skill markdown files (source)
        ├── Q33N.md
        ├── SPEC-ANALYST.md
        ├── ARCHITECT.md
        ├── CODE-WRITER.md
        ├── CODE-REVIEWER.md
        ├── TESTER.md
        ├── DOCS-WRITER.md
        └── DEBUGGER.md

.deia/hive/
├── tasks/                 # EXISTS
├── responses/             # EXISTS
├── archive/               # EXISTS
├── specs/                 # NEW - spec files
│   └── SPEC-001.json
└── workflows/             # NEW - workflow definitions + state
    ├── definitions/
    │   └── WF-SPRINT.json
    └── runs/
        └── RUN-001.json
```

---

## 3. Shared Contracts

These schemas and API signatures are the synchronization points between frontend and backend tracks.

### 3.1 Spec Schema (`schemas/spec.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["spec_id", "title", "problem", "requirements"],
  "properties": {
    "spec_id": {
      "type": "string",
      "pattern": "^SPEC-[0-9]{3,}$"
    },
    "title": {
      "type": "string",
      "maxLength": 200
    },
    "version": {
      "type": "string",
      "default": "1.0"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "author": {
      "type": "string",
      "enum": ["human", "q33n"]
    },
    "problem": {
      "type": "object",
      "required": ["statement"],
      "properties": {
        "statement": { "type": "string" },
        "impact": { "type": "string" }
      }
    },
    "goals": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "description"],
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "metric": { "type": "string" }
        }
      }
    },
    "user_stories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "role", "want", "so_that"],
        "properties": {
          "id": { "type": "string" },
          "role": { "type": "string" },
          "want": { "type": "string" },
          "so_that": { "type": "string" },
          "acceptance": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "requirements": {
      "type": "object",
      "properties": {
        "functional": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "description"],
            "properties": {
              "id": { "type": "string" },
              "story_ref": { "type": "string" },
              "description": { "type": "string" },
              "priority": {
                "type": "string",
                "enum": ["must", "should", "could", "wont"]
              },
              "intent": {
                "type": "string",
                "enum": ["design", "code", "test", "docs", "review"]
              }
            }
          }
        },
        "non_functional": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "description"],
            "properties": {
              "id": { "type": "string" },
              "description": { "type": "string" },
              "category": { "type": "string" }
            }
          }
        }
      }
    },
    "constraints": {
      "type": "object",
      "properties": {
        "technical": {
          "type": "array",
          "items": { "type": "string" }
        },
        "timeline": { "type": "string" },
        "dependencies": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "exclusions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "kb_hints": {
      "type": "array",
      "items": { "type": "string" },
      "description": "KB entity IDs to include (rules, snippets, skills)"
    }
  }
}
```

### 3.2 Workflow Schema (`schemas/workflow.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["workflow_id", "title", "nodes", "edges"],
  "properties": {
    "workflow_id": {
      "type": "string",
      "pattern": "^WF-[A-Z0-9-]+$"
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "version": {
      "type": "string",
      "default": "1.0"
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "label"],
        "properties": {
          "id": { "type": "string" },
          "type": {
            "type": "string",
            "enum": [
              "trigger.manual",
              "trigger.webhook",
              "trigger.file_watch",
              "action.create_task",
              "action.launch_bee",
              "action.git_commit",
              "action.git_push",
              "action.kb_inject",
              "action.send_message",
              "action.run_command",
              "logic.condition",
              "logic.loop",
              "logic.merge",
              "logic.delay",
              "gate.human_review",
              "subflow.spec_to_tasks",
              "subflow.execute_task"
            ]
          },
          "label": { "type": "string" },
          "config": { "type": "object" }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "label": { "type": "string" },
          "condition": { "type": "string" }
        }
      }
    }
  }
}
```

### 3.3 Workflow Run State (`schemas/workflow_run.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["run_id", "workflow_id", "status"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^RUN-[0-9]+$"
    },
    "workflow_id": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "paused", "completed", "failed"]
    },
    "started_at": {
      "type": "string",
      "format": "date-time"
    },
    "paused_at": {
      "type": "string",
      "format": "date-time"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time"
    },
    "current_node": {
      "type": "string"
    },
    "inputs": {
      "type": "object"
    },
    "node_outputs": {
      "type": "object",
      "description": "Map of node_id -> output data"
    },
    "error": {
      "type": "string"
    }
  }
}
```

### 3.4 Skill Entity Schema (extends KB entity)

```json
{
  "id": "SKILL-CODE-WRITER",
  "type": "SKILL",
  "title": "Code Writer",
  "summary": "Writes implementation code from requirements",
  "tags": ["code", "implement", "build"],
  "delivery_mode": "task_file",
  "load_mode": "situation",
  
  "triggers": {
    "intents": ["code", "implement", "build"],
    "file_patterns": ["*.py", "*.js", "*.ts"]
  },
  "instructions": [
    "1. Read the requirement and acceptance criteria",
    "2. Identify affected files",
    "3. Write minimal code that satisfies criteria",
    "4. Include docstrings",
    "5. Run tests to verify"
  ],
  "output_format": {
    "type": "code_patch",
    "sections": ["files_modified", "test_results", "notes"]
  },
  "quality_checks": [
    "All acceptance criteria addressed",
    "No unrelated changes",
    "Tests pass"
  ]
}
```

### 3.5 API Contracts

#### Spec Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/specs` | `SpecCreateRequest` | `{"spec_id", "path", "created_at"}` |
| GET | `/api/specs` | - | `[{spec summaries}]` |
| GET | `/api/specs/{id}` | - | Full spec object |
| POST | `/api/specs/{id}/plan` | `{"options": {}}` | `{"task_graph": [...], "task_count"}` |
| POST | `/api/specs/parse` | `{"content": "...", "format": "md|json"}` | Parsed spec object |

**SpecCreateRequest**:
```json
{
  "content": "string (markdown or json)",
  "format": "md | json",
  "spec_id": "optional - auto-generated if omitted"
}
```

#### Workflow Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/workflows` | Workflow definition | `{"workflow_id", "path"}` |
| GET | `/api/workflows` | - | `[{workflow summaries}]` |
| GET | `/api/workflows/{id}` | - | Full workflow definition |
| PUT | `/api/workflows/{id}` | Workflow definition | `{"updated": true}` |
| POST | `/api/workflows/{id}/run` | `{"inputs": {}}` | `{"run_id", "status"}` |
| GET | `/api/workflows/{id}/runs` | - | `[{run summaries}]` |
| GET | `/api/workflows/{id}/runs/{run_id}` | - | Full run state |
| POST | `/api/workflows/{id}/runs/{run_id}/resume` | `{"approval": true}` | `{"status"}` |
| POST | `/api/workflows/{id}/runs/{run_id}/cancel` | - | `{"status": "cancelled"}` |

#### Skill Endpoints (via existing KB API)

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/kb/entities?type=SKILL` | Filter by type |
| POST | `/api/kb/entities` | Create skill (type=SKILL) |
| PUT | `/api/kb/entities/{id}` | Update skill |
| GET | `/api/kb/skills/{id}/preview` | Formatted skill for injection |

### 3.6 Shared Constants

```python
# core/constants.py

SPEC_DIR = ".deia/hive/specs"
WORKFLOW_DIR = ".deia/hive/workflows/definitions"
WORKFLOW_RUNS_DIR = ".deia/hive/workflows/runs"

VALID_INTENTS = ["design", "code", "test", "docs", "review", "debug", "orchestrate"]

VALID_PRIORITIES = ["must", "should", "could", "wont"]

WORKFLOW_STATUSES = ["pending", "running", "paused", "completed", "failed", "cancelled"]

NODE_TYPES = {
    "triggers": ["manual", "webhook", "file_watch"],
    "actions": ["create_task", "launch_bee", "git_commit", "git_push", "kb_inject", "send_message", "run_command"],
    "logic": ["condition", "loop", "merge", "delay"],
    "gates": ["human_review"],
    "subflows": ["spec_to_tasks", "execute_task"]
}

SKILL_IDS = [
    "SKILL-Q33N",
    "SKILL-SPEC-ANALYST", 
    "SKILL-ARCHITECT",
    "SKILL-CODE-WRITER",
    "SKILL-CODE-REVIEWER",
    "SKILL-TESTER",
    "SKILL-DOCS-WRITER",
    "SKILL-DEBUGGER"
]
```

---

## 4. Prerequisites (Existing Gaps)

These must be completed before Planning Engine work begins. Estimated: 4-6 hours total.

### 4.1 Wire Router into Task Creation

**File**: `runtime/server.py`  
**Depends on**: `core/router.py`

**Current state**: `decide_route()` exists but is never called. Tasks bypass routing.

**Required changes**:

```python
# In server.py, import router
from core.router import decide_route

# In create_task() endpoint, after validating request:
route = decide_route({
    "intent": request.intent,
    "title": request.title,
    "kb_entities": request.kb_entities
})

# Include routing in task payload
payload = {
    ...existing fields...,
    "lane": route.lane,
    "provider": route.provider,
    "delivery": route.delivery
}
```

**Acceptance**: Task JSON files include `lane`, `provider`, `delivery` fields based on intent.

---

### 4.2 Implement KB Injection into Tasks

**File**: `runtime/server.py`  
**Depends on**: `kb/store.py`

**Current state**: `kb_entities` IDs stored but content never injected.

**Required changes**:

```python
# In create_task(), after routing:
if request.kb_entities:
    injected_content = preview_injection(request.kb_entities)
    payload["kb_context"] = injected_content
```

**Acceptance**: Task JSON files include `kb_context` field with actual KB content.

---

### 4.3 Complete Gate Enforcement

**File**: `runtime/server.py`

**Current state**: `allow_flight_commits` gate defined but not checked.

**Required changes**:

```python
# In git_commit(), add check:
if not _gates.get("allow_flight_commits", False):
    raise HTTPException(403, "Flight commits not enabled")
```

**Acceptance**: All three gates (`allow_q33n_git`, `pre_sprint_review`, `allow_flight_commits`) enforced.

---

### 4.4 Add SKILL Type to KB Store

**File**: `kb/store.py`

**Current state**: `ALLOWED_TYPES = {"RULE", "SNIPPET"}`

**Required changes**:

```python
ALLOWED_TYPES = {"RULE", "SNIPPET", "SKILL"}

# Add skill-specific validation in upsert_entity():
if entity.get("type") == "SKILL":
    required = ["triggers", "instructions", "output_format"]
    for field in required:
        if field not in entity:
            raise ValueError(f"SKILL requires {field}")
```

**Acceptance**: Can create/update KB entities with `type: "SKILL"`.

---

## 5. Backend Track

Tasks for the backend bee. All work in Python, modifying existing files or creating new modules.

### 5.1 Spec Parser Module

**New file**: `runtime/spec_parser.py`

**Purpose**: Parse markdown or JSON specs into internal format.

**Functions**:

| Function | Input | Output |
|----------|-------|--------|
| `parse_spec(content, format)` | Raw string, "md" or "json" | Validated spec dict |
| `parse_markdown_spec(content)` | Markdown string | Spec dict |
| `parse_json_spec(content)` | JSON string | Spec dict |
| `validate_spec(spec)` | Spec dict | Raises on invalid |

**Markdown parsing rules**:
- `# Title` → `spec.title`
- `## Problem` → `spec.problem.statement`
- `## Goals` → `spec.goals[]` (numbered list)
- `## User Stories` → `spec.user_stories[]`
- `## Requirements` → `spec.requirements.functional[]`
- `## Constraints` → `spec.constraints`
- `## Exclusions` → `spec.exclusions[]`
- `## KB Hints` → `spec.kb_hints[]`

**Acceptance**: Both formats produce identical internal structure. Invalid specs raise clear errors.

---

### 5.2 Task Graph Generator

**New file**: `runtime/task_graph.py`

**Purpose**: Convert spec into executable task DAG.

**Functions**:

| Function | Input | Output |
|----------|-------|--------|
| `generate_task_graph(spec)` | Spec dict | List of task dicts with dependencies |
| `infer_dependencies(requirements)` | Requirements list | Dependency map |
| `assign_skills(tasks)` | Task list | Tasks with skill_id assigned |
| `topological_sort(tasks)` | Tasks with deps | Ordered task list |

**Task generation rules**:
- Each functional requirement → 1 task
- Intent inferred from requirement description if not explicit
- Dependencies inferred from `story_ref` relationships
- `kb_hints` from spec attached to all tasks
- Skill assigned based on intent

**Output task structure**:
```json
{
  "task_id": "TASK-001",
  "spec_id": "SPEC-001",
  "requirement_id": "FR1",
  "title": "...",
  "description": "...",
  "intent": "code",
  "skill_id": "SKILL-CODE-WRITER",
  "dependencies": ["TASK-000"],
  "acceptance_criteria": ["..."],
  "kb_entities": ["RULE-001", "SKILL-CODE-WRITER"],
  "status": "pending"
}
```

**Acceptance**: Spec with 5 requirements produces 5 tasks with correct ordering.

---

### 5.3 Skill Selector

**New file**: `core/skill_selector.py`

**Purpose**: Match task intent to appropriate skill.

**Functions**:

| Function | Input | Output |
|----------|-------|--------|
| `select_skill(intent, context)` | Intent string, optional context | Skill ID |
| `load_skills()` | - | List of skill entities from KB |
| `match_intent(intent, skill)` | Intent, skill entity | Boolean |

**Matching logic**:
```python
def select_skill(intent, context=None):
    skills = load_skills()
    
    # Exact match on triggers.intents
    for skill in skills:
        if intent in skill.get("triggers", {}).get("intents", []):
            return skill["id"]
    
    # Fallback mapping
    fallbacks = {
        "design": "SKILL-ARCHITECT",
        "code": "SKILL-CODE-WRITER",
        "implement": "SKILL-CODE-WRITER",
        "test": "SKILL-TESTER",
        "review": "SKILL-CODE-REVIEWER",
        "docs": "SKILL-DOCS-WRITER",
        "debug": "SKILL-DEBUGGER",
        "orchestrate": "SKILL-Q33N"
    }
    return fallbacks.get(intent, "SKILL-CODE-WRITER")
```

**Acceptance**: Each valid intent resolves to correct skill.

---

### 5.4 Workflow Engine

**New file**: `runtime/workflow_engine.py`

**Purpose**: Execute workflow definitions, manage state, handle pause/resume.

**Class**: `WorkflowEngine`

**Methods**:

| Method | Purpose |
|--------|---------|
| `__init__(workflow_dir, runs_dir)` | Initialize with paths |
| `load_workflow(workflow_id)` | Load definition from JSON |
| `start_run(workflow_id, inputs)` | Create run state, begin execution |
| `execute_node(run, node)` | Execute single node, return output |
| `advance(run)` | Move to next node(s) based on edges |
| `pause(run_id, gate_name)` | Persist state, set status=paused |
| `resume(run_id, approval_data)` | Reload state, continue execution |
| `cancel(run_id)` | Set status=cancelled |
| `get_run_state(run_id)` | Return current run state |

**Node execution dispatch**:
```python
def execute_node(self, run, node):
    node_type = node["type"]
    config = node.get("config", {})
    
    handlers = {
        "trigger.manual": self._handle_manual_trigger,
        "action.create_task": self._handle_create_task,
        "action.launch_bee": self._handle_launch_bee,
        "action.git_commit": self._handle_git_commit,
        "logic.condition": self._handle_condition,
        "logic.loop": self._handle_loop,
        "gate.human_review": self._handle_gate,
        "subflow.spec_to_tasks": self._handle_spec_to_tasks,
        "subflow.execute_task": self._handle_execute_task,
    }
    
    handler = handlers.get(node_type)
    if not handler:
        raise ValueError(f"Unknown node type: {node_type}")
    
    return handler(run, config)
```

**State persistence**: JSON files in `.deia/hive/workflows/runs/`

**Acceptance**: 
- Workflow runs to completion
- Pauses at gate nodes
- Resumes after approval
- State survives process restart

---

### 5.5 Spec API Endpoints

**File**: `runtime/server.py`

**New endpoints**:

```python
@app.post("/api/specs")
def create_spec(request: SpecCreateRequest) -> Dict:
    """Parse and store a new spec."""
    
@app.get("/api/specs")
def list_specs() -> List[Dict]:
    """List all specs with summaries."""

@app.get("/api/specs/{spec_id}")
def get_spec(spec_id: str) -> Dict:
    """Get full spec by ID."""

@app.post("/api/specs/{spec_id}/plan")
def plan_spec(spec_id: str, options: PlanOptions = None) -> Dict:
    """Generate task graph from spec."""

@app.post("/api/specs/parse")
def parse_spec_preview(request: SpecParseRequest) -> Dict:
    """Parse spec without storing (preview)."""
```

**Models**:
```python
class SpecCreateRequest(BaseModel):
    content: str
    format: str  # "md" or "json"
    spec_id: Optional[str] = None

class SpecParseRequest(BaseModel):
    content: str
    format: str

class PlanOptions(BaseModel):
    auto_create_tasks: bool = False
    bot_id: Optional[str] = None
```

---

### 5.6 Workflow API Endpoints

**File**: `runtime/server.py`

**New endpoints**:

```python
@app.post("/api/workflows")
def create_workflow(workflow: WorkflowDefinition) -> Dict:
    """Store a new workflow definition."""

@app.get("/api/workflows")
def list_workflows() -> List[Dict]:
    """List all workflow definitions."""

@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: str) -> Dict:
    """Get workflow definition."""

@app.put("/api/workflows/{workflow_id}")
def update_workflow(workflow_id: str, workflow: WorkflowDefinition) -> Dict:
    """Update workflow definition."""

@app.post("/api/workflows/{workflow_id}/run")
def run_workflow(workflow_id: str, request: WorkflowRunRequest) -> Dict:
    """Start a workflow run."""

@app.get("/api/workflows/{workflow_id}/runs")
def list_workflow_runs(workflow_id: str) -> List[Dict]:
    """List runs for a workflow."""

@app.get("/api/workflows/{workflow_id}/runs/{run_id}")
def get_workflow_run(workflow_id: str, run_id: str) -> Dict:
    """Get run state."""

@app.post("/api/workflows/{workflow_id}/runs/{run_id}/resume")
def resume_workflow_run(workflow_id: str, run_id: str, request: ResumeRequest) -> Dict:
    """Resume a paused run."""

@app.post("/api/workflows/{workflow_id}/runs/{run_id}/cancel")
def cancel_workflow_run(workflow_id: str, run_id: str) -> Dict:
    """Cancel a run."""
```

---

### 5.7 Create Initial Skills

**Location**: `kb/skills/` (source markdown) → `kb/kb.json` (loaded)

Create 8 skill files, then load into KB:

| File | Skill ID | Primary Intents |
|------|----------|-----------------|
| Q33N.md | SKILL-Q33N | orchestrate, coordinate, plan |
| SPEC-ANALYST.md | SKILL-SPEC-ANALYST | analyze, review spec |
| ARCHITECT.md | SKILL-ARCHITECT | design, architecture |
| CODE-WRITER.md | SKILL-CODE-WRITER | code, implement, build |
| CODE-REVIEWER.md | SKILL-CODE-REVIEWER | review, audit |
| TESTER.md | SKILL-TESTER | test, verify, qa |
| DOCS-WRITER.md | SKILL-DOCS-WRITER | document, explain |
| DEBUGGER.md | SKILL-DEBUGGER | debug, fix, investigate |

**Acceptance**: All 8 skills loadable via `/api/kb/entities?type=SKILL`.

---

## 6. Frontend Track

Tasks for the frontend bee. Focus on UI components that connect to new backend APIs.

### 6.1 Spec Editor Page

**New file**: `docs/mockups/spec-editor.html`

**Features**:
- Textarea for markdown or JSON input
- Format toggle (md/json)
- "Parse Preview" button → calls `/api/specs/parse`
- "Save Spec" button → calls `POST /api/specs`
- Display parsed spec structure
- Show validation errors

**API calls**:
- `POST /api/specs/parse` - preview
- `POST /api/specs` - save
- `GET /api/specs` - list existing

---

### 6.2 Spec List View

**Add to**: `docs/mockups/hive-project.html` or new page

**Features**:
- Table of specs (id, title, created_at, author)
- Click row → view spec detail
- "Plan Tasks" button → calls `/api/specs/{id}/plan`
- Show generated task count

**API calls**:
- `GET /api/specs`
- `GET /api/specs/{id}`
- `POST /api/specs/{id}/plan`

---

### 6.3 Task Graph Visualization

**New file**: `docs/mockups/task-graph.html`

**Features**:
- Display tasks as nodes
- Show dependencies as edges
- Color by status (pending, running, completed, blocked)
- Click node → show task detail
- Show skill assignment per task

**Implementation**: Use simple SVG or CSS-based layout (Canvas UI deferred).

**Data source**: Output of `/api/specs/{id}/plan`

---

### 6.4 Workflow Run Dashboard

**New file**: `docs/mockups/workflow-dashboard.html`

**Features**:
- List active/recent workflow runs
- Show run status (running, paused, completed, failed)
- Progress indicator (current node)
- "Resume" button for paused runs
- "Cancel" button for active runs
- Expand to see node execution log

**API calls**:
- `GET /api/workflows`
- `GET /api/workflows/{id}/runs`
- `GET /api/workflows/{id}/runs/{run_id}`
- `POST /api/workflows/{id}/runs/{run_id}/resume`
- `POST /api/workflows/{id}/runs/{run_id}/cancel`

---

### 6.5 Skill Browser

**Add to**: `docs/mockups/kb-editor.html`

**Features**:
- Filter KB entities by type=SKILL
- Display skill cards with:
  - Title, summary
  - Trigger intents
  - Instructions preview
- Click to expand full skill
- (Editing deferred—bots edit via files)

**API calls**:
- `GET /api/kb/entities?type=SKILL`
- `GET /api/kb/entities/{id}`

---

### 6.6 Gate Approval UI

**Add to**: `docs/mockups/workflow-dashboard.html`

**Features**:
- When run status=paused, show approval panel
- Display gate name and context
- "Approve" / "Reject" buttons
- Optional comment field

**API calls**:
- `POST /api/workflows/{id}/runs/{run_id}/resume` with `{"approval": true/false, "comment": "..."}`

---

## 7. Acceptance Criteria

### 7.1 End-to-End Scenarios

**Scenario A: Spec to Tasks**
1. User writes markdown spec in Spec Editor
2. Clicks "Save Spec" → spec stored
3. Clicks "Plan Tasks" → task graph generated
4. Task Graph view shows tasks with dependencies
5. Each task has skill assigned

**Scenario B: Workflow Execution**
1. User triggers workflow via API or UI
2. Workflow runs through nodes
3. Reaches gate node → pauses
4. User approves in Gate Approval UI
5. Workflow resumes and completes

**Scenario C: Skill-Based Task Execution**
1. Task created with intent="code"
2. Router assigns lane, skill selector picks SKILL-CODE-WRITER
3. KB injection includes skill content
4. Task file contains full skill instructions
5. Bee executes with skill guidance

### 7.2 API Acceptance

| Endpoint | Test |
|----------|------|
| POST /api/specs | Returns spec_id, file created |
| GET /api/specs | Returns list with correct count |
| POST /api/specs/{id}/plan | Returns task_graph array |
| POST /api/workflows/{id}/run | Returns run_id, status=running |
| POST /api/.../resume | Status changes from paused to running |

### 7.3 Integration Acceptance

| Integration | Test |
|-------------|------|
| Router + Skills | Task intent maps to correct skill |
| KB + Skills | Skill content appears in task kb_context |
| Workflow + Gates | Run pauses at gate.human_review node |
| Workflow + Tasks | subflow.execute_task creates real task |

---

## 8. Timeline (1 Week)

### Day 1: Prerequisites + Setup

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | Wire router, KB injection, gate enforcement | 3 |
| Backend | Add SKILL type to KB store | 1 |
| Backend | Create skill markdown files (8) | 2 |
| Frontend | Review spec, set up new page stubs | 1 |

**Checkpoint**: Router working, skills in KB, existing MVP fully wired.

---

### Day 2: Spec Engine

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | Build spec_parser.py (md + json) | 3 |
| Backend | Build task_graph.py | 3 |
| Backend | Spec API endpoints | 2 |
| Frontend | Spec Editor page (basic) | 2 |

**Checkpoint**: Can parse spec and generate task graph via API.

---

### Day 3: Skill Integration

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | Build skill_selector.py | 2 |
| Backend | Integrate skill selection into task graph | 2 |
| Backend | Test skill injection end-to-end | 2 |
| Frontend | Skill Browser in KB editor | 2 |
| Frontend | Spec List view | 2 |

**Checkpoint**: Tasks created with correct skill assigned and injected.

---

### Day 4: Workflow Engine Core

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | WorkflowEngine class (load, start, execute) | 4 |
| Backend | Node handlers (actions, logic) | 3 |
| Frontend | Task Graph visualization | 3 |

**Checkpoint**: Simple workflow runs to completion.

---

### Day 5: Workflow State + Gates

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | Pause/resume logic | 2 |
| Backend | State persistence (JSON files) | 2 |
| Backend | Gate node handler | 2 |
| Backend | Workflow API endpoints | 2 |
| Frontend | Workflow Run Dashboard (basic) | 2 |

**Checkpoint**: Workflow pauses at gate, can resume via API.

---

### Day 6: Integration + Polish

| Track | Tasks | Hours |
|-------|-------|-------|
| Backend | Subflow handlers (spec_to_tasks, execute_task) | 3 |
| Backend | Error handling, edge cases | 2 |
| Frontend | Gate Approval UI | 2 |
| Frontend | Polish existing pages | 2 |
| Both | Integration testing | 2 |

**Checkpoint**: Full spec→tasks→workflow→execution path works.

---

### Day 7: Testing + Documentation

| Track | Tasks | Hours |
|-------|-------|-------|
| Both | End-to-end scenario testing | 3 |
| Both | Bug fixes | 2 |
| Backend | Update API docs | 1 |
| Frontend | Update UI mockup docs | 1 |
| Both | Write runbook for Planning Engine | 1 |

**Deliverable**: Planning Engine MVP complete, documented, tested.

---

## 9. Bee Coordination Protocol

Since frontend and backend bees work in parallel, follow these rules:

### 9.1 Sync Points

| Day | Sync Topic |
|-----|------------|
| Day 1 end | Confirm schemas match, API stubs ready |
| Day 3 end | Confirm skill integration working |
| Day 5 end | Confirm workflow API contracts |
| Day 7 | Final integration test |

### 9.2 Contract Changes

If either bee needs to change a shared contract (schema, API):

1. Propose change in task file or message
2. Wait for confirmation before implementing
3. Both bees update simultaneously

### 9.3 File Ownership

| Owner | Files |
|-------|-------|
| Backend | `runtime/*.py`, `core/*.py`, `kb/*.py`, `schemas/*.json` |
| Frontend | `docs/mockups/*.html` |
| Shared | This spec document |

### 9.4 Communication

- Use `/api/messages` with channel `planning-engine-sync`
- Tag messages with bee ID
- Include blockers, questions, status updates

---

## Appendix A: Example Spec (Markdown)

```markdown
# User Authentication Flow

## Problem
Users cannot securely log in to the application.
Impact: Blocks all authenticated features.

## Goals
1. G1: Implement secure OAuth2 login (metric: passes security audit)
2. G2: Session persistence (metric: survives page refresh)

## User Stories
- US1: As an end_user, I want to log in with Google so that I don't need another password.
  - Acceptance: Google OAuth flow works, session persists

## Requirements
- FR1 [must] [code]: Implement Google OAuth2 flow (ref: US1)
- FR2 [must] [code]: Create session management (ref: US1, depends: FR1)
- FR3 [should] [test]: Write auth integration tests (depends: FR1, FR2)
- FR4 [should] [docs]: Document auth flow (depends: FR1)

## Constraints
- Technical: Python 3.13, FastAPI
- Timeline: 3 days
- Dependencies: Google Cloud project configured

## Exclusions
- Password-based auth
- Social logins other than Google

## KB Hints
- RULE-SEC-001
- SNIPPET-OAUTH-CONFIG
```

---

## Appendix B: Example Workflow (JSON)

```json
{
  "workflow_id": "WF-SIMPLE-SPRINT",
  "title": "Simple Sprint Workflow",
  "version": "1.0",
  "nodes": [
    {"id": "start", "type": "trigger.manual", "label": "Start Sprint", "config": {}},
    {"id": "plan", "type": "subflow.spec_to_tasks", "label": "Generate Tasks", "config": {"spec_id": "{{input.spec_id}}"}},
    {"id": "review", "type": "gate.human_review", "label": "Review Plan", "config": {"gate": "pre_sprint_review"}},
    {"id": "loop", "type": "logic.loop", "label": "Each Task", "config": {"items": "{{plan.tasks}}"}},
    {"id": "execute", "type": "subflow.execute_task", "label": "Execute Task", "config": {"task": "{{loop.current}}"}},
    {"id": "commit", "type": "action.git_commit", "label": "Commit", "config": {"message": "Sprint {{input.spec_id}}"}}
  ],
  "edges": [
    {"from": "start", "to": "plan"},
    {"from": "plan", "to": "review"},
    {"from": "review", "to": "loop", "condition": "approved"},
    {"from": "loop", "to": "execute", "label": "each"},
    {"from": "execute", "to": "loop", "label": "next", "condition": "has_more"},
    {"from": "execute", "to": "commit", "condition": "all_done"}
  ]
}
```

---

*End of Planning Engine Specification*
