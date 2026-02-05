# Hive Tasks Structure Specification

**Version:** 0.1.0-draft
**Created:** 2026-01-26
**Status:** QUEUED FOR IMPLEMENTATION

---

## 1. Overview

### 1.1 Purpose
Define the directory structure for hive task management across multiple projects/workspaces, with semantic search capability via Voyage embeddings.

### 1.2 Scope
- MVP: Single workspace (`project_1`) with 3-folder structure
- Future: Multi-workspace support, full 6-folder structure, standardization across CLI repos

---

## 2. Directory Structure

### 2.1 Full Hierarchy

```
.deia/hive/
└── workspaces/
    └── project_1/
        ├── queue/           ← Ready for bees
        ├── buzz/            ← Bee responses
        ├── archive/
        │   ├── tasks/       ← Completed task requests
        │   ├── responses/   ← Completed responses
        │   └── index.db     ← Semantic search index
        ├── backlog/         ← [FUTURE] Defined but not prioritized
        ├── future/          ← [FUTURE] Someday/maybe
        └── on-hold/         ← [FUTURE] Paused work
```

### 2.2 MVP Implementation (Phase 1)

```
.deia/hive/
└── workspaces/
    └── project_1/
        ├── queue/
        ├── buzz/
        └── archive/
            ├── tasks/
            ├── responses/
            └── index.db
```

### 2.3 Why "workspaces/"
- "projects" is overloaded (Claude Projects, git projects, IDE projects)
- "products" implies shipped/released items
- "workspaces" is neutral, scales to teams, clients, or organizational units

---

## 3. File Naming Conventions

### 3.1 Universal Format

All files follow this pattern for parseability:

```
{DATE}-{PROJECT}-{TLA}-{TYPE}-{IDENTIFIER}-{subject}.md
```

| Segment | Format | Example |
|---------|--------|---------|
| DATE | `YYYYMMDD` or `YYYYMMDD-HHMM` | `20260126`, `20260126-1430` |
| PROJECT | 3-4 char code | `PRJ1`, `RAQC` |
| TLA | 3-letter LLM/CLI code | `CLC`, `CDX` |
| TYPE | File type | `TASK`, `RESP`, `NOTE` |
| IDENTIFIER | Priority + BeeID or just BeeID | `P1-B002`, `B002` |
| subject | kebab-case description | `api-refactor` |

### 3.2 LLM/CLI Type Codes (TLA Registry)

| TLA | Full Name | Category |
|-----|-----------|----------|
| **Claude Family** |||
| CLC | Claude Code | CLI |
| CLA | Claude API | API |
| CLW | Claude Web (claude.ai) | Web |
| **OpenAI Family** |||
| CDX | Codex | CLI |
| GPT | GPT-4 / GPT-4o | API |
| CPL | GitHub Copilot | IDE |
| **Google Family** |||
| GEM | Gemini | API |
| GCP | Gemini Code Assist | IDE |
| **Open Source** |||
| LMA | Llama (Meta) | Local |
| MST | Mistral | Local/API |
| DPS | DeepSeek | API |
| **Other** |||
| PPX | Perplexity | API |
| GRK | Grok | API |
| Q3N | Q33N (Orchestrator) | Internal |
| HMN | Human | Manual |

**Adding New TLAs:**
- Must be exactly 3 uppercase letters
- Should be mnemonic (first letters or phonetic)
- Add to this registry before use

### 3.3 Project Codes

| Code | Project | Notes |
|------|---------|-------|
| PRJ1 | project_1 | Initial test workspace |
| RAQC | RAQCOON | Main platform |
| DEIA | DEIA Solutions | Parent org work |

**Rules:**
- 3-4 uppercase characters
- Unique across all workspaces
- Defined in `workspace.json`

### 3.4 Task Requests (queue/)

```
{DATE}-{PROJECT}-{TLA}-TASK-{PRIORITY}-{BEE}-{subject}.md
```

