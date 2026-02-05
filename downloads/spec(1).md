# spec.md
# Hybrid AI Coding Orchestration (HACO) — Master Specification
**Version:** 1.0  
**Date:** 2026-01-19  
**Audience:** Claude Code (Supervisor), local/service wrappers, and human maintainers  
**Goal:** A reproducible, auditable workflow where a “Supervisor” model plans/reviews/integrates, while one or more local “Worker” models generate bulk code for low cost and privacy.

---

## 0. Scope & Non‑Goals

### 0.1 In scope
- A **Supervisor→Worker** architecture for coding tasks:
  - **Supervisor**: Claude Code (Anthropic) for planning, repository navigation, code review, integration, testing, and git operations.
  - **Workers**: Local Ollama models (primary: Qwen 2.5 Coder; optional: DeepSeek Coder) for drafting longer code blocks, repetitive refactors, and test boilerplate.
- A **control surface** usable by:
  - Claude Code (interactive) and
  - a local service wrapper (non-interactive) that can call the same worker interface.
- A **decision log** documenting alternatives considered (OpenAI/Codex CLI, Gemini CLI, direct single-model approach, etc.) and why the recommended approach was chosen.
- Implementation artifacts:
  - `bin/worker` bridge script
  - `CLAUDE.md` project rules (Supervisor protocol)
  - Optional: `bin/haco` orchestration helper (multi-step loop)
  - Optional: `.haco/` folder conventions
  - Optional: ignore rules (`.gitignore`, `.geminiignore`, `.claudeignore`) guidance

### 0.2 Non‑goals
- Not building a full autonomous agent that edits files without review.
- Not forcing one provider; the system is provider-agnostic by design.
- Not guaranteeing model correctness; correctness comes from review + tests.

---

## 1. Design Principles

1. **Least privilege:** Workers never write to disk directly; only Supervisor writes files and commits.
2. **Determinism over cleverness:** Prefer clear state + steps, not implicit behaviors.
3. **Token/latency efficiency:** Don’t dump whole repositories into Workers; send focused snippets + requirements.
4. **Auditability:** Every significant change is traceable to a plan + test run.
5. **Fail closed:** If outputs are ambiguous or unsafe, Supervisor rejects and requests revision.

---

## 2. Terminology

- **Supervisor**: The “lead engineer” model. Owns plan, reviews worker output, runs tests, writes files, controls git.
- **Worker**: The “staff engineer” model. Produces draft code/text based on a tight prompt.
- **Bridge**: A stable local command that turns a prompt into a Worker response (`bin/worker`).
- **Ticket**: A single implementation unit (file/module/function/test) within a plan.
- **Plan**: A structured sequence of tickets with acceptance criteria and test commands.

---

## 3. System Overview

### 3.1 High-level architecture
```
Human (you)
   |
   v
Claude Code (Supervisor)
   |  (Bash tool calls)
   v
bin/worker  --->  Ollama runtime  --->  Qwen / DeepSeek (Worker)
   |
   v
stdout back to Supervisor  --->  review  --->  edits to repo  --->  tests  --->  commit
```

### 3.2 Why this pattern
- Claude is strong at **planning, code review, and not getting lost** in multi-step refactors.
- Local open-weight models are strong at **bulk code generation** with **$0 marginal cost** and privacy (local execution).

---

## 4. Options Considered (Alternatives) & Decision Log

### 4.1 Option A — Single-model “do everything” (reject)
- **Pros:** simplest mental model.
- **Cons:** higher cost; more brittle; less controllable; worse privacy if cloud-only.
- **Decision:** rejected because the goal includes low-cost bulk coding + strong supervision.

### 4.2 Option B — Codex CLI as Supervisor (alternative)
- **Pros:** very fast, great for micro-edits.
- **Cons:** less “architectural planning” oriented than Claude (in your described workflow).
- **Decision:** optional, but not the primary Supervisor for this spec.

### 4.3 Option C — Gemini CLI as Supervisor (alternative)
- **Pros:** good for Google ecosystem; useful for large context and search workflows.
- **Cons:** less aligned with your “engineering supervisor” workflow than Claude Code.
- **Decision:** keep as a supplemental tool; not core to HACO.

### 4.4 Option D — Claude Code as Supervisor + local Worker (recommended)
- **Pros:** best planning/review loop; local cost efficiency; strict separation of duties.
- **Cons:** requires a bridge script + discipline.
- **Decision:** **selected** as the default architecture.

---

## 5. Recommended Baseline: Claude Code (Supervisor) + Ollama Worker

### 5.1 Requirements
- **Claude Code CLI** installed and working.
- **Ollama** installed and running.
- One or more local models pulled:
  - `qwen2.5-coder:32b` (primary)
  - optionally `deepseek-coder` (long-context use cases)

### 5.2 Repository layout (recommended)
```
<repo>/
  CLAUDE.md
  PLAN.md                  (generated per initiative)
  bin/
    worker                 (stable bridge to Worker)
    haco                   (optional helper wrapper)
  .haco/
    prompts/               (optional reusable prompt templates)
    logs/                  (optional run logs)
  docs/
    haco/                  (optional design notes)
```

