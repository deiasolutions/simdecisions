# SimDecisions

**Design any system of interacting agents. Run it. Measure results.**

SimDecisions is an organizational simulation and execution platform. It lets you model teams of AI agents, human approval gates, and automated processes — then run them in production or simulate them statistically for capacity planning and what-if analysis.

---

## What It Does

**Two modes, one engine:**

1. **Production Mode** — Real AI agents (Claude, GPT, Gemini, local Llama) produce real outputs: code, documents, research, designs. Coordinated through a hive architecture with human oversight gates.

2. **Simulation Mode** — Statistical work arrivals (Poisson), queue disciplines, routing rules, agent scheduling. Pause, branch, compare variants. Capacity planning without burning tokens.

**Agent types supported:** LLM agents, Python scripts, human approval gates, queues, workflows, external APIs.

---

## Why This Exists

Every multi-agent framework lets you run agents. None of them let you measure what happened, simulate what-if alternatives, or govern the agents constitutionally.

| Category | They Do | We Do |
|----------|---------|-------|
| Process simulators (Arena, Simio) | Model | Execute |
| AI frameworks (AutoGen, CrewAI) | Execute | Measure |
| Workflow tools (n8n, Zapier) | Coordinate | Simulate |
| Org design (Figma, Miro) | Visualize | Run |

SimDecisions does all four.

---

## Current State (February 2026)

| Component | Status |
|-----------|--------|
| FastAPI server (26 REST + 1 WebSocket) | Working |
| Task file loop (create → route → execute → archive) | Working |
| Multi-LLM adapters (Claude Code, Codex, Gemini) | Working |
| Intent-based router | Wired |
| Knowledge base injection | Wired |
| WebSocket real-time updates | Wired |
| Gate enforcement (3 gates) | Complete |
| Flight tracking + recaps | Working |
| BOK (32 patterns) | Working |
| Event ledger | Phase 2 — building now |
| DES simulation engine | Phase 3 — next |
| Visual UI | Phase 4 — planned |

**Phase 2 (current):** Metrics & Observability — event ledger, cost tracking, dashboard, export.

---

## Architecture

```
src/deia/
├── hivemind/              # HiveMind runtime (the engine)
│   ├── core/              # Router, skill selector, task files
│   ├── adapters/          # CLI, headless, Gemini adapters
│   ├── runtime/           # FastAPI server, flights, store, launcher
│   │   ├── server.py      # Main API (26 endpoints)
│   │   ├── store.py       # SQLite message persistence
│   │   ├── flights.py     # Flight/sprint tracking
│   │   ├── launcher.py    # Repo root preflight
│   │   ├── pty_bridge.py  # PTY session management
│   │   ├── minder.py      # Periodic health pings
│   │   └── run_server.py  # Entry point (uvicorn)
│   ├── kb/                # Knowledge base (entities, injection)
│   ├── schemas/           # JSON schemas (task_file.json)
│   ├── ui/                # Web interface mockups
│   ├── mcp/               # Model Context Protocol server
│   └── sdk_bridge/        # TypeScript SDK bridge
├── adapters/              # External LLM adapters
├── services/              # Core DEIA services
└── cli/                   # CLI entry points
```

### Key Modules

| Module | Location | Purpose |
|--------|----------|---------|
| **server.py** | `hivemind/runtime/` | FastAPI app, all REST/WebSocket endpoints |
| **router.py** | `hivemind/core/` | Intent-based routing (design→llm, code→terminal) |
| **task_files.py** | `hivemind/core/` | Write/complete/archive task JSON files |
| **store.py** | `hivemind/runtime/` | SQLite message persistence + aggregation |
| **flights.py** | `hivemind/runtime/` | Flight (sprint) tracking + recaps |
| **kb/store.py** | `hivemind/kb/` | Knowledge base CRUD + injection preview |
| **registry.py** | `hivemind/adapters/` | CLI adapter factory (Claude, Codex, Gemini) |
| **launcher.py** | `hivemind/runtime/` | Repo root detection + preflight checks |

---

## How to Run

### Prerequisites

- Python 3.13+
- pip packages: `fastapi`, `uvicorn`, `pydantic`, `requests`
- At least one CLI agent installed: `claude` (Claude Code), `codex`, or `gemini`
- Git repo with a `.deia/` directory at root

### 1. Install Dependencies

```bash
cd deiasolutions-2
pip install fastapi uvicorn pydantic requests
```

### 2. Start the API Server

```bash
python src/deia/hivemind/runtime/run_server.py
```

Server starts at `http://127.0.0.1:8010`. Verify:

```bash
curl http://127.0.0.1:8010/api/health
# → {"status": "ok"}
```

### 3. Set Repo Root

```bash
curl http://127.0.0.1:8010/api/config
# Returns cwd, repo_root, repo_status
```

If repo root is not detected, the system will prompt. The repo root must contain a `.deia/` directory.

