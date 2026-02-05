# BeeHive-Governance-v1.0.md

---
deia_routing:
  project: quantum
  destination: docs/specs/
  filename: BeeHive-Governance-v1.0.md
  action: move
version: 1.0
last_updated: 2025-10-17
sprint: 2025-Q4-Sprint-03
created_by: gpt-5 (Bot D) × daaaave-atx
linked_projects:
  - DEIA-Orchestration
  - Drone-Lite
  - File-Drone-Subsystem
  - Efemera.Live
---

# Bee Hive Governance & Orchestration (v1.0)

## Executive Summary
- Purpose: Establish a balanced **governance + technical orchestration** model for a Hive of AI agents (Queen, Assistant Queens, Workers, Drones) coordinating coding and analysis work across Claude Code, GPT-5, and Llama-based Drone-Lite.
- Principles: **Clarity, bounded autonomy, provenance, reversibility, safety-by-default**, and **DEIA Clock** alignment.
- Outcomes: Repeatable **task lifecycle**, **kill-switch policy**, **retry caps**, **async delegation**, **telemetry JSONL**, **RACI**, and **benchmark harness** for quality/time tradeoffs.

---

## 1. Role Model & Authorities
**Queen (Coordinator)**
- Owns backlog, routing, approvals, and final merges.
- Grants/limits capabilities via **Capability Manifest** (see §2) and signs off on risky ops.

**Assistant Queens (Planning & QA)**
- Translate goals into plans (milestones, test gates, rollbacks).
- Run structured reviews, enforce spec and style; can spawn Workers within quota.

**Workers (Performers)**
- Single-focus executors (edit a file; run tests; draft docs; create benchmarks); cannot escalate privileges.

**Drones (Drone-Lite / Think Agents)**
- Long-running or low‑priority tasks (refactors, synthesis, training); always **async**; results must pass QA.

**Auditor (Automated)**
- Monitors policy compliance, logs provenance, triggers kill-switches, and emits **telemetry JSONL**.

---

## 2. Capability Manifest (CLAUDE.md / HIVE.yaml)
- **Purpose:** Declare what each agent *may* do: file scope, directories, commands, external tools, model endpoints, and data sensitivity tiers.
- **Minimum fields:**
  - `agent_role`, `allowed_operations` (edit|create|delete|run|read-only), `directory_allowlist`, `file_extensions`, `shell_commands_allowlist`, `mcp_tools_allowlist`, `network_endpoints`, `secrets_policy`, `max_runtime_seconds`, `retry_limit`.
- **Change control:** Only Queen may approve manifest expansions; Auditor enforces.

---

## 3. Task Lifecycle (Plan → Execute → Verify → Merge → Telemetry)
1) **Intake**: Queen/Assistants frame a **single, testable unit of work** (goal, constraints, success tests, rollback).
2) **Plan**: Chosen agent proposes steps; Queen approves or edits.
3) **Execute**: Worker or Drone performs steps within bounds (no self-escalation).
4) **Verify**: Assistant runs checks (unit/typing/lint/e2e; doc diffs; artifact integrity).
5) **Merge & Release**: Queen merges; Auditor snapshots manifests and logs.
6) **Telemetry**: Emit JSONL record (see §8) and update **DEIA Clock**.

---

## 4. Safety Controls
- **Kill-Switch Policy:**
  - Trigger on: ≥3 consecutive failures, idle ≥X min (default 10), policy violation, or anomaly score ≥τ.
  - Action: Stop process, quarantine outputs, raise alert to Queen, require human re-authz.
- **Retry Caps:** default `3`; exponential backoff; reset on human-reviewed fix.
- **Least Privilege:** Per-agent allowlists; deny-by-default; immutable logs.
- **Reversibility:** Require **rollback plan** for any change touching ≥N files or protected paths.

---

## 5. Async Drone-Lite Handler (Architecture)
- **Purpose:** Offload slow, parallelizable work while keeping fast delivery unblocked.
- **Dispatch rules:**
  - Send to Drone when: long execution, exploratory synthesis, batch refactors, or background benchmarking.
  - Keep with Worker when: hot path fixes, security-sensitive changes, or non-idempotent migrations.
