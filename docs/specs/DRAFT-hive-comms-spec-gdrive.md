# iDea Hive Communications Specification
**Version:** 0.1
**Date:** 2025-02-04

> **Note:** Earlier draft from Downloads folder. Compare with ADR-004 for reconciliation.
> This version predates the ADR-004 comprehensive spec.

---

## 1. Overview

This spec defines two core contracts for hive communication:
- **Scribe Input Contract** — how bees publish messages to the scribe bee
- **Error File Schema** — how errors are captured for the error-handler bee

All files reside on GDrive filestore. One writer (scribe) handles comms persistence. All bees can read.

---

## 2. Scribe Input Contract

### 2.1 Purpose
Bees publish messages to the scribe for recording. Scribe is the single writer to the comms log.

### 2.2 Publish Request Location
```
G:\My Drive\idea-hive\inbox\{timestamp}_{source_bee}_{message_type}.json
```

### 2.3 Publish Request Schema
```json
{
  "schema_version": "0.1",
  "timestamp": "2025-02-04T14:32:01.123Z",
  "source_bee": "worker-01",
  "message_type": "status | request | response | broadcast | escalation",
  "priority": "low | normal | high | critical",
  "target_bee": "queen | worker-02 | all | null",
  "correlation_id": "uuid-if-part-of-conversation",
  "payload": {
    "subject": "brief description",
    "body": "message content",
    "attachments": ["optional", "file", "references"]
  },
  "requires_ack": false
}
```

### 2.4 Message Types
| Type | Use |
|------|-----|
| `status` | Heartbeat, progress update, state change |
| `request` | Asking another bee or human to do something |
| `response` | Reply to a prior request |
| `broadcast` | Info for all bees (no specific target) |
| `escalation` | Needs human attention |

### 2.5 Scribe Processing
1. Polls `inbox/` for new files
2. Validates schema
3. Appends to `comms_log/{date}.jsonl` (newline-delimited JSON)
4. Moves processed file to `inbox/processed/`
5. If `requires_ack: true`, writes ack to `outbox/{target_bee}/`

### 2.6 Comms Log Format
```
G:\My Drive\idea-hive\comms_log\2025-02-04.jsonl
```
Each line is the original publish request with scribe metadata added:
```json
{"logged_at": "...", "log_seq": 42, ...original_message}
```

---

## 3. Error File Schema

### 3.1 Purpose
Capture errors for the error-handler bee to investigate, resolve, or escalate.

### 3.2 Error File Location
```
G:\My Drive\idea-hive\errors\{timestamp}_{source_bee}_{error_id}.json
```

### 3.3 Error File Schema
```json
{
  "schema_version": "0.1",
  "error_id": "uuid",
  "timestamp": "2025-02-04T14:35:22.456Z",
  "source_bee": "worker-01",
  "severity": "warning | error | critical",
  "category": "io | api | logic | timeout | unknown",
  "context": {
    "task_id": "what was being attempted",
    "function": "function_name_if_known",
    "file": "file_path_if_relevant",
    "inputs": {"sanitized": "inputs that led to error"}
  },
  "error_detail": {
    "type": "ExceptionType",
    "message": "the error message",
    "traceback": "optional stack trace"
  },
  "attempted_recovery": "what the bee tried, if anything",
  "human_escalation": false,
  "notes": "any additional context"
}
```

### 3.4 Error Handler Processing
1. Polls `errors/` for new files
2. Analyzes error context and detail
3. Attempts resolution or pattern match
4. Writes to one of:
   - `resolutions/{error_id}.json` — resolved, includes fix applied
   - `patterns/{pattern_name}.json` — new or updated antipattern
   - `escalations/{error_id}.json` — needs human, includes analysis so far
5. Moves processed error to `errors/processed/`

### 3.5 Resolution File Schema
```json
{
  "error_id": "uuid",
  "resolved_at": "timestamp",
  "resolution": "what was done",
  "pattern_id": "link to pattern if applicable",
  "confidence": "high | medium | low",
  "verified": false
}
```

### 3.6 Pattern File Schema
```json
{
  "pattern_id": "descriptive-slug",
  "pattern_type": "antipattern | pattern",
  "title": "Short name",
  "description": "What this pattern is",
  "symptoms": ["how to recognize it"],
  "root_cause": "why it happens",
  "resolution": "how to fix or avoid",
  "examples": ["error_ids that matched"],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## 4. Directory Structure

```
G:\My Drive\idea-hive\
├── inbox\                  # Bees drop publish requests here
│   └── processed\          # Scribe moves processed requests here
├── outbox\                 # Acks and direct replies
│   └── {bee_name}\         # Per-bee outbox
├── comms_log\              # Scribe writes here (append-only)
│   └── 2025-02-04.jsonl
├── errors\                 # Bees drop errors here
│   └── processed\
├── resolutions\            # Error handler writes fixes
├── patterns\               # Antipattern library
└── escalations\            # Needs human attention
```

---

## 5. Open Questions

5.1 Scribe polling interval — sim-tick driven or time-based?  
5.2 Retention policy for processed files and logs?  
5.3 Human interface for escalations — file watch, notification, dashboard?  
5.4 Should patterns be human-curated or auto-generated?

---

## 6. Change Log

| Version | Date | Notes |
|---------|------|-------|
| 0.1 | 2025-02-04 | Initial draft |