### 4. Launch a Bee (CLI Agent)

```bash
curl -X POST http://127.0.0.1:8010/api/bees/launch \
  -H "Content-Type: application/json" \
  -d '{"tool": "claude-code", "confirm": true}'
```

Optional env overrides:
- `DEIA_CLAUDE_CMD` — full path to Claude Code binary (default: `claude`)
- `DEIA_CODEX_CMD` — full path to Codex binary (default: `codex`)

### 5. Create a Task

```bash
curl -X POST http://127.0.0.1:8010/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "BEE-001",
    "intent": "code",
    "title": "Implement event ledger",
    "summary": "Create runtime/ledger.py with append-only SQLite event log",
    "kb_entities": ["RULE-001"],
    "delivery_mode": "task_file"
  }'
```

Task file written to `.deia/hive/tasks/BEE-001/`. The router processes intent and injects KB content automatically.

### 6. Check Task Response

```bash
curl "http://127.0.0.1:8010/api/tasks/response?task_id=TASK-009"
```

### 7. Manage Gates

```bash
# View gates
curl http://127.0.0.1:8010/api/gates

# Enable git commits
curl -X POST http://127.0.0.1:8010/api/gates \
  -H "Content-Type: application/json" \
  -d '{"allow_q33n_git": true, "pre_sprint_review": true, "allow_flight_commits": true}'
```

All three gates must be true before `POST /api/git/commit` will execute.

### 8. Flight Tracking

```bash
# Start a flight (sprint)
curl -X POST http://127.0.0.1:8010/api/flights/start \
  -d '{"flight_id": "METRICS-001", "title": "Phase 2: Metrics & Observability"}'

# Add recap
curl -X POST http://127.0.0.1:8010/api/flights/recap \
  -d '{"flight_id": "METRICS-001", "recap_text": "Event ledger schema designed"}'

# End flight
curl -X POST http://127.0.0.1:8010/api/flights/end \
  -d '{"flight_id": "METRICS-001"}'
```

---

## API Reference (26 Endpoints)

### System
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Server config, repo root status |

### Bees (Agent Management)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/bees/launch` | Launch CLI agent in new console |

### PTY Sessions
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/pty/start` | Start PTY session with CLI tool |
| POST | `/api/pty/send` | Send input to PTY session |
| GET | `/api/pty/read` | Read PTY output buffer |
| POST | `/api/pty/stop` | Stop PTY session |

### Messages
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/messages` | Post message (with lane/provider metadata) |
| GET | `/api/messages` | Get messages (optional channel filter) |
| GET | `/api/summary` | Aggregate stats (counts, by provider/lane) |
| GET | `/api/channels` | List unique channel IDs |

### Tasks
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/tasks` | Create task (routes by intent, injects KB) |
| POST | `/api/tasks/complete` | Archive completed task |
| GET | `/api/tasks/response` | Get latest response file |

### Knowledge Base
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/kb/entities` | List all KB entities |
| POST | `/api/kb/entities` | Create/upsert KB entity |
| PUT | `/api/kb/entities/{id}` | Update KB entity |
| POST | `/api/kb/preview` | Preview KB injection text |

### Git Operations (Gate-Protected)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/git/status` | Run `git status -sb` |
| POST | `/api/git/commit` | Commit (requires 3 gates) |
| POST | `/api/git/push` | Push (requires `allow_q33n_git`) |

### Gates
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/gates` | Get current gate flags |
| POST | `/api/gates` | Update gate flags |

### Flights (Sprint Tracking)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/flights/start` | Start flight session |
| POST | `/api/flights/end` | End flight session |
| POST | `/api/flights/recap` | Add recap text |
| GET | `/api/flights` | List all flights |
| GET | `/api/flights/recaps` | List recaps (optional flight filter) |

### WebSocket
| Path | Purpose |
|------|---------|
| `/api/ws` | Real-time task event broadcasting |

---

## Gate System

Three gates control git operations. All default to `false`.

| Gate | Controls | Purpose |
|------|----------|---------|
| `allow_q33n_git` | commit + push | Master switch for automated git |
| `pre_sprint_review` | commit | Human review before sprint starts |
| `allow_flight_commits` | commit | Per-flight commit permission |

**All three must be true** for `POST /api/git/commit` to execute. This is the human sovereignty mechanism — no automated commits without explicit human approval.

---

## Task Flow

```
1. POST /api/tasks          → Task created, routed by intent, KB injected
2. Task file written         → .deia/hive/tasks/{bot_id}/TASK-{id}.json
3. Bee picks up task         → Reads file, executes work
4. Bee writes response       → .deia/hive/responses/RESP-{id}.md
5. GET /api/tasks/response   → Operator retrieves result
6. POST /api/tasks/complete  → Task archived to .deia/hive/archive/
```

### Routing Logic (core/router.py)

