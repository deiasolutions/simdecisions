# RAQCOON v1 – Clarifications, Decisions, Scaling Pipeline, and Task Contract

Generated: 2026-01-27

This document is the **authoritative clarification and execution guide** for RAQCOON v1.
It defines invariants, agreed decisions, and explicit expectations for how this document
should be translated into concrete work items by Codex.

---

## a. SQLite Role & Authority

- SQLite is a **secondary index and reconciliation aid**, not the authoritative source of truth.
- The filesystem (`queue/`, `claimed/`, `archive/`) remains the **canonical source**.
- SQLite is written **before** filesystem moves to support crash recovery and reconciliation.
- **Filesystem wins on divergence**.

**Additional requirement**
- If a task appears in `claimed/` but the SQLite record indicates `COMPLETE`, the system must perform an **explicit completion verification step** before archiving or requeuing.
- Tasks failing verification are routed to the **recovery lane** (see f).

---

## b. Crash Recovery & Reconciliation

- A **server launch reconciliation phase** must run when the MCP server starts.
- Reconciliation compares SQLite intent/state, filesystem location, and completion evidence.
- The system favors **re-evaluation over blind completion**.

---

## c. Naming Spec Evolution

- Filename schema is **frozen for v1**.
- New metadata belongs in **YAML frontmatter** or SQLite, not filenames.

---

## d. Scaling Model (v1 Scope)

- RAQCOON v1 is **single-hive**.
- Bees are scoped to one workspace and may not cross repos by default.

---

## e. SQLite Concurrency & Stability

- `TaskIndex` must serialize access with an internal lock.
- SQLite must enable **WAL mode** and a **busy timeout**.

---

## f. Bee Assignment & Recovery Lane

- Assignment requires registry existence + MCP liveness.
- Failed, stale, or unverifiable tasks enter a **recovery lane** for re-evaluation.

---

## g. BeeRegistry Persistence

- Minimal persistence (identity + status snapshot) is required.

---

## h. Observability & Pipeline UI

- Scheduler status may be surfaced via UI/CLI.
- Pipeline page refreshes on navigation and shows a friendly timestamp.

---

# Scaling Pipeline (Documentation Requirement)

- Add `scaling-pipeline.md` to `deia_raqcoon/pipeline/`.
- Documentation only; exploratory, not prescriptive.

---

# Task Generation Expectations (for Codex)

Codex must convert each requirement above into discrete tasks.

- Tasks must be **small, scoped, and categorized**.
- Categories: `DOC`, `INFRA`, `PROTO`, `UI`.
- Each task must include description, likely files, and acceptance criteria.

---

# Pre-Seeded Canonical Tasks (Gold Standards)

The following tasks are **authoritative examples** of how Codex should generate work.
Future tasks should follow the same structure, scope, and level of specificity.

---

### TASK 1 — Startup Reconciliation Pass

- **Category:** INFRA  
- **Description:** Add an explicit reconciliation phase when the MCP server starts to reconcile SQLite intent with filesystem reality.  
- **Likely files:**  
  - `protocol/mcp_server.py`  
  - `store/index.py`  
  - `store/workspace.py`  
- **Acceptance criteria:**  
  - On startup, tasks in limbo are detected deterministically.  
  - No tasks are silently completed or dropped.  
  - Recovery lane is used when reconciliation cannot resolve state safely.

---

### TASK 2 — Recovery Lane Implementation

- **Category:** PROTO  
- **Description:** Introduce a dedicated recovery lane for tasks that fail assignment, verification, or reconciliation.  
- **Likely files:**  
  - `protocol/scheduler.py`  
  - `protocol/claims.py`  
  - `store/workspace.py`  
- **Acceptance criteria:**  
  - Recovery lane tasks are isolated from normal queue flow.  
  - Tasks are re-evaluated before requeue or archive.  
  - Manual or automated review is possible.

---

### TASK 3 — Completion Verification Step

- **Category:** PROTO  
- **Description:** Verify task completion when SQLite indicates COMPLETE but filesystem state disagrees.  
- **Likely files:**  
  - `protocol/claims.py`  
  - `store/index.py`  
- **Acceptance criteria:**  
  - Completion is verified before archival.  
  - Failed verification routes task to recovery lane.

---

### TASK 4 — SQLite Concurrency Hardening

- **Category:** INFRA  
- **Description:** Harden SQLite usage with locking, WAL mode, and busy timeout.  
- **Likely files:**  
  - `store/index.py`  
- **Acceptance criteria:**  
  - No unhandled SQLite lock errors under concurrent access.  
  - Reads may proceed during writes.

---

### TASK 5 — Bee Assignment Validation

- **Category:** PROTO  
- **Description:** Prevent assignment to non-existent or unreachable bees.  
- **Likely files:**  
  - `protocol/scheduler.py`  
  - `bees/registry.py`  
- **Acceptance criteria:**  
  - Bee existence and liveness are validated before assignment.  
  - Failed assignments route tasks to recovery lane.

---

### TASK 6 — BeeRegistry Persistence

- **Category:** INFRA  
- **Description:** Persist minimal BeeRegistry state across restarts.  
- **Likely files:**  
  - `bees/registry.py`  
- **Acceptance criteria:**  
  - Bees restore identity and last-known status after restart.

---

### TASK 7 — Pipeline Status Surface

- **Category:** UI  
- **Description:** Surface scheduler status in the pipeline UI with refresh and timestamp.  
- **Likely files:**  
  - `ui/pipeline.py`  
  - `protocol/scheduler.py`  
- **Acceptance criteria:**  
  - Status refreshes on navigation.  
  - Manual refresh works.  
  - Timestamp is user-friendly.

---

### TASK 8 — Scaling Pipeline Documentation

- **Category:** DOC  
- **Description:** Draft `scaling-pipeline.md` describing future multi-hive and broker-based scaling paths.  
- **Likely files:**  
  - `pipeline/scaling-pipeline.md`  
- **Acceptance criteria:**  
  - Document covers multi-hive, broker concepts, and invariants.  
  - No implementation commitments are introduced.

---

## Status

This document includes canonical task exemplars and is ready for direct ingestion by Codex.
