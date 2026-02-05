# ADR-004: G-Drive as Coordination Layer

**Status:** PROPOSED
**Date:** 2026-02-04
**Author:** Q33N (Dave) + BEE-001
**Supersedes:** File-based `.deia/hive/` coordination

> **Note:** This document was recovered from BEE-001's session on 2026-02-04 after a crash.
> If an original version is found with different content, compare and reconcile.

---

## Decision

Move hive coordination, logging, and human communication from GitHub (`.deia/hive/`) to Google Drive. GitHub remains for code only. G-Drive becomes the living workspace for tasks, responses, logs, and tribunal reviews.

---

## Context

### Current State (GitHub-based)

```
.deia/
├── hive/
│   ├── tasks/           # Task files (markdown)
│   ├── responses/       # Response files (markdown)
│   └── archive/         # Completed work
├── bot-logs/            # Activity logs (JSONL)
└── processes/           # Process definitions
```

### Problems

| Problem | Impact |
|---------|--------|
| Logs buried in repo | Humans don't read them |
| Tasks are static files | No real-time collaboration |
| Archive is invisible | Historical context lost |
| Non-devs can't participate | Q33N coordination limited to terminal |
| PR-based review | Slow, fragmented feedback |

### Solution

G-Drive as the coordination layer:

- **Real-time:** Multiple bees and humans can work in same doc
- **Accessible:** Non-technical stakeholders can see/comment
- **Searchable:** Google's search beats grep on markdown
- **Persistent:** Docs don't get lost in git history
- **API-driven:** Bots can read/write programmatically

---

## G-Drive Folder Hierarchy

```
📁 SimDecisions/
│
├── 📁 Hive/
│   │
│   ├── 📁 Queue/
│   │   │   # Unclaimed tasks — any bee can grab
│   │   ├── 📄 [P1] TASK-030 - GDrive Interface PyBee.gdoc
│   │   ├── 📄 [P2] TASK-031 - Tribunal Doc Template.gdoc
│   │   └── ...
│   │
│   ├── 📁 Claimed/
│   │   │   # In-progress — locked by assigned bee
│   │   ├── 📁 BEE-001/
│   │   │   ├── 📄 TASK-009 - Event Ledger v1.gdoc
│   │   │   └── ...
│   │   ├── 📁 BEE-002/
│   │   └── 📁 PYBEE-001/
│   │
│   ├── 📁 Buzz/
│   │   │   # Complete, awaiting Q33N review
│   │   ├── 📄 TASK-009 - Event Ledger v1 [COMPLETE].gdoc
│   │   └── ...
│   │
│   └── 📁 Archive/
│       │   # Reviewed and closed
│       ├── 📁 2026-02/
│       │   ├── 📄 TASK-001 - Repo Setup [MERGED].gdoc
│       │   └── ...
│       └── 📁 2026-01/
│
├── 📁 Logs/
│   │   # Activity logs — replaces .deia/bot-logs/
│   │
│   ├── 📄 BEE-001-Activity.gsheet
│   ├── 📄 BEE-002-Activity.gsheet
│   ├── 📄 PYBEE-001-Activity.gsheet
│   └── 📄 System-Events.gsheet
│
├── 📁 Tribunal/
│   │   # Code review tribunal docs
│   │
│   ├── 📁 Pending/
│   │   ├── 📄 PR-042 [TASK-009] Event Ledger - Tribunal.gdoc
│   │   └── ...
│   │
│   ├── 📁 Ready-for-Dave/
│   │   └── ...
│   │
│   ├── 📁 QC-Queue/
│   │   │   # Sampled rejects for human review
│   │   └── ...
│   │
│   └── 📁 Archive/
│       ├── 📁 2026-02/
│       └── ...
│
├── 📁 Specs/
│   │   # Human-readable specs (sync from GitHub or primary here)
│   │
│   ├── 📄 ADR-001 - Event Ledger Foundation.gdoc
│   ├── 📄 ADR-002 - API Endpoint Registry.gdoc
│   ├── 📄 SPEC-PyBee - Python Executable Species.gdoc
│   └── ...
│
├── 📁 Federalist/
│   │   # The Federalist Papers — philosophy docs
│   │
│   ├── 📄 NO-01 - On the Constitution of Minds.gdoc
│   ├── 📄 NO-02 - On Queens and Tyranny.gdoc
│   └── ...
│
├── 📁 Templates/
│   │   # Document templates
│   │
│   ├── 📄 TEMPLATE - Task.gdoc
│   ├── 📄 TEMPLATE - Response.gdoc
│   ├── 📄 TEMPLATE - Tribunal Review.gdoc
│   └── 📄 TEMPLATE - Activity Log.gsheet
│
└── 📁 Dashboards/
    │   # Aggregated views
    │
    ├── 📄 Hive Status Dashboard.gsheet
    ├── 📄 Kaizen Metrics.gsheet
    └── 📄 Tribunal Analytics.gsheet
```

