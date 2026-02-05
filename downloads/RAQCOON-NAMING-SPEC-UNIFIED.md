# RAQCOON Unified Naming Specification

**Version:** 1.0.0
**Created:** 2026-01-26
**Status:** FINALIZED

---

## 1. Comparison of Source Specs

| Aspect | HIVE-TASKS-STRUCTURE | RAQCOON-V1 | Unified |
|--------|---------------------|------------|---------|
| Format length | 6 segments | 7 segments | 7 segments |
| Date | YYYYMMDD[-HHMM] | YYYYMMDD | YYYYMMDD-HHMM |
| Project | 3-4 char | 3 char | 3 char |
| Bee ID | B + 3 digits (B002) | Role + number (D001) | **Role + number** ✓ |
| Agent type | TLA (CLC, CDX) | TYP (CCC, CCH) | **Merged registry** |
| Priority | In identifier (P1-B002) | Separate field | **Separate field** ✓ |
| Category | TYPE (TASK, RESP) | CAT (TSK, RSP) | **3-char CAT** ✓ |
| Subject | kebab-case | kebab-case | kebab-case |

---

## 2. Unified Format

```
YYYYMMDD-HHMM-PRJ-BEE-AGT-PRI-CAT-subject.md
```

| Position | Field | Length | Required | Description |
|----------|-------|--------|----------|-------------|
| 1 | DATE | 8 | Yes | YYYYMMDD |
| 2 | TIME | 4 | Yes | HHMM (24-hour) |
| 3 | PRJ | 3 | Yes | Project code |
| 4 | BEE | 3-4 | Yes | Role + number or wildcard |
| 5 | AGT | 3 | Yes | Agent type |
| 6 | PRI | 2 | Yes | Priority level |
| 7 | CAT | 3 | Yes | Category |
| 8 | subject | variable | Yes | Kebab-case description |

**Why mandatory HHMM:** Eliminates same-day collisions, enables precise ordering, minimal overhead.

---

## 3. Field Specifications

### 3.1 Project Codes (PRJ)

| Code | Project | Notes |
|------|---------|-------|
| HIV | HiveMind | **Default** - general hive work |
| FBB | FBB Project | |
| DIA | DEIA Core | |
| RAQ | RAQCOON | Platform development |
| TST | Test/Sandbox | |

**Rules:**
- Exactly 3 uppercase letters
- Unique across organization
- Default to `HIV` if unspecified

---

### 3.2 Bee Identifiers (BEE)

#### Roles

| Letter | Role | Description |
|--------|------|-------------|
| Q | Queen | Coordinator, orchestrator |
| D | Developer | Writes code |
| T | Tester | Writes/runs tests |
| R | Reviewer | Code review, PR review |
| A | Architect | Planning, design, specs |
| W | Writer | Documentation |
| S | Security | Audits, scanning |
| O | Ops | CI/CD, deployment |
| I | Investigator | Research, exploration |
| X | Generalist | Any role (fallback) |

#### Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| X### | Specific bee | D001, T002, Q001 |
| XNY | Any bee of role X | DNY, TNY, RNY |
| ANY | Any available bee | ANY |

**Examples:**
- `D001` - Developer bee #1
- `DNY` - Any developer
- `Q001` - Queen #1 (typically one per hive)
- `ANY` - First available bee regardless of role

---

### 3.3 Agent Types (AGT)

Merged registry from both specs:

| Code | Full Name | Mode | Notes |
|------|-----------|------|-------|
| **Claude** ||||
| CLC | Claude Code CLI | Interactive | PTY-based |
| CCH | Claude Code Headless | JSON | `--output-format json` |
| CLA | Claude API | API | Direct Anthropic API |
| CLW | Claude Web | Web | claude.ai interface |
| **OpenAI** ||||
| CDX | Codex CLI | Interactive | PTY-based |
| CDH | Codex Headless | JSON | JSON output mode |
| GPT | GPT-4/4o API | API | Direct OpenAI API |
| CPL | GitHub Copilot | IDE | IDE integration |
| **Google** ||||
| GEM | Gemini API | API | |
| GCA | Gemini Code Assist | IDE | |
| **Open Source** ||||
| OLM | Ollama | Local | Any Ollama model |
| LMA | Llama | Local | Direct Llama |
| MST | Mistral | Local/API | |
| DPS | DeepSeek | API | |
| **Other** ||||
| PPX | Perplexity | API | |
| GRK | Grok | API | |
| **Internal** ||||
| Q3N | Q33N Orchestrator | Internal | Coordination only |
| HMN | Human | Manual | Human-performed task |