**Examples:**
```
20260126-PRJ1-CLC-TASK-P0-B002-critical-hotfix.md    # Claude Code, P0, assigned
20260126-RAQC-CDX-TASK-P1-B005-api-refactor.md       # Codex, P1, assigned
20260126-PRJ1-Q3N-TASK-P2-queue-router-fix.md        # Q33N created, unassigned
```

**Priority Levels:**
| Priority | Meaning |
|----------|---------|
| P0 | Critical / blocking |
| P1 | Urgent / high |
| P2 | Normal |
| P3 | Low / nice-to-have |

**Bee ID Format:** `B` + 3-digit number (e.g., `B002`, `B015`)

### 3.5 Responses (buzz/)

```
{DATE}-{HHMM}-{PROJECT}-{TLA}-RESP-{BEE}-{subject}.md
```

**Examples:**
```
20260126-1430-PRJ1-CLC-RESP-B002-critical-hotfix.md
20260126-0915-RAQC-CDX-RESP-B005-api-refactor.md
```

### 3.6 Archived Items

Same naming as original, moved to `archive/tasks/` or `archive/responses/`.

### 3.7 Parsing Filenames (Pseudocode)

```python
import re

PATTERN = r'^(\d{8})(?:-(\d{4}))?-([A-Z]{3,4})-([A-Z]{3})-([A-Z]+)-(?:P(\d)-)?(?:B(\d{3})-)?(.+)\.md$'

def parse_filename(filename):
    match = re.match(PATTERN, filename)
    if not match:
        return None
    return {
        'date': match.group(1),           # 20260126
        'time': match.group(2),           # 1430 or None
        'project': match.group(3),        # PRJ1
        'tla': match.group(4),            # CLC
        'type': match.group(5),           # TASK or RESP
        'priority': match.group(6),       # 0-3 or None
        'bee_id': match.group(7),         # 002 or None
        'subject': match.group(8)         # critical-hotfix
    }
```

---

## 4. Semantic Search Index

### 4.1 Storage Options

| Option | Pros | Cons |
|--------|------|------|
| SQLite (`index.db`) | Single file, portable, SQL queries | No native vector ops |
| SQLite + sqlite-vec | Vector search built-in | Extension dependency |
| Markdown (`index.md`) | Human-readable, git-friendly | Slower queries |
| JSON (`index.json`) | Simple, flexible | No query language |

**Recommendation:** SQLite with optional sqlite-vec extension for vector search.

### 4.2 Index Schema (SQLite)

```sql
CREATE TABLE archive_index (
    id TEXT PRIMARY KEY,              -- task_id or response_id
    type TEXT NOT NULL,               -- 'task' | 'response'
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,           -- relative to workspace
    project TEXT NOT NULL,            -- project code (PRJ1, RAQC)
    tla TEXT NOT NULL,                -- LLM/CLI code (CLC, CDX)
    title TEXT,
    summary TEXT,
    tags TEXT,                        -- JSON array
    priority TEXT,                    -- P0-P3 or NULL
    bot_id TEXT,
    status TEXT,                      -- completed | failed | cancelled
    created_at TEXT NOT NULL,         -- ISO 8601
    completed_at TEXT,                -- ISO 8601
    content_hash TEXT,                -- SHA-256 for dedup
    voyage_model TEXT,                -- e.g., 'voyage-3'
    voyage_embedding BLOB             -- serialized vector
);

CREATE INDEX idx_type ON archive_index(type);
CREATE INDEX idx_project ON archive_index(project);
CREATE INDEX idx_tla ON archive_index(tla);
CREATE INDEX idx_status ON archive_index(status);
CREATE INDEX idx_created ON archive_index(created_at);
CREATE INDEX idx_tags ON archive_index(tags);
```

### 4.3 Required Fields for Semantic Search