---

## Document Formats

### Task Document (`.gdoc`)

```
┌─────────────────────────────────────────────────────────────┐
│ TASK-030: GDrive Interface PyBee                            │
├─────────────────────────────────────────────────────────────┤
│ Priority: P1        │ Status: QUEUED                        │
│ Issued: 2026-02-04  │ Assigned: [unclaimed]                 │
│ Domain: integration │ Effort: 4 hrs                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## Objective                                                │
│ Build PyBee that interfaces with Google Drive API...        │
│                                                             │
│ ## Acceptance Criteria                                      │
│ - [ ] Can create docs from template                         │
│ - [ ] Can write to doc sections                             │
│ - [ ] Can read doc content                                  │
│ - [ ] Can move docs between folders                         │
│                                                             │
│ ## References                                               │
│ - ADR-004 (this doc)                                        │
│ - SPEC-PyBee                                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ## Work Log                                                 │
│ [Bee writes progress here as they work]                     │
│                                                             │
│ 2026-02-04 16:30 BEE-001: Claimed task, reading specs       │
│ 2026-02-04 17:00 BEE-001: Auth working, testing API calls   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ## Response                                                 │
│ [Bee writes final response here when complete]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Activity Log (`.gsheet`)

| Timestamp | Event | Task | Message | Tokens | Cost |
|-----------|-------|------|---------|--------|------|
| 2026-02-04T16:00:00Z | session_start | — | Session started | — | — |
| 2026-02-04T16:05:00Z | task_claimed | TASK-030 | Claimed GDrive PyBee task | — | — |
| 2026-02-04T16:30:00Z | progress | TASK-030 | Auth working | 1200 | $0.02 |
| 2026-02-04T17:00:00Z | progress | TASK-030 | API calls tested | 800 | $0.01 |

### Tribunal Review (`.gdoc`)

```
┌─────────────────────────────────────────────────────────────┐
│ TRIBUNAL: PR #42 — [TASK-009] Event Ledger v1               │
├─────────────────────────────────────────────────────────────┤
│ PR Link: [github.com/...]                                   │
│ Submitted: 2026-02-04 14:00                                 │
│ Submitter: BEE-001 (Claude)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## Judge 1: Gemini Q33N                                     │
│ [Assessment narrative...]                                   │
│ Scores: I:1 N:0 V:1 E:1 S:1 T:1 = 5/6                      │
│ Vote: APPROVE                                               │
│                                                             │
│ ## Judge 2: Codex Q33N                                      │
│ [Assessment narrative...]                                   │
│ Scores: I:1 N:-1 V:1 E:0 S:1 T:1 = 3/6                     │
│ Vote: REQUEST CHANGES                                       │
│                                                             │
│ ## Judge 3: Anthropic Q33N                                  │
│ [Assessment narrative...]                                   │
│ Scores: I:1 N:0 V:1 E:1 S:1 T:1 = 5/6                      │
│ Vote: APPROVE                                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ## Consensus Opinion                                        │
│ Verdict: APPROVE (2-1)                                      │
│ Score: 13/18                                                │
│ [Narrative summary...]                                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ## Human Decision                                           │
│ Verdict: ____________                                       │
│ Notes: ____________                                         │
│ Date: ____________                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API Integration

### PyBee: `gdrive-hive-interface`

Runs locally on Dave's machine. Provides:

