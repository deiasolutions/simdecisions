# DEIA RAQCOON — Consolidated Specification

**Version**: 1.0  
**Date**: 2026-01-18  
**Status**: MVP in progress (~70% complete)

---

## 1. Vision

### 1.1 Purpose
RAQCOON (Retrieval-Augmented Quality Control & Orchestration for Ops Nodes) is an AI orchestration platform that coordinates multiple AI coding agents through a "hive" architecture.

### 1.2 Goal
**"Spec In → Code Out"** — Transform specifications into working, tested code through coordinated AI agents with human oversight gates.

### 1.3 Architecture
- **Q33N (Queen) Bees**: Orchestrators that coordinate work, review code, manage integration
- **Worker Bees**: Specialized agents handling implementation tasks
- **Hive**: The coordination layer managing task routing, knowledge injection, and communication

---

## 2. Phase Roadmap

### Phase 0: MVP Infrastructure (Current)
Runtime, API, task file loop, CLI bee launch, basic KB, flight tracking.

### Phase 1: Spec Intake + Task Graph
| Deliverable | Type | Description |
|-------------|------|-------------|
| `schemas/spec.json` | Schema | Spec schema: goals, constraints, acceptance criteria, scope exclusions |
| `runtime/spec_parser.py` | Module | Parser to convert markdown/spec into JSON |
| `runtime/task_graph.py` | Module | Break spec into tasks with dependencies, owners, routing lane |
| `POST /api/spec/plan` | Endpoint | Spec-to-tasks flow endpoint |

### Phase 2: Execution Loop + Verification
| Deliverable | Type | Description |
|-------------|------|-------------|
| `runtime/executor.py` | Module | Pull tasks, route to lane, collect responses, mark complete/blocked |
| `runtime/verifier.py` | Module | Hook test/lint commands, capture results into task history |
| `POST /api/tasks/run` | Endpoint | Execute tasks |
| `POST /api/tasks/verify` | Endpoint | Run verification/tests |

### Phase 3: Git Automation + Gates
| Deliverable | Type | Description |
|-------------|------|-------------|
| `runtime/git_flow.py` | Module | Patch assembly, staging, commit workflow |
| Gate-integrated pipeline | Feature | Pre-sprint review, per-flight commit permission, human override |

### Phase 4: Observability + Cost Controls
| Deliverable | Type | Description |
|-------------|------|-------------|
| `runtime/telemetry.py` | Module | Token/provider cost per message, per-task aggregation |
| `/api/summary` extensions | Endpoint | Cost + per-flight stats in summary |
| Dashboards | UI | Flight performance dashboards |

### Phase 5: Advanced RAQCOON (Quality + Safety)
| Deliverable | Type | Description |
|-------------|------|-------------|
| KB policy engine | Module | Rule enforcement per task type |
| Rule-based blockers | Feature | Block execution before bad patterns |
| Retrieval policies | Feature | Strict mode for critical paths (security, infra, payments) |

### Phase 6: Full "Spec In → Code Out" Workflow
| Deliverable | Type | Description |
|-------------|------|-------------|
| "Run Spec" button | UI | Single UI action to trigger full workflow |
| End-to-end status | Feature | Flight checkpoints and status tracking |

**Flow**: Spec uploaded → Planner creates tasks → Executor runs → Verifier tests → Git stages → Human approves → Push

---

## 3. Module Structure

```
deia_raqcoon/
├── core/                  # Core orchestration, state, routing
│   ├── router.py          # Task routing by intent
│   └── task_files.py      # Task file read/write/archive
├── adapters/              # Provider adapters
│   ├── base.py            # Abstract adapter interface
│   ├── cli_adapter.py     # CLI tool launcher
│   └── registry.py        # Adapter factory
├── kb/                    # Knowledge base
│   └── store.py           # KB entity CRUD + injection
├── runtime/               # Runtime services
│   ├── server.py          # FastAPI application
│   ├── store.py           # Message persistence (SQLite)
│   ├── flights.py         # Flight/recap tracking (SQLite)
│   ├── launcher.py        # Repo root preflight
│   ├── minder.py          # Periodic ping service
│   └── pty_bridge.py      # PTY session management
├── schemas/               # JSON schemas
│   └── task_file.json     # Task schema definition
└── docs/                  # Documentation
```

---

## 4. API Specification