| Intent | Lane | Provider | Delivery |
|--------|------|----------|----------|
| `design`, `planning` | llm | default | cache_prompt |
| `code` | terminal | cli | task_file |
| (anything else) | llm | default | cache_prompt |

### KB Entity Types

| Type | Purpose | Delivery Modes |
|------|---------|----------------|
| RULE | Non-negotiable guardrails | cache_prompt, task_file, both |
| SNIPPET | Code/config fragments | cache_prompt, task_file, both |

---

## Directory Structure (.deia/hive/)

```
.deia/
├── hive/
│   ├── tasks/
│   │   ├── BEE-001/        # Tasks assigned to BEE-001
│   │   └── BEE-002/        # Tasks assigned to BEE-002
│   ├── responses/           # Response files from bees
│   └── archive/             # Completed tasks
│       ├── BEE-001/
│       └── BEE-002/
├── raqcoon_messages.db      # SQLite message store
└── raqcoon_flights.db       # SQLite flight/recap store
```

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEIA_CLAUDE_CMD` | `claude` | Claude Code executable |
| `DEIA_CLAUDE_ARGS` | (empty) | Additional Claude Code args |
| `DEIA_CODEX_CMD` | `codex` | Codex executable |
| `DEIA_CODEX_ARGS` | (empty) | Additional Codex args |

| Hardcoded | Value | Location |
|-----------|-------|----------|
| Server address | `127.0.0.1:8010` | run_server.py |
| Minder interval | 600 seconds | minder.py |
| Message fetch limit | 200 | store.py |
| PTY buffer max | 4000 chars | pty_bridge.py |

---

## Roadmap

| Phase | Target | Status |
|-------|--------|--------|
| Phase 0: Consolidation | Feb 14 | Complete |
| Phase 1: Wire the Machine | Mar 14 | Complete |
| **Phase 2: Metrics & Observability** | **Apr 11** | **Current** |
| Phase 3: Simulation Engine (DES) | May 23 | Planned |
| Phase 4: Visual UI | Jul 4 | Planned |
| Phase 5: Package & Ship | Aug 1 | Planned |

**Ship target: August 2026.**

Current task: TASK-009 (Event Ledger v1) — append-only log of all system events.

---

## Built on DEIA

SimDecisions is built on the **DEIA** (Diversity, Equity, Inclusion, Automation) governance framework.

### The Philosophy

The DEIA Federalist Papers (20 papers) establish constitutional governance for AI agent coordination. Key principles:

- **#NOKINGS** — Human override always. No agent acts without human consent being retractable.
- **Protocol of Grace** — Conflict resolution: pause → listen → reflect → respond → rejoin.
- **Species Diversity** — Multi-vendor by design. No single AI provider dependency.
- **Ethics as Infrastructure** — Morality encoded in files (`ethics.yml`), not professed in manifestos.
- **Limited Liability Hive (LLH)** — Bounded, observable, replaceable coordination units.

### The BOK

The Body of Knowledge contains 32+ patterns for AI-assisted development, covering architecture, testing, prompt engineering, and governance. These feed the KB injection system.

### The Ecosystem

| Layer | Component | Status |
|-------|-----------|--------|
| Philosophy | Federalist Papers (20 papers) | Complete |
| Governance | Constitution + Gates + BOK | Complete |
| Production | **SimDecisions** | Building |
| Commerce | RAGGIT (creator marketplace) | Spec draft |
| Transport | ClipEgg (reference-first protocol) | Spec draft |

---

## For Bees: Deployment Checklist

If you are a bee (AI agent) deploying or working on this system:

1. **Repo root:** Ensure `.deia/` directory exists at project root
2. **Python:** 3.13+ with fastapi, uvicorn, pydantic, requests installed
3. **Server:** Start via `python src/deia/hivemind/runtime/run_server.py`
4. **Verify:** `GET /api/health` returns `{"status": "ok"}`
5. **Tasks go to:** `.deia/hive/tasks/{your-bot-id}/`
6. **Responses go to:** `.deia/hive/responses/`
7. **Always check gates** before any git operation
8. **Current mission:** METRICS-001 (Phase 2)
9. **Next task:** TASK-009 (Event Ledger)
10. **All tasks sequential** — assigned to BEE-001 unless otherwise specified
11. **Task numbering** starts at TASK-009 (TASK-001 through TASK-005 complete, TASK-013 through TASK-018 cancelled)

### Golden Rules for Bees

- Never commit without all three gates enabled
- Always route tasks through `POST /api/tasks` (don't write files directly)
- KB entities are injected automatically — trust the pipeline
- Log everything — if it's not in the event ledger, it didn't happen
- File-based storage preferred over complex databases
- SQLite for structured data (messages, flights, events)
- JSON for task files, Markdown for responses

---

## License

CC BY 4.0 International

Copyright © 2025-2026 DEIA Global Commons