---

## 6. Bridge Contract: `bin/worker`

### 6.1 Purpose
A stable interface the Supervisor can call that:
- accepts a single prompt string (or stdin),
- invokes an Ollama model,
- returns clean stdout suitable for parsing/review.

### 6.2 Output contract
Worker output must be:
- **only** the requested artifact (code, patch, tests, docs),
- **no** conversational filler,
- and must respect the requested format (e.g., fenced code blocks or unified diffs).

### 6.3 Minimal implementation (portable shell)
Create: `bin/worker`
```bash
#!/usr/bin/env bash
set -euo pipefail

MODEL="${HACO_WORKER_MODEL:-qwen2.5-coder:32b}"

if [[ $# -lt 1 ]]; then
  echo "Usage: bin/worker \"<prompt>\""
  exit 1
fi

PROMPT="$1"

# Basic guard: ensure model exists locally (avoid confusing failures)
if ! ollama list | awk '{print $1}' | grep -qx "$MODEL"; then
  echo "Error: model '$MODEL' not found. Run: ollama pull $MODEL"
  exit 1
fi

# Worker wrapper to enforce terse output
ollama run "$MODEL" \
"You are a code implementation worker. Output only the requested artifact. \
No explanations unless explicitly requested. Task:\n\n$PROMPT"
```

Then:
```bash
chmod +x bin/worker
```

### 6.4 Stdin mode (optional but recommended)
If you prefer sending large prompts via stdin to avoid quoting issues:
```bash
#!/usr/bin/env bash
set -euo pipefail

MODEL="${HACO_WORKER_MODEL:-qwen2.5-coder:32b}"

if ! ollama list | awk '{print $1}' | grep -qx "$MODEL"; then
  echo "Error: model '$MODEL' not found. Run: ollama pull $MODEL"
  exit 1
fi

PROMPT="$(cat)"

ollama run "$MODEL" \
"You are a code implementation worker. Output only the requested artifact. \
No explanations unless explicitly requested. Task:\n\n$PROMPT"
```

Usage:
```bash
cat .haco/prompts/ticket.txt | bin/worker
```

### 6.5 Model routing (optional)
Use env var per-call:
```bash
HACO_WORKER_MODEL=deepseek-coder bin/worker "Write tests for ..."
```

---

## 7. Supervisor Rules: `CLAUDE.md` (Project Memory)

Create: `CLAUDE.md`
```markdown
# HACO Supervisor Rules (Claude Code)

## Role
You are the Supervisor and Lead Architect.

## Authority Boundaries
- You are the ONLY agent that may write to files, run tests, and perform git operations.
- Workers (Ollama models) may ONLY generate drafts via `bin/worker`.

## Protocol (mandatory)
1) PLAN: For any non-trivial change, produce/maintain PLAN.md with Tickets + Acceptance Criteria.
2) DELEGATE: For any ticket that would produce > ~20 lines of code, delegate the first draft to the worker:
   - Use: `! bin/worker "<ticket prompt>"` (or stdin mode).
3) REVIEW: Treat worker output as untrusted. Review for:
   - correctness, edge cases, security, performance, and style consistency.
4) INTEGRATE: Apply edits yourself (Edit tool). Never pipe worker output directly into repo files without review.
5) VERIFY: Run tests/lint/build. If no tests exist, add a minimal sanity check.
6) COMMIT: Commit with a message referencing the ticket(s).

## Prompt Hygiene
- Do not send full files/repo to the worker unless required.
- Prefer sending: function signatures, interfaces, constraints, and acceptance tests.

## Safe Defaults
- If requirements are ambiguous, ask for clarification OR create an explicit assumption block in PLAN.md.
```
```

---

## 8. Operating Workflow (Canonical “Hybrid Loop”)

### 8.1 Phase 1 — Plan (Supervisor)
Supervisor produces/updates `PLAN.md` containing:
- Summary
- Tickets (numbered)
- File targets
- Acceptance criteria
- Test/verification commands

### 8.2 Phase 2 — Delegate (Supervisor→Worker)
For each ticket requiring bulk code:
- Supervisor constructs a worker prompt that includes:
  - objective
  - file path(s)
  - required function signatures
  - constraints (style, libs, security)
  - acceptance criteria / test expectations
- Supervisor invokes:
  - `! bin/worker "<prompt>"` (or stdin mode)

### 8.3 Phase 3 — Review & Integrate (Supervisor)
Supervisor:
- checks compile-ability and consistency with repo standards
- ensures error handling, edge cases, and security basics
- writes the final code into actual files

### 8.4 Phase 4 — Verify (Supervisor)
Supervisor runs:
- unit tests
- lint/format
- typecheck/build
- minimal smoke test (if none exist)

### 8.5 Phase 5 — Iterate
If failures occur:
- Supervisor writes a tight failure report (error output + constraints)
- re-delegates to worker with explicit fix request
- repeats review + verify

---

## 9. Prompt Templates (Reusable)

### 9.1 Ticket prompt template (recommended)
Save as: `.haco/prompts/ticket_template.md`
```markdown
# Ticket: <short name>