**Rationale:**
- 3-char codes throughout (consistent)
- Distinguish interactive (CLC) from headless (CCH) modes
- Keep comprehensive coverage from HIVE-TASKS TLA registry

---

### 3.4 Priority Levels (PRI)

| Code | Level | SLA Hint | Description |
|------|-------|----------|-------------|
| P0 | Critical | Immediate | Drop everything |
| P1 | High | < 1 hour | Next after current |
| P2 | Normal | < 4 hours | Standard queue |
| P3 | Low | Best effort | When idle |

---

### 3.5 Categories (CAT)

| Code | Category | Direction | Description |
|------|----------|-----------|-------------|
| **Work Items** ||||
| TSK | Task | Q→Bee | Work assignment |
| BUG | Bug | Q→Bee | Bug fix request |
| FEA | Feature | Q→Bee | Feature request |
| **Responses** ||||
| RSP | Response | Bee→Q | Completed work |
| BLK | Blocked | Bee→Q | Cannot proceed |
| QST | Question | Bee→Q | Needs clarification |
| **Planning** ||||
| SPR | Sprint | Q | Sprint definition |
| SPC | Spec | Q/A | Specification |
| PLN | Plan | Q/A | Planning document |
| **Reports** ||||
| RPT | Report | Any | Status/analysis |
| LOG | Log | Any | Activity log |
| MET | Metrics | Q | Performance data |
| **Config** ||||
| CFG | Config | Q | Configuration |
| CTX | Context | Q | Project context |

---

## 4. File Examples

### 4.1 Tasks (Q33N → Bee)

```
20260126-1030-FBB-DNY-CCH-P1-TSK-fix-login-validation.md
20260126-1045-HIV-D001-CLC-P0-BUG-critical-null-pointer.md
20260126-1100-RAQ-ANY-CDH-P2-FEA-add-retry-logic.md
20260126-1115-DIA-TNY-CCH-P2-TSK-write-unit-tests.md
```

### 4.2 Responses (Bee → Q33N)

```
20260126-1142-FBB-D001-CCH-P1-RSP-fix-login-validation.md
20260126-1130-HIV-D002-CLC-P0-RSP-critical-null-pointer.md
20260126-1200-RAQ-D003-CDH-P2-BLK-add-retry-logic.md
```

### 4.3 Planning & Reports

```
20260126-0900-HIV-Q001-Q3N-P1-SPR-week-04-sprint.md
20260126-1700-FBB-Q001-Q3N-P2-RPT-daily-summary.md
20260126-0800-RAQ-A001-HMN-P2-SPC-mcp-server-design.md
```

---

## 5. Parsing

### 5.1 Regex Pattern

```python
import re

PATTERN = r'^(\d{8})-(\d{4})-([A-Z]{3})-([A-Z]{1,3}\d{0,3}|ANY)-([A-Z]{3})-P([0-3])-([A-Z]{3})-(.+)\.md$'

def parse_filename(filename):
    match = re.match(PATTERN, filename)
    if not match:
        return None
    return {
        'date': match.group(1),        # 20260126
        'time': match.group(2),        # 1030
        'project': match.group(3),     # FBB
        'bee': match.group(4),         # DNY or D001
        'agent': match.group(5),       # CCH
        'priority': int(match.group(6)), # 1
        'category': match.group(7),    # TSK
        'subject': match.group(8)      # fix-login-validation
    }
```

### 5.2 Filename Generator

```python
from datetime import datetime

def generate_filename(project, bee, agent, priority, category, subject, dt=None):
    dt = dt or datetime.now()
    return f"{dt:%Y%m%d}-{dt:%H%M}-{project}-{bee}-{agent}-P{priority}-{category}-{subject}.md"

# Example
generate_filename("FBB", "DNY", "CCH", 1, "TSK", "fix-login")
# → "20260126-1030-FBB-DNY-CCH-P1-TSK-fix-login.md"
```

---

## 6. Directory Structure

```
.deia/hive/
├── index.db                    # SQLite index (preferred)
├── index.json                  # JSON fallback
├── workspaces/
│   └── {project}/              # Per-project folders
│       ├── queue/              # Pending tasks (unclaimed)
│       ├── claimed/            # In-progress (bee has lock)
│       ├── buzz/               # Responses awaiting review
│       └── archive/
│           ├── tasks/
│           ├── responses/
│           └── index.db        # Project-specific embeddings
└── config/
    └── hive.json               # Global hive config
```

**Change from V1:** Project-based subfolders under `workspaces/` for scalability.

---

## 6.1 Task Claim Protocol

