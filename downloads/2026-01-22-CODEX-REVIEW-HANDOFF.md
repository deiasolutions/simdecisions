# RAQCOON System Review Handoff

**Prepared For:** Codex
**Prepared By:** Claude Opus 4.5 (via Dave)
**Date:** 2026-01-22
**Context:** Continuing review of DEIA RAQCOON MVP integration status

---

## 1. Background

RAQCOON (Retrieval-Augmented Quality Control & Orchestration for Ops Nodes) is an AI workforce orchestration platform using a "hive" architecture with Q33N (Queen) orchestrators and worker bees. The MVP is approximately 70% complete per prior analysis.

### 1.1 Documents Reviewed
| Document | Date | Author | Purpose |
|----------|------|--------|---------|
| BEE1-SPEC-ANALYSIS.md | 2026-01-05 | BEE-001 | Spec inventory, phase roadmap, endpoint registry |
| BEE2-IMPLEMENTATION-AUDIT.md | 2026-01-05 | BEE-002 | Code inventory, module functions, import graph |
| BEE3-GAP-ANALYSIS.md | 2026-01-05 | BEE-003 | Missing endpoints, unconnected code, logic bugs |
| CLAUDE-6870-cli-llm-interfaces-report.md | 2026-01-19 | CLAUDE-6870 | Interface inventory, execution paths, architecture |
| hive-coding-method-spec.md | 2026-01-22 | — | iDea method, pattern capture, governance requirements |

---

## 2. Current State Summary

### 2.1 What's Working
- Basic FastAPI server structure (`runtime/server.py`)
- Task file loop (write/read/archive)
- Flight tracking (start/end/recap)
- CLI bee launch with repo-root discipline
- KB entity storage (but not injection)
- PTY Bridge for terminal control
- DirectLLM for Anthropic API calls
- MCP Server for hive communication tools

### 2.2 Critical Gaps (from BEE3)
| Issue | Severity | Details |
|-------|----------|---------|
| Router disconnected | Critical | `decide_route()` in `core/router.py` is never called from server.py |
| KB injection missing | Critical | Entity IDs stored but content never retrieved/injected into tasks |
| WebSocket echo-only | Critical | `/api/ws` just echoes input, no real messaging |
| Gate enforcement incomplete | High | `allow_flight_commits` gate defined but not checked in `git_commit` |
| Minder not integrated | High | Standalone script, not started with server |

### 2.3 New Modules (per CLAUDE-6870, post-BEE2)
These files are documented but need verification against actual repo:
- `runtime/direct_llm.py` — Direct Anthropic API client
- `runtime/executor.py` — Task execution router (SDK/CLI/API/TaskFile)
- `runtime/orchestrator.py` — Spec-to-Code pipeline coordinator
- `runtime/worker.py` — Task discovery and execution loop
- `runtime/message_router.py` — @mention parsing and routing
- `runtime/pty_chat_bridge.py` — PTY output to chat bridge
- `runtime/sdk_client.py` — Claude Agent SDK bridge client
- `mcp/hive_server.py` — MCP tools for hive communication

---

## 3. Architecture Overview

### 3.1 Four Execution Paths
```
1. PTY Bridge      → Spawn & control CLI sessions (Claude Code, Codex)
2. Direct LLM API  → Anthropic SDK for reasoning-only tasks
3. SDK Bridge      → Claude Agent SDK via HTTP bridge (Node.js dependency)
4. MCP Server      → Model Context Protocol for tool-based hive comms
```

### 3.2 Pipeline Checkpoints (Orchestrator)
```
SPEC_RECEIVED → TASKS_PLANNED → POLICY_PASSED → EXECUTION_START →
TASK_COMPLETE → EXECUTION_DONE → VERIFICATION_PASS → STAGED →
COMMITTED → AWAITING_PUSH → PUSHED → COMPLETE
```

### 3.3 Gate System
| Gate | Purpose | Status |
|------|---------|--------|
| `allow_q33n_git` | Q33N git commit/push permission | Enforced |
| `pre_sprint_review` | Human review gate before sprint | Enforced |
| `allow_flight_commits` | Per-flight commit permission | **NOT ENFORCED** |

---

## 4. Review Tasks for Codex

### 4.1 File Verification
Confirm existence and implementation status of these files in `deia_raqcoon/`:

```
runtime/
├── direct_llm.py        # Verify: functional or stub?
├── executor.py          # Verify: routing logic connected?
├── orchestrator.py      # Verify: pipeline checkpoints working?
├── worker.py            # Verify: task discovery loop active?
├── message_router.py    # Verify: @mention parsing functional?
├── pty_chat_bridge.py   # Verify: PTY→chat bridge working?
├── sdk_client.py        # Verify: requires Node.js bridge?
└── verifier.py          # Expected per spec, confirm exists

mcp/
└── hive_server.py       # Verify: MCP tools registered?

core/
├── router.py            # Confirm: still disconnected from server.py?
└── policy_engine.py     # Expected per Hive Method spec, confirm exists
```