### 4.1 MVP Endpoints (Required)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Current config (cwd, repo_root, status) |
| WS | `/api/ws` | WebSocket for real-time messaging |
| POST | `/api/bees/launch` | Launch CLI bee (claude-code/codex) |
| POST | `/api/messages` | Store message with metadata |
| GET | `/api/messages` | Retrieve messages (optional channel filter) |
| GET | `/api/channels` | List unique channel IDs |
| GET | `/api/summary` | Aggregate message stats |
| POST | `/api/tasks` | Create task file |
| POST | `/api/tasks/complete` | Archive completed task |
| GET | `/api/tasks/response` | Get latest response file path |
| GET | `/api/git/status` | Run `git status -sb` |
| POST | `/api/git/commit` | Commit with gate checks |
| POST | `/api/git/push` | Push with gate checks |
| GET | `/api/gates` | Get current gate flags |
| POST | `/api/gates` | Update gate flags |
| POST | `/api/flights/start` | Start flight tracking |
| POST | `/api/flights/end` | End flight tracking |
| POST | `/api/flights/recap` | Add recap to flight |
| GET | `/api/flights` | List all flights |
| GET | `/api/flights/recaps` | List recaps (optional flight filter) |

### 4.2 KB Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/kb/entities` | List all KB entities |
| POST | `/api/kb/entities` | Create/upsert entity |
| PUT | `/api/kb/entities/{id}` | Update entity by ID |
| POST | `/api/kb/preview` | Preview formatted injection |

### 4.3 PTY Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/pty/start` | Start PTY session |
| POST | `/api/pty/send` | Send data to PTY |
| GET | `/api/pty/read` | Read PTY output buffer |
| POST | `/api/pty/stop` | Stop PTY session |

### 4.4 Phase 1+ Endpoints (Planned)

| Method | Path | Phase | Purpose |
|--------|------|-------|---------|
| POST | `/api/spec/plan` | 1 | Convert spec to task graph |
| POST | `/api/tasks/run` | 2 | Execute task |
| POST | `/api/tasks/verify` | 2 | Run verification |

---

## 5. Data Models

### 5.1 Task Request
```json
{
  "bot_id": "string",
  "task_id": "string (optional, auto-generated)",
  "intent": "string (design|planning|code|...)",
  "title": "string",
  "summary": "string",
  "kb_entities": ["entity_id_1", "entity_id_2"],
  "delivery_mode": "cache_prompt|task_file|both",
  "repo_root": "string (optional)"
}
```

### 5.2 Task File Schema
```json
{
  "task_id": "string",
  "bot_id": "string",
  "intent": "string",
  "title": "string",
  "summary": "string",
  "kb_entities": ["string"],
  "delivery_mode": "string",
  "status": "pending|in_progress|completed|blocked",
  "created_at": "ISO timestamp",
  "completed_at": "ISO timestamp (optional)"
}
```

### 5.3 Message Request
```json
{
  "channel_id": "string",
  "author": "string",
  "content": "string",
  "lane": "string (optional)",
  "provider": "string (optional)",
  "token_count": "integer (optional)"
}
```

### 5.4 KB Entity
```json
{
  "id": "string (e.g., RULE-001)",
  "type": "RULE|SNIPPET|PLAYBOOK|PATTERN|CHECKLIST|REFERENCE",
  "title": "string",
  "summary": "string",
  "tags": ["string"],
  "delivery_mode": "cache_prompt|task_file|both",
  "load_mode": "always|situation|on_demand",
  "attachments": ["string (optional)"]
}
```

---

## 6. Routing System

### 6.1 Lanes
| Lane | Purpose | Provider |
|------|---------|----------|
| `llm` | LLM API calls (design, planning) | default |
| `terminal` | CLI tool execution (code) | cli |

### 6.2 Routing Logic
```
Intent "design" or "planning" → lane=llm, delivery=cache_prompt
Intent "code" → lane=terminal, delivery=task_file
Default → lane=llm, delivery=cache_prompt
```

### 6.3 Route Decision
```python
@dataclass
class RouteDecision:
    lane: str       # "llm" or "terminal"
    provider: str   # "default" or "cli"
    delivery: str   # "cache_prompt" or "task_file"
```

---

## 7. Gate System

### 7.1 Gate Flags
| Gate | Purpose | Default |
|------|---------|---------|
| `allow_q33n_git` | Q33N git commit/push permission | False |
| `pre_sprint_review` | Human review before sprint | False |
| `allow_flight_commits` | Auto-commits during flight | False |

### 7.2 Gate Flow
```
Start Flight
    ↓
pre_sprint_review = true? → No → Block commits
    ↓ Yes
allow_flight_commits = true? → No → Require manual commit
    ↓ Yes
allow_q33n_git = true? → No → Block push
    ↓ Yes
Auto-commit + push allowed
```

---

## 8. Knowledge Base (RAQCOON)