## Context
<what module does, what must remain true>

## Target
- File(s): <path(s)>
- Function(s)/Class(es): <names>
- Public API: <signatures>

## Requirements
- Correctness:
- Edge cases:
- Security:
- Performance:
- Style constraints:

## Output Format
Return:
1) A fenced code block for each file OR a unified diff patch.
2) No extra commentary.
```
```

### 9.2 Worker “diff” mode (useful for large edits)
Add to prompt:
- “Return a **unified diff** (git-style) only.”

---

## 10. Service Mode (Programmatic Control)

### 10.1 Goals
- Run the same worker calls from a local service that you control programmatically.
- Avoid interactive UI noise; capture clean stdout/stderr.

### 10.2 Approach
- Keep `bin/worker` as the single source of truth.
- Build service wrappers that call `bin/worker` (or call Ollama’s local REST API) and return:
  - stdout (response)
  - stderr (errors)
  - exit code
  - optional timing metadata

### 10.3 Minimal wrapper contract
Inputs:
- `prompt: string`
- `model?: string`
Outputs:
- `{ ok: boolean, output: string, error?: string, model: string }`

### 10.4 Suggested control patterns
1) **Supervisor-driven:** Claude Code runs the loop; service is optional.
2) **Service-driven:** Service runs: plan → worker draft → supervisor review (still via Claude Code) → integrate.
3) **Queued tasks:** Service accepts tickets, writes them to `.haco/queue/`, and Claude Code processes them.

---

## 11. Security & Privacy Considerations

### 11.1 Local vs cloud
- Local Ollama workers keep repository content on-machine.
- Supervisor may still use cloud API (Claude). Treat sensitive repos accordingly.

### 11.2 Data minimization
- Share only the minimum context needed for a ticket.
- Prefer sending interfaces + failing tests over whole modules.

### 11.3 Supply chain hygiene
- Do not accept generated code that introduces unexpected dependencies.
- Require Supervisor to run:
  - `npm audit` / `pip-audit` (as applicable)
  - linters and type checks

---

## 12. Performance & Stability

### 12.1 Pre-warm (optional)
At the start of a session:
```bash
ollama run qwen2.5-coder:32b "ping"
```

### 12.2 Timeouts & retries
- Worker calls should fail fast if the model isn’t present.
- Supervisor should treat repeated worker failures as a signal to simplify tickets.

### 12.3 Context compaction
- Keep long-lived truth in files (`PLAN.md`, ADRs) rather than chat history.

---

## 13. Multi-Model Strategy (When to use what)

### 13.1 Qwen 2.5 Coder (default Worker)
Use for:
- boilerplate, CRUD layers, tests scaffolding
- straightforward refactors
- multi-file codegen where the Supervisor provides a strong plan

### 13.2 DeepSeek Coder (optional Worker)
Use for:
- longer-context synthesis tasks (large interfaces, lots of similar helpers)
- situations where Qwen loses coherence across many constraints

### 13.3 Gemini CLI (optional tool, not core)
Use for:
- exploratory questions or broad repo scanning where it’s strongest in your workflow,
- but keep results treated as suggestions (verify).

### 13.4 Codex CLI (optional)
Use for:
- high-volume micro-edits,
- but keep architecture decisions with Supervisor (Claude).

---

## 14. Acceptance Criteria (Definition of Done)

A HACO setup is “done” when:
1. `bin/worker` runs successfully and returns clean output.
2. `CLAUDE.md` exists and Supervisor follows the protocol.
3. A sample ticket can be executed end-to-end:
   - PLAN → delegate → integrate → tests pass.
4. Worker cannot write files directly (process/policy + human discipline).
5. The repo contains at least one example `PLAN.md` and a small “hello loop” test.

---

## 15. Quick Start Checklist

1) Install/verify:
- Claude Code CLI
- Ollama

2) Pull models:
```bash
ollama pull qwen2.5-coder:32b
# optional:
# ollama pull deepseek-coder
```

3) Create files:
- `bin/worker` (+ chmod)
- `CLAUDE.md`
- optional `.haco/prompts/ticket_template.md`

4) Run a smoke test:
```bash
bin/worker "Return a Python function add(a,b) with type hints."
```

5) Start Claude Code and instruct:
- “Read CLAUDE.md. Initialize HACO. Create a PLAN.md for <feature>. Use bin/worker for drafts.”

---

## 16. Notes on Trust & Verification

Models make mistakes. Treat all generated output as untrusted until:
- compiled/typechecked,
- tested,
- and reviewed for safety and dependency creep.

---

## References (APA)
This spec is a practical engineering pattern drawing on standard software architecture practices (e.g., least privilege, separation of duties, and review-gated change control) and does not rely on a single external publication.