| Field | Purpose |
|-------|---------|
| `voyage_embedding` | Vector for similarity search |
| `voyage_model` | Model version (for re-encoding if model changes) |
| `filename` | Human reference |
| `project` | Filter by workspace/project |
| `tla` | Filter by LLM/CLI type |
| `title` | Quick identification |
| `summary` | Search context |
| `tags` | Categorical filtering |
| `content_hash` | Deduplication |
| `created_at` | Time-based filtering |

### 4.4 Embedding Strategy

- **What to embed:** Concatenate `title + summary + tags` for task metadata embedding
- **When to embed:** On archive (not on create—saves API calls for abandoned tasks)
- **Model:** Voyage-3 (or latest)
- **Dimensions:** Store full vector; truncate at query time if needed

---

## 5. Workflow

### 5.1 Task Lifecycle

```
CREATE                  EXECUTE                 COMPLETE
   │                       │                       │
   ▼                       ▼                       ▼
queue/task.md  ───►  bee picks up  ───►  buzz/response.md
                                                   │
                                                   ▼
                                         archive/tasks/task.md
                                         archive/responses/response.md
                                         index.db (with embedding)
```

### 5.2 Archive Process (Pseudocode)

```python
def archive_completed_task(task_path, response_path, workspace):
    # 1. Move files
    task_dest = workspace / "archive/tasks" / task_path.name
    resp_dest = workspace / "archive/responses" / response_path.name
    shutil.move(task_path, task_dest)
    shutil.move(response_path, resp_dest)
    
    # 2. Generate embedding
    content = f"{task.title} {task.summary} {' '.join(task.tags)}"
    embedding = voyage_client.embed(content, model="voyage-3")
    
    # 3. Index both items
    index_item(task, task_dest, embedding, type="task")
    index_item(response, resp_dest, embedding, type="response")
```

---

## 6. Multi-Workspace Support (Future)

### 6.1 Adding New Workspaces

```
.deia/hive/workspaces/
├── project_1/
├── project_2/
└── client_acme/
```

### 6.2 Workspace Config (Future)

Each workspace may have a `workspace.json`:

```json
{
  "name": "project_1",
  "created": "2026-01-26",
  "default_priority": "P2",
  "auto_archive": true,
  "embedding_model": "voyage-3"
}
```

---

## 7. Migration Path

### 7.1 From Current Structure

**Current:**
```
.deia/hive/
├── tasks/{bot_id}/
├── responses/
└── archive/{bot_id}/
```

**Migration Steps:**
1. Create `workspaces/project_1/` structure
2. Move `tasks/*` → `workspaces/project_1/queue/` (flatten bot folders)
3. Move `responses/*` → `workspaces/project_1/buzz/`
4. Move `archive/*` → `workspaces/project_1/archive/tasks/`
5. Update `task_files.py` paths
6. Update server.py endpoints

### 7.2 Code Changes Required

| File | Changes |
|------|---------|
| `core/task_files.py` | Update `task_dir()`, `response_dir()`, `archive_dir()` |
| `runtime/server.py` | Update path references in task endpoints |
| UI files | Update any hardcoded paths |

---

## 8. Standardization Plan (Future)

### 8.1 Goal
Make this structure the standard for all DEIA CLI-managed repos.

### 8.2 Steps
1. Validate with `project_1` (current)
2. Document edge cases and adjustments
3. Create `deia init` command to scaffold structure
4. Publish as part of DEIA CLI tooling
5. Add workspace templates (coding, research, ops)

---

## 9. Open Questions

9.1 Should `index.db` be per-workspace or global (`.deia/hive/index.db`)?
9.2 Embed responses separately or link to parent task embedding?
9.3 Include full file content in embedding, or just metadata?

---

## 10. Acceptance Criteria

- [ ] `workspaces/project_1/` structure created
- [ ] `queue/`, `buzz/`, `archive/` folders functional
- [ ] Archive process moves both task and response
- [ ] `index.db` created with schema
- [ ] At least one task archived with Voyage embedding
- [ ] Semantic search query returns relevant results

---

**Status:** Ready for Dave review before implementation.