### 4.2 Integration Audit
Check whether these connections exist:

| From | To | Expected Behavior |
|------|----|-------------------|
| `server.py POST /api/tasks` | `router.decide_route()` | Route task by intent before writing |
| `server.py POST /api/tasks` | `kb.store.preview_injection()` | Inject KB content into task payload |
| `server.py POST /api/git/commit` | `_gates["allow_flight_commits"]` | Check gate before commit |
| `server.py startup` | `minder.run_minder()` | Auto-start minder as background thread |
| `server.py /api/ws` | `MessageStore` | Broadcast messages, not just echo |
| `executor.py` | `router.decide_route()` | Use routing decision for execution method |
| `orchestrator.py` | `PolicyEngine` | Policy check at POLICY_PASSED checkpoint |

### 4.3 Policy Engine Assessment
The Hive Coding Method spec requires `PolicyEngine` + `GateManager` to:
- Block commits when `strict_policy` violations occur
- Enforce gate states (`pre_sprint_review`, `allow_flight_commits`)
- Surface violations in UI

**Questions to answer:**
1. Does `PolicyEngine` class exist? Where?
2. Does `GateManager` class exist or is it just the `_gates` dict in server.py?
3. Is policy evaluation wired into the Orchestrator pipeline?

### 4.4 SDK Bridge Dependency
CLAUDE-6870 notes SDK Bridge Client requires external Node.js service not included in Python codebase.

**Questions to answer:**
1. Is the Node.js bridge service in the repo? Location?
2. If not, is there a plan to include it or rewrite in Python?
3. Can the system function without SDK Bridge (using DirectLLM + PTY only)?

---

## 5. Hive Coding Method Spec Requirements

The new `hive-coding-method-spec.md` adds these requirements:

### 5.1 Practice Reference
- [ ] Publish condensed iDea method as `docs/quick-reference/idea-method-summary.md`
- [ ] Q33N must reference this before assigning tasks

### 5.2 Pattern Capture Loop
- [ ] Conversation logging → sanitization → pattern extraction pipeline
- [ ] Pattern submission flow with templates + QA
- [ ] UI notifications when new pattern suggested

### 5.3 Governance / Policy
- [ ] `Orchestrator` uses `PolicyEngine` + `GateManager`
- [ ] Policy evaluation runs before execution stage
- [ ] Violations surface in UI
- [ ] Gate toggles call real endpoints (not placeholders)

### 5.4 UI Wiring
- [ ] Channel picker wired to `/api/channels`
- [ ] Dashboard cards wired to `/api/flights`, `/api/tasks`
- [ ] Git panels wired to `/api/git/*` with gate checks
- [ ] Spawn modal wired to `/api/agents` or `/api/bees/launch`
- [ ] "Capture pattern" button when new insight detected

---

## 6. Recommended Review Sequence

1. **File existence check** — Confirm which runtime modules actually exist
2. **Router wiring audit** — Trace `decide_route()` call path (or lack thereof)
3. **Gate enforcement audit** — Check all three gates are enforced
4. **PolicyEngine search** — Find or confirm missing
5. **WebSocket functionality** — Assess what it would take to make functional
6. **SDK Bridge assessment** — Determine if dependency is blocking or optional

---

## 7. Expected Outputs

After review, please produce:

1. **File Status Table** — Each file from 4.1 marked as: EXISTS/FUNCTIONAL, EXISTS/STUB, MISSING
2. **Integration Status Table** — Each connection from 4.2 marked as: CONNECTED, PARTIAL, DISCONNECTED
3. **Policy Engine Report** — Implementation status and location (or confirmation missing)
4. **Blocking Issues List** — Prioritized list of what blocks MVP completion
5. **Recommended Sprint Tasks** — Ordered task list to close gaps

---

## 8. Reference: Key File Paths

```
Repository: deiasolutions/deia_raqcoon

deia_raqcoon/
├── adapters/
│   ├── base.py
│   ├── cli_adapter.py
│   └── registry.py
├── core/
│   ├── router.py          # CRITICAL: routing logic
│   └── task_files.py
├── kb/
│   └── store.py           # KB entities + preview_injection
├── mcp/
│   └── hive_server.py     # MCP tools
├── runtime/
│   ├── server.py          # Main FastAPI app
│   ├── store.py           # MessageStore
│   ├── flights.py         # FlightStore
│   ├── launcher.py        # Repo root preflight
│   ├── minder.py          # Periodic ping (standalone)
│   ├── pty_bridge.py      # PTY sessions
│   └── [new modules per CLAUDE-6870]
└── schemas/
    └── task_file.json
```

---

## 9. Contact

Questions or clarifications: route through Dave or post to hive chat channel `#raqcoon-dev`.

---

**END OF HANDOFF DOCUMENT**