- **Queueing:** Priority queue with SLAs; bounded concurrency; per-agent runtime quotas.
- **Return path:** Drones post artifacts + **confidence notes**; Assistants verify before merge.
- **A/B Mode:** Run duplicate tasks on Drone vs Worker to measure **quality/time**.

---

## 6. Benchmark Harness (Quality × Time)
- **Metrics:** wall-clock, CPU/GPU time, tokens in/out, edit distance, test pass rate, defect density, review iterations.
- **Design:** Deterministic inputs (fixtures), seeded randomness, golden outputs, and reproducible environments.
- **Reporting:** Per‑agent scorecards; trend lines; **stoplight thresholds** for promotion/demotion of agents.

---

## 7. RACI Matrix (Snapshot)
| Activity | Queen | Assistant Queen | Worker | Drone | Auditor |
|---|---|---|---|---|---|
| Intake & scoping | A | R | C | C | I |
| Plan approval | A | R | C | C | I |
| Execute task | C | C | R | R | I |
| QA/verification | A | R | C | C | I |
| Merge/release | A | R | C | C | I |
| Telemetry & compliance | I | C | I | I | R |
| Capability manifest changes | A | R | C | I | R |

*A = Accountable, R = Responsible, C = Consulted, I = Informed*

---

## 8. Telemetry JSONL (Emit per Task)
- **Fields (minimum):**
  - `ts`, `task_id`, `parent_id`, `agent_id`, `agent_role`, `capability_manifest_hash`, `inputs_hash`, `outputs_hash`, `dur_ms`, `tokens_in`, `tokens_out`, `quality_score`, `tests_passed`, `retries`, `kill_switch_triggered`, `ab_group`, `notes`.
- **Storage:** Append-only JSONL; signed digests; linked to **DEIA Clock**; rolling window dashboards.

---

## 9. Governance Charter
- **Bounded Autonomy:** Agents can plan internally but must stay within manifest limits.
- **Risk Classes:**
  - R0 (docs/tests), R1 (non-critical code), R2 (prod-facing), R3 (security/data). Higher class ⇒ stricter reviews.
- **Auditability:** Every action traceable to a manifest and a human approval.
- **Ethics & Impact:** Prioritize sustainability, accessibility, and community benefit (DEIA principles).

---

## 10. Implementation Roadmap (T‑shirt size × Difficulty)
1) Capability Manifests (S, ★★☆☆☆)
2) Task Lifecycle templates (S, ★★☆☆☆)
3) Kill-switch & Retry service (M, ★★★☆☆)
4) Telemetry JSONL emitter + dashboard (M, ★★★☆☆)
5) Drone-Lite dispatcher & queue (M, ★★★★☆)
6) Benchmark harness (M, ★★★★☆)
7) Governance audits & promotions (S, ★★☆☆☆)
8) DEIA Clock integration (M, ★★★☆☆)

---

## 11. Acceptance Criteria
- All agents constrained by manifests; unsafe ops rejected.
- Every task produces telemetry JSONL and passes defined tests.
- Kill-switches demonstrably halt misbehavior with quarantined outputs.
- Benchmarks run weekly; promotions/demotions logged.

---

## 12. Prompts & Patterns (No Code)
- **Plan-first:** “Propose a 5‑step plan with tests and rollback. Wait for approval.”
- **Bounded edit:** “Edit only files under `src/featureX/`. No new deps. Provide diff summary.”
- **Async delegate:** “Spin off a Drone-Lite task for batch refactor; return ETA and verification plan.”
- **Review gate:** “List risks by class (R0–R3); confirm test coverage before merge.”

---

## 13. Appendix — Manifests (Schema Sketch)
- **HIVE.yaml (top-level):** roles, endpoints, repos, data tiers.
- **CLAUDE.md (per-repo):** style, tests, commands, tool allowlists, incident protocol.

---

## Document History
- **v1.0 (2025‑10‑17):** First balanced governance + orchestration Egg.