**Problem:** Multiple bees might try to grab the same task simultaneously.

**Solution:** Pessimistic locking via Q33N-mediated handshake.

### Claim Flow

```
┌─────────┐         ┌─────────┐         ┌─────────────┐
│  BEE    │         │  Q33N   │         │ Filesystem  │
└────┬────┘         └────┬────┘         └──────┬──────┘
     │                   │                     │
     │  1. /claim <task> │                     │
     │──────────────────>│                     │
     │                   │  2. Check queue/    │
     │                   │────────────────────>│
     │                   │                     │
     │                   │  3. File exists?    │
     │                   │<────────────────────│
     │                   │                     │
     │   [IF YES]        │  4. Move to claimed/│
     │                   │────────────────────>│
     │                   │                     │
     │  5. GRANTED       │                     │
     │   + new path      │                     │
     │<──────────────────│                     │
     │                   │                     │
     │   [IF NO]         │                     │
     │  5. DENIED        │                     │
     │   (already taken) │                     │
     │<──────────────────│                     │
     │                   │                     │
     │  6. Work on task  │                     │
     │   at claimed/path │                     │
     │                   │                     │
     │  7. Post response │                     │
     │   to buzz/        │                     │
     │──────────────────>│                     │
     │                   │  8. Archive both    │
     │                   │────────────────────>│
     │                   │                     │
```

### Claim States

| Location | State | Who Can Act |
|----------|-------|-------------|
| `queue/` | Unclaimed | Any bee can request |
| `claimed/` | Locked | Only assigned bee |
| `buzz/` | Completed | Q33N reviews |
| `archive/` | Done | Reference only |

### Claim Message Format

**Bee → Q33N (Request):**
```
/claim 20260126-1030-FBB-DNY-CCH-P1-TSK-fix-login.md
```

**Q33N → Bee (Granted):**
```
CLAIM GRANTED
Task: 20260126-1030-FBB-DNY-CCH-P1-TSK-fix-login.md
Assigned: D001
New Path: .deia/hive/workspaces/FBB/claimed/20260126-1030-FBB-D001-CCH-P1-TSK-fix-login.md
```

Note: Filename updates from `DNY` → `D001` when claimed.

**Q33N → Bee (Denied):**
```
CLAIM DENIED
Task: 20260126-1030-FBB-DNY-CCH-P1-TSK-fix-login.md
Reason: Already claimed by D002
Suggestion: Try /queue next
```

### Claim Rules

6.1.1 **Only Q33N moves files** - Bees never touch queue/ or claimed/ directly.

6.1.2 **Atomic claim** - Q33N checks + moves in single operation (no TOCTOU race).

6.1.3 **Bee ID updated on claim** - `DNY` → `D001` in filename reflects assignment.

6.1.4 **Manual release only** - No automatic timeout. Q33N uses `/revoke` if needed.

6.1.5 **Voluntary release** - Bee can `/release <task>` if blocked, returns to queue/.

### Additional Commands

```
/claim <filename>             # Request to claim task
/release <filename>           # Release claimed task back to queue
/status <filename>            # Check task state and owner
```

### Index Tracking

When claimed, index.db updates:

```sql
UPDATE tasks SET
    status = 'claimed',
    assigned_bee = 'D001',
    claimed_at = '2026-01-26T10:32:15Z',
    filepath = 'workspaces/FBB/claimed/...'
WHERE filename = '...';
```

### Full Task Lifecycle

```
                    Q33N creates task
                           │
                           ▼
                    ┌─────────────┐
                    │   queue/    │  ← Unclaimed, any bee can request
                    └──────┬──────┘
                           │
                    Bee: /claim <task>
                    Q33N: GRANTED + new path
                           │
                           ▼
                    ┌─────────────┐
                    │  claimed/   │  ← Locked to specific bee
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         Bee works                 Bee blocked
              │                         │
              │                  Bee: /release
              │                   ─ OR ─
              │                  Q33N: /revoke
              │                         │
              │                         ▼
              │                  ┌─────────────┐
              │                  │   queue/    │
              │                  └─────────────┘
              │                    (retry loop)
              │
              ▼
       Bee posts response
              │
              ▼
       ┌─────────────┐
       │    buzz/    │  ← Response awaiting Q33N review
       └──────┬──────┘
              │
       Q33N reviews
              │
              ▼
       ┌─────────────┐
       │  archive/   │  ← Permanent. Both task + response.
       │  + index.db │  ← Voyage embedding generated.
       └─────────────┘
```

---

## 7. Slash Commands (Updated)

