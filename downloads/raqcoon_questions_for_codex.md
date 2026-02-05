# RAQCOON v1 – Clarifying Questions for Codex

## Purpose
These questions are intended to clarify intent, invariants, and future-facing assumptions in the RAQCOON v1 design, not to request immediate changes.

---

## a. SQLite Role & Authority
1. Is SQLite intended to be the **authoritative source of task state**, or an **index over filesystem truth**?
2. In the event of disagreement between SQLite and the filesystem, which should win?
3. Are there planned non-scheduler read paths (e.g., status, dashboards, inspectors) that will rely primarily on SQLite?
4. Would you be open to explicitly documenting SQLite as a write-ahead / reconciliation aid rather than the primary truth?

---

## b. Crash Recovery & Reconciliation
1. Is there an intended **startup reconciliation phase** when the MCP server launches?
2. If a crash occurs mid-operation (e.g., DB updated but file not moved), should the system:
   - finish the intended move, or
   - re-evaluate and potentially requeue?
3. Would a small operation log (task_id, op, timestamp, from/to paths) fit the intended design philosophy?

---

## c. Naming Spec Evolution
1. Is the filename schema considered a **frozen v1 contract**, or do you anticipate evolution?
2. Would you support the idea that future metadata belongs in:
   - YAML frontmatter inside task files, or
   - SQLite / sidecar metadata,
   rather than expanding the filename itself?

---

## d. Scaling Model
1. Is RAQCOON intentionally scoped as **single-hive / single-filesystem** for v1?
2. Do you see future scaling as:
   - multiple independent hives,
   - shared filesystem with coordination,
   - or eventual broker-backed queues?
3. Are there design constraints that would make a future broker incompatible with the current filesystem model?

---

## e. SQLite Concurrency
1. Are there plans to add internal locking or per-thread connections in `TaskIndex`?
2. Would enabling WAL mode and a busy timeout align with your expectations for stability?

---

## f. Bee Assignment Guarantees
1. Should task assignment be allowed only if:
   - the bee exists in the registry, and
   - the bee is reachable (MCP ping)?
2. Is there an intended concept of a **recovery lane** for tasks that cannot be safely reassigned?

---

## g. BeeRegistry Persistence
1. Is BeeRegistry persistence intentionally deferred, or simply out of scope for v1?
2. Would minimal persistence (identity + last-known status) fit your design goals?

---

## h. Observability
1. Is exposing scheduler / queue health via CLI or HTTP considered acceptable?
2. Would a lightweight status surface violate any architectural constraints you’re aiming to preserve?