### 8.1 Entity Types
| Type | Purpose | Example |
|------|---------|---------|
| RULE | Dos/don'ts, guardrails | "Never commit secrets" |
| SNIPPET | Configs, code fragments | vercel.json template |
| PLAYBOOK | Step-by-step procedures | Deploy to Vercel |
| PATTERN | Design/architecture patterns | Repository pattern |
| CHECKLIST | Release and QA gates | Pre-release checklist |
| REFERENCE | Docs, links, context | API documentation |

### 8.2 Delivery Modes
| Mode | Behavior |
|------|----------|
| `cache_prompt` | Inject into LLM system prompt |
| `task_file` | Include in task file for terminal bees |
| `both` | Use both methods |

### 8.3 Load Modes
| Mode | Behavior |
|------|----------|
| `always` | Always load |
| `situation` | Load based on task intent/domain |
| `on_demand` | Only when explicitly requested |

---

## 9. File System Layout

### 9.1 Hive Directory Structure
```
.deia/
├── hive/
│   ├── tasks/
│   │   └── {bot_id}/
│   │       └── {timestamp}-{task_id}.json
│   ├── responses/
│   │   └── {task_id}.md
│   └── archive/
│       └── {bot_id}/
│           └── {timestamp}-{task_id}.json
├── raqcoon_messages.db    # SQLite message store
└── raqcoon_flights.db     # SQLite flight store
```

### 9.2 KB Storage
```
kb/
└── kb.json                # KB entity store
```

---

## 10. CLI Adapters

### 10.1 Supported Tools
| Tool | Env Variable | Default Command |
|------|--------------|-----------------|
| Claude Code | `DEIA_CLAUDE_CMD` | `claude` |
| Codex | `DEIA_CODEX_CMD` | `codex` |

### 10.2 Launch Requirements
1. Preflight: detect repo root (`.deia` directory)
2. Prompt if not at repo root
3. `chdir` to repo root before process spawn
4. Launch in new console window

---

## 11. Configuration

### 11.1 Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `DEIA_CLAUDE_CMD` | Claude CLI executable | `claude` |
| `DEIA_CLAUDE_ARGS` | Additional Claude args | `""` |
| `DEIA_CODEX_CMD` | Codex CLI executable | `codex` |
| `DEIA_CODEX_ARGS` | Additional Codex args | `""` |

### 11.2 Hardcoded Defaults
| Value | Purpose |
|-------|---------|
| `127.0.0.1:8010` | Server host:port |
| `600` seconds | Minder ping interval |
| `200` | Message fetch limit |
| `4000` | PTY read max chars |

---

## 12. Exit Criteria (MVP Complete)

| # | Criterion |
|---|-----------|
| E1 | Launch local API + UI from repo root |
| E2 | Start Claude Code + Codex CLI bees from UI |
| E3 | Send a task and receive a response via task file loop |
| E4 | Inject a RULE or SNIPPET into a task or prompt |
| E5 | Repo root discipline enforced |
| E6 | Git status viewable |
| E7 | Gates block unauthorized commits |
| E8 | Flight start/end/recap workflow functional |
| E9 | Messages stored with lane/provider metadata |

---

## 13. Current Implementation Status

### 13.1 Working
- FastAPI server (27 endpoints)
- Task file loop (write/read/archive)
- Flight tracking + recaps
- CLI bee launch with repo-root discipline
- KB entity storage + preview
- Message persistence with metadata
- Gate flag management

### 13.2 Implemented but Disconnected
| Component | Issue |
|-----------|-------|
| Router (`decide_route()`) | Never called—tasks bypass routing |
| KB injection | Entity IDs stored but content not injected |
| WebSocket | Echo-only, no broadcasting |
| `allow_flight_commits` gate | Defined but not enforced |
| Minder | Standalone script, not integrated |

### 13.3 Not Implemented
- Phase 1: `/api/spec/plan`, spec_parser.py, task_graph.py
- Phase 2: `/api/tasks/run`, `/api/tasks/verify`, executor.py, verifier.py
- Phase 3: git_flow.py
- Phase 4: telemetry.py

---

## 14. Appendix: Quick Reference

### API Base URL
```
http://127.0.0.1:8010
```

### Launch Command
```bash
# Windows
run-local-hive.bat

# Manual
python -m deia_raqcoon.runtime.run_server
```

### Task File Path Pattern
```
.deia/hive/tasks/{bot_id}/{timestamp}-{task_id}.json
```

### Response File Path Pattern
```
.deia/hive/responses/{task_id}.md
```

---

*End of Consolidated Specification*