```python
class GDriveHive:
    """
    G-Drive interface for hive coordination.
    Replaces file-based .deia/hive/ operations.
    """

    # === Task Operations ===

    def list_queue(self) -> List[Task]:
        """List all tasks in Queue/ folder."""

    def claim_task(self, task_id: str, bee_id: str) -> bool:
        """
        Move task from Queue/ to Claimed/{bee_id}/.
        Update status in doc.
        """

    def log_progress(self, task_id: str, bee_id: str, message: str):
        """Append to Work Log section in task doc."""

    def complete_task(self, task_id: str, bee_id: str, response: str):
        """
        Write response to Response section.
        Move doc to Buzz/ folder.
        """

    def archive_task(self, task_id: str, outcome: str):
        """Move from Buzz/ to Archive/{month}/."""

    # === Logging Operations ===

    def log_activity(self, bee_id: str, event: str, task: str, msg: str):
        """Append row to bee's activity log sheet."""

    def get_activity_log(self, bee_id: str, since: datetime) -> List[Dict]:
        """Read recent activity from sheet."""

    # === Tribunal Operations ===

    def create_tribunal_doc(self, pr_number: int, task_id: str) -> str:
        """Create tribunal review doc from template. Returns doc_id."""

    def write_judge_verdict(self, doc_id: str, judge: str, verdict: Dict):
        """Write judge section to tribunal doc."""

    def write_consensus(self, doc_id: str, consensus: Dict):
        """Write consensus section."""

    def read_human_decision(self, doc_id: str) -> Optional[Dict]:
        """Poll for human decision in doc."""

    # === Folder Operations ===

    def ensure_folder_structure(self):
        """Create folder hierarchy if not exists."""

    def move_doc(self, doc_id: str, target_folder: str):
        """Move doc to different folder."""
```

### Authentication

```yaml
# gdrive-credentials.yml (NOT in repo — local only)

type: "service_account"
project_id: "simdecisions-hive"
client_email: "hive-bot@simdecisions-hive.iam.gserviceaccount.com"
private_key: "..."

# Scopes needed:
# - https://www.googleapis.com/auth/drive
# - https://www.googleapis.com/auth/documents
# - https://www.googleapis.com/auth/spreadsheets
```

### Local Bot Runner

```python
# runner.py — runs on Dave's machine

from gdrive_hive import GDriveHive
import time

hive = GDriveHive(credentials_path="~/.config/simdecisions/gdrive-credentials.json")

# Ensure folder structure exists
hive.ensure_folder_structure()

# Main loop — poll for work, sync state
while True:
    # Check for tasks in queue
    tasks = hive.list_queue()
    print(f"Tasks in queue: {len(tasks)}")

    # Check tribunal docs for human decisions
    pending = hive.list_tribunal_pending()
    for doc in pending:
        decision = hive.read_human_decision(doc.id)
        if decision:
            # Human decided — process it
            handle_tribunal_decision(doc, decision)

    time.sleep(60)  # Poll every minute
```

---

## Migration Plan

### Phase 1: Setup (Now)

1. Create G-Drive folder structure
2. Create document templates
3. Set up service account + API access
4. Build basic `gdrive-hive-interface` PyBee

### Phase 2: Parallel Operation

1. Write new tasks to both GitHub and G-Drive
2. Bees log to both `.deia/bot-logs/` and G-Drive Logs/
3. Validate G-Drive workflow works

### Phase 3: G-Drive Primary

1. Stop writing to `.deia/hive/` (keep for legacy reference)
2. G-Drive becomes source of truth for coordination
3. GitHub `.deia/` only keeps process definitions

### Phase 4: Full Integration

1. Tribunal reviews only in G-Drive
2. Dashboard sheets auto-update
3. Discord notifications from G-Drive events

---

## What Stays in GitHub

| In GitHub | In G-Drive |
|-----------|------------|
| Code (`runtime/`, `core/`, etc.) | Task documents |
| Specs (markdown source) | Specs (readable copies) |
| Process definitions | Activity logs |
| ADRs (source of truth) | Tribunal reviews |
| Tests | Work logs |
| CI/CD configs | Dashboards |

---

## Consequences

### Positive

- Humans can see and participate in coordination
- Real-time collaboration on tasks
- Better search and discoverability
- Non-dev stakeholders included
- Tribunal reviews are human-readable documents

### Negative

- Adds external dependency (Google)
- Requires API credentials management
- Two systems to keep in sync initially
- Network required for coordination

### Mitigations

- Local cache of critical state
- Graceful degradation if G-Drive unavailable
- Clear ownership: GitHub = code, G-Drive = coordination

---

## Next Steps

1. **Q33N:** Create G-Drive folder structure manually
2. **BEE-001:** Build `gdrive-hive-interface` PyBee
3. **Test:** Create one task in G-Drive, run through full workflow
4. **Iterate:** Refine templates based on actual use

---

*"Code lives in GitHub. Coordination lives in G-Drive. Humans can see both."*
