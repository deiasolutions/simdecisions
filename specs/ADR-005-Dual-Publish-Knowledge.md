# ADR-005: Dual-Publish Knowledge Pattern

**Status:** PROPOSED
**Date:** 2026-02-04
**Author:** Q33N (Dave) + BEE-001

---

## Decision

All knowledge artifacts (BOK patterns, specs, decisions, learnings) are published to **both** GitHub and G-Drive. GitHub is source of truth for machines. G-Drive is the human-readable layer.

---

## Context

### Problem

Knowledge captured in BOK is buried:
- Markdown files in git repo
- Non-devs never see it
- No easy way to comment or discuss
- Patterns exist but aren't discoverable
- Humans ask questions already answered in BOK

### Solution

**Dual-publish everything:**

1. **GitHub** — Source of truth, version controlled, bot-readable
2. **G-Drive** — Human-readable copies, commentable, searchable
3. **Discord** — Notifications when new knowledge added

---

## Knowledge Types & Destinations

| Knowledge Type | GitHub Location | G-Drive Location | Discord Channel |
|----------------|-----------------|------------------|-----------------|
| **BOK Patterns** | `bok/patterns/` | `BOK/Patterns/` | #bok-updates |
| **ADRs** | `specs/ADR-*.md` | `Specs/ADRs/` | #specs |
| **Specs** | `specs/SPEC-*.md` | `Specs/` | #specs |
| **Federalist Papers** | `federalist/` | `Federalist/` | #philosophy |
| **Tribunal Reviews** | — | `Tribunal/` | #tribunal |
| **Decisions** | `.deia/decisions/` | `Decisions/` | #decisions |
| **Learnings** | `MEMORY.md` / logs | `Learnings/` | — |

---

## Dual-Publish Workflow

### Option A: GitHub Primary (Sync to G-Drive)

```
Author writes in GitHub (markdown)
          │
          ▼
    Commit / PR merged
          │
          ▼
    PyBee: gdrive-sync
          │
          ├── Convert markdown → Google Doc
          ├── Upload to appropriate G-Drive folder
          └── Post notification to Discord
```

**Pros:** Single source of truth, version control
**Cons:** Authors must use markdown/git

### Option B: G-Drive Primary (Sync to GitHub)

```
Author writes in G-Drive (Google Doc)
          │
          ▼
    Mark doc as "Ready"
          │
          ▼
    PyBee: github-sync
          │
          ├── Convert Google Doc → markdown
          ├── Commit to appropriate GitHub folder
          └── Post notification to Discord
```

**Pros:** Accessible to non-devs, rich formatting
**Cons:** Merge conflicts, version control harder

### Option C: Bidirectional (Recommended)

```
┌─────────────┐                    ┌─────────────┐
│   GitHub    │◀── sync-bot ─────▶│   G-Drive   │
│   (source)  │                    │  (readable) │
└─────────────┘                    └─────────────┘
       │                                  │
       └────────────┬─────────────────────┘
                    ▼
              ┌──────────┐
              │ Discord  │
              │ (notify) │
              └──────────┘
```

- **Bots** write to GitHub → synced to G-Drive
- **Humans** write to G-Drive → synced to GitHub
- **Conflict resolution:** Last-write-wins with audit log, or human arbitration

---

## G-Drive BOK Structure

```
📁 SimDecisions/
│
├── 📁 BOK/
│   │   # Book of Knowledge — patterns, antipatterns
│   │
│   ├── 📁 Patterns/
│   │   ├── 📄 BOK-SIM-001 - Oort Cloud Partitioning.gdoc
│   │   ├── 📄 BOK-SIM-002 - Prophecy Engine.gdoc
│   │   ├── 📄 BOK-REVIEW-001 - GitHub Tribunal.gdoc
│   │   └── ...
│   │
│   ├── 📁 Antipatterns/
│   │   ├── 📄 ANTI-001 - Premature Deletion.gdoc
│   │   └── ...
│   │
│   └── 📁 Learnings/
│       ├── 📄 2026-02 Learnings.gdoc
│       └── ...
│
├── 📁 Specs/
│   ├── 📁 ADRs/
│   │   ├── 📄 ADR-001 - Event Ledger Foundation.gdoc
│   │   ├── 📄 ADR-002 - API Endpoint Registry.gdoc
│   │   └── ...
│   │
│   └── 📁 Feature Specs/
│       ├── 📄 SPEC-PyBee - Python Executable Species.gdoc
│       └── ...
│
├── 📁 Federalist/
│   ├── 📄 NO-01 - On the Constitution of Minds.gdoc
│   ├── 📄 NO-02 - On Queens and Tyranny.gdoc
│   └── ...
│
└── 📁 Decisions/
    ├── 📄 2026-02-04 - G-Drive as Coordination Layer.gdoc
    └── ...
```

---

## Sync Bot Specification

### PyBee: `knowledge-sync`

```python
class KnowledgeSync:
    """
    Syncs knowledge between GitHub and G-Drive.
    Notifies Discord on changes.
    """

    def sync_github_to_gdrive(self, github_path: str):
        """
        1. Read markdown from GitHub
        2. Convert to Google Doc format
        3. Upload/update in G-Drive
        4. Notify Discord
        """
        pass

    def sync_gdrive_to_github(self, doc_id: str):
        """
        1. Read Google Doc
        2. Convert to markdown
        3. Commit to GitHub
        4. Notify Discord
        """
        pass

    def detect_changes(self):
        """
        Poll both sources for changes.
        Trigger appropriate sync direction.
        """
        pass

    def notify_discord(self, change_type: str, title: str, url: str):
        """
        Post to appropriate Discord channel.
        """
        pass
```

---

## Discord Notifications

| Event | Channel | Message |
|-------|---------|---------|
| New BOK pattern | #bok-updates | "📚 New pattern: BOK-SIM-003 - Alterverse Tree [link]" |
| Spec updated | #specs | "📝 Updated: ADR-001 - Event Ledger [link]" |
| Federalist added | #philosophy | "📜 New Federalist: NO-21 - On the Planetary Ethic [link]" |
| Decision made | #decisions | "⚖️ Decision: G-Drive as Coordination Layer [link]" |

---

## Human Discovery

### Search

G-Drive search works across all docs. Humans can find knowledge by keyword.

### Browse

Folder structure mirrors knowledge taxonomy. Humans can explore.

### Comment

Google Docs allow inline comments. Humans can ask questions, suggest edits.

### Subscribe

G-Drive notifications for folder changes. Humans opt-in to updates.

---

## Consequences

### Positive

- Knowledge is discoverable by humans
- Non-devs can participate
- Comments enable discussion
- Discord keeps everyone informed
- Two audiences, two formats, one source of truth

### Negative

- Sync complexity
- Potential for drift if sync fails
- Two places to look

### Mitigations

- Clear "source of truth" rules
- Audit log of syncs
- Alerts on sync failures
- Regular reconciliation checks

---

## Implementation

| Task | Description |
|------|-------------|
| TASK-040 | Create G-Drive BOK folder structure |
| TASK-041 | Build markdown → Google Doc converter |
| TASK-042 | Build Google Doc → markdown converter |
| TASK-043 | Create sync bot with change detection |
| TASK-044 | Set up Discord webhook notifications |
| TASK-045 | Initial sync of existing BOK to G-Drive |

---

*"If humans can't find it, it doesn't exist."*