```
# Project
/project                      # Show active project
/project <PRJ>                # Switch to project
/project list                 # List all projects

# Tasks
/task <subject>               # Create P2 task (defaults: HIV, DNY, CCH)
/task <subject> -p <0-3>      # Create with priority
/task <subject> -b <BEE>      # Assign to specific bee
/task <subject> -a <AGT>      # Specify agent type
/task list                    # List queue for active project
/task list --all              # List all projects
/task status <filename>       # Check task state and owner

# Claims (Bee ↔ Q33N handshake)
/claim <filename>             # Bee requests to claim task
/release <filename>           # Bee releases task back to queue
/grant <filename> <BEE>       # Q33N manually assigns task
/revoke <filename>            # Q33N forces task back to queue

# Bees
/bee list                     # List all bees
/bee spawn <role> <agent>     # Spawn bee (e.g., /bee spawn D CCH)
/bee status <id>              # Get bee status
/bee kill <id>                # Terminate bee

# Queue
/queue                        # Show combined queue
/queue next                   # What's next (unclaimed only)
/queue --project <PRJ>        # Filter by project
/queue --claimed              # Show claimed tasks

# Help
/help                         # Command list
/help <command>               # Command details
```

---

## 8. Migration Notes

### 8.1 From HIVE-TASKS-STRUCTURE-SPEC

| Change | Action |
|--------|--------|
| B002 → D002 | Add role prefix based on bee config |
| TASK → TSK | Shorten to 3-char |
| Optional HHMM → Required | Always include time |
| TLA → AGT | Rename field, keep codes |

### 8.2 From RAQCOON-V1-SPEC

| Change | Action |
|--------|--------|
| CCC → CLC | Rename for consistency |
| Flat tasks/ → workspaces/{prj}/queue/ | Add project folders |
| 7 segments → 8 segments | Add TIME field |

### 8.3 Code Updates Required

| File | Changes |
|------|---------|
| `core/task_files.py` | New path structure, filename format |
| `runtime/server.py` | Update task endpoints |
| `kb/store.py` | No change (KB separate from tasks) |
| UI mockups | Path updates |

---

## 9. Validation Rules

| Rule | Regex/Check | Error |
|------|-------------|-------|
| Project exists | Lookup in config | "Unknown project: XXX" |
| Bee format valid | `^[QDTRASWOIX](NY\|\d{3})\|ANY$` | "Invalid bee: XXX" |
| Agent supported | Lookup in registry | "Unknown agent: XXX" |
| Priority 0-3 | `^P[0-3]$` | "Priority must be P0-P3" |
| Category valid | Lookup in registry | "Unknown category: XXX" |
| Subject kebab | `^[a-z0-9]+(-[a-z0-9]+)*$` | "Subject must be kebab-case" |
| Subject length | ≤ 80 chars | "Subject exceeds 80 char limit" |
| Reserved names | Not CON, PRN, AUX, NUL, COM1-9, LPT1-9 | "Reserved filename on Windows" |

---

## 10. Summary of Key Decisions

| Decision | Rationale |
|----------|-----------|
| **7→8 segments (add TIME)** | Same-day disambiguation essential at scale |
| **Role-based bees (D001 vs B001)** | More informative, enables role routing |
| **3-char codes throughout** | Consistent, parseable, compact |
| **Project subfolders** | Scalability—flat folders won't survive 100+ tasks/day |
| **Merge TLA + TYP → AGT** | Single authoritative registry |
| **SQLite preferred over JSON** | Concurrent access, vector search |
| **Mandatory fields** | No optionals in filename—predictable parsing |
| **claimed/ folder + handshake** | Pessimistic locking prevents race conditions |
| **Q33N moves files, bees don't** | Single authority over task state |
| **Bee ID updates on claim** | DNY → D001 reflects actual assignment |

---

## 11. Open Items

~~11.1 Should `active/` folder exist (in-progress tasks) or just track in index?~~
**RESOLVED:** Use `claimed/` folder with Q33N-mediated handshake protocol (Section 6.1).

~~11.2 Max subject length?~~
**RESOLVED:** 80 characters. Validated on create. Balances expressiveness with Windows MAX_PATH safety.

~~11.3 Archive retention policy?~~
**RESOLVED:** Indefinite. Never auto-delete. Archive is permanent record.

~~11.4 Claim timeout duration?~~
**RESOLVED:** None. Manual `/revoke` only. Q33N monitors with `/queue --claimed` and revokes as needed. Keeps it simple.

---

**Status:** FINALIZED - All open items resolved. Supersedes HIVE-TASKS-STRUCTURE-SPEC and RAQCOON-V1-SPEC.
