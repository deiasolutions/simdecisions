# BOK-REVIEW-001 Addendum: G-Drive Interface & Post-Reject QC

**Date:** 2026-02-04
**Author:** Q33N (Dave)
**Status:** DRAFT
**Extends:** BOK-REVIEW-001-GitHub-Tribunal-Pattern.md

---

## 1. Post-Reject Human Quality Control

### 1.1 Problem

If the tribunal rejects a submission, the human never sees it. This creates blind spots:

- Tribunal may be too strict (false negatives)
- Tribunal may misunderstand context
- Good work gets buried in `needs-work` limbo
- No feedback loop to calibrate tribunal

### 1.2 Solution

**Human QC sampling of rejected PRs:**

```
PR submitted → Tribunal rejects → Feedback posted
                                        ↓
                     [Sampling: 10-20% of rejects go to human QC queue]
                                        ↓
                     Human reviews: Was rejection correct?
                                        ↓
                     If tribunal wrong → Override + calibration signal
                     If tribunal right → Confirm + training signal
```

### 1.3 QC Queue

| Field | Description |
|-------|-------------|
| `qc_sampled` | Boolean — was this reject sampled for QC? |
| `qc_reviewed` | Boolean — has human reviewed? |
| `qc_verdict` | `tribunal_correct` / `tribunal_wrong` / `partial` |
| `qc_notes` | Human notes on what tribunal missed |

### 1.4 Calibration Signal

When human overrides tribunal:

```yaml
calibration_event:
  type: "tribunal_override"
  pr_number: 42
  tribunal_verdict: "reject"
  human_verdict: "approve"
  criteria_miscalibrated:
    - "narrow_scope"  # Tribunal was too strict here
  notes: "Config changes were justified, tribunal didn't read commit message"
```

Feed these back into judge prompt tuning.

---

## 2. Consensus Opinion (Narrative)

### 2.1 Current Model (Scores Only)

```
Gemini: 5/6
Codex: 3/6
Anthropic: 5/6
Total: 13/18 → Pass
```

**Problem:** Scores don't capture WHY. No shared understanding.

### 2.2 New Model (Narrative + Vote)

Each judge writes:

1. **Assessment** — 2-3 paragraph analysis
2. **Vote** — Approve / Reject / Abstain
3. **Key concerns** — Bullet points
4. **Recommendation** — What should submitter do?

Then **Aggregator synthesizes consensus opinion:**

```markdown
## Tribunal Consensus Opinion

**Verdict:** APPROVE with notes (2-1 vote)

**Summary:**
The submission implements TASK-009 Event Ledger per ADR-001 specification.
All three judges agree the core implementation is sound. Test coverage is
comprehensive. One judge (Codex) flagged scope creep in config.py changes;
two judges accepted the justification in commit message.

**Key Agreement:**
- Schema matches spec exactly
- Tests comprehensive, coverage +4%
- Provenance clear (links to ADR-001, TASK-009)

**Key Disagreement:**
- Scope: Codex strict, Gemini/Anthropic accepted justification

**Recommendation to Human:**
Review the config.py changes. If acceptable, merge. If not, request
submitter split into separate PR.
```

---

## 3. Google Docs Integration

### 3.1 Why Google Docs?

| GitHub Reviews | Google Docs |
|----------------|-------------|
| Fragmented (per-file comments) | Single narrative document |
| Hard to compare judge opinions | Side-by-side judge sections |
| No real-time collaboration | Human can comment inline |
| Ephemeral (buried in PR history) | Persistent, searchable |
| Dev-focused format | Human-readable format |

### 3.2 Document Structure

```
📄 [TASK-009] Event Ledger v1 — Tribunal Review

├── Header
│   ├── PR Link
│   ├── Task Reference
│   ├── Submitting Agent
│   └── Tribunal Date
│
├── Judge 1: Gemini Q33N
│   ├── Assessment (narrative)
│   ├── Scores (I/N/V/E/S/T)
│   ├── Vote: APPROVE
│   └── Notes
│
├── Judge 2: Codex Q33N
│   ├── Assessment (narrative)
│   ├── Scores (I/N/V/E/S/T)
│   ├── Vote: REQUEST CHANGES
│   └── Notes
│
├── Judge 3: Anthropic Q33N
│   ├── Assessment (narrative)
│   ├── Scores (I/N/V/E/S/T)
│   ├── Vote: APPROVE
│   └── Notes
│
├── Consensus Opinion
│   ├── Aggregated verdict
│   ├── Key agreements
│   ├── Key disagreements
│   └── Recommendation
│
├── Human Decision
│   ├── Verdict: [pending]
│   ├── Notes: [pending]
│   └── Timestamp: [pending]
│
└── Metadata
    ├── Embeddings scores
    ├── Moderation results
    └── Kaizen metrics
```

### 3.3 G-Drive Folder Structure

```
SimDecisions Tribunal/
├── 2026/
│   ├── 02/
│   │   ├── 04/
│   │   │   ├── [TASK-009] Event Ledger v1 — Tribunal Review.gdoc
│   │   │   ├── [TASK-010] API Routes — Tribunal Review.gdoc
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── Templates/
│   └── Tribunal Review Template.gdoc
├── QC Queue/
│   └── [Sampled rejects for human review]
└── Calibration Log/
    └── Tribunal Override Events.gsheet
```

---

## 4. G-Drive Interface (PyBee)

### 4.1 Interface Spec

```python
# PYBEE: gdrive-tribunal-writer

class GDriveTribunalWriter:
    """
    Writes tribunal reviews to Google Docs.
    Reads human decisions from docs.
    """

    def create_review_doc(
        self,
        task_id: str,
        pr_number: int,
        pr_title: str,
        submitter: str
    ) -> str:
        """
        Create new tribunal review doc from template.
        Returns: doc_id
        """
        pass

    def write_judge_section(
        self,
        doc_id: str,
        judge_id: str,
        assessment: str,
        scores: Dict[str, int],
        vote: str,
        notes: str
    ) -> None:
        """
        Write one judge's section to the doc.
        """
        pass

    def write_consensus(
        self,
        doc_id: str,
        verdict: str,
        summary: str,
        agreements: List[str],
        disagreements: List[str],
        recommendation: str
    ) -> None:
        """
        Write aggregated consensus section.
        """
        pass

    def read_human_decision(
        self,
        doc_id: str
    ) -> Optional[Dict]:
        """
        Poll doc for human decision.
        Returns None if not yet decided.
        Returns {verdict, notes, timestamp} if decided.
        """
        pass

    def move_to_archive(
        self,
        doc_id: str,
        outcome: str  # "merged" | "abandoned" | "qc_override"
    ) -> None:
        """
        Move completed review to archive folder.
        """
        pass
```

### 4.2 Authentication

- Service account with G-Drive API access
- Scoped to SimDecisions Tribunal folder only
- Credentials in secrets manager (not in repo)

### 4.3 Workflow Integration

```
1. PR opened
2. Aggregator creates Google Doc (from template)
3. Each judge writes their section to doc (parallel)
4. Aggregator writes consensus section
5. Aggregator posts doc link to GitHub PR comment
6. Human reviews doc, fills in decision section
7. Aggregator polls for decision
8. On decision: update GitHub labels, write to ledger, archive doc
```

---

## 5. Updated Workflow Diagram

```
┌─────────────┐
│ Agent       │
│ submits PR  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                     TRIBUNAL                              │
│                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│  │ Gemini  │    │ Codex   │    │Anthropic│              │
│  │ writes  │    │ writes  │    │ writes  │              │
│  │ to doc  │    │ to doc  │    │ to doc  │              │
│  └────┬────┘    └────┬────┘    └────┬────┘              │
│       └──────────────┼──────────────┘                    │
│                      ▼                                   │
│              ┌──────────────┐                            │
│              │ Aggregator   │                            │
│              │ writes       │                            │
│              │ consensus    │                            │
│              └──────┬───────┘                            │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Google Doc   │
              │ with full    │
              │ review       │
              └──────┬───────┘
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
┌──────────────┐           ┌──────────────┐
│ PASS         │           │ REJECT       │
│ → ready-for- │           │ → needs-work │
│    dave      │           │ → feedback   │
└──────┬───────┘           └──────┬───────┘
       │                          │
       ▼                          ▼
┌──────────────┐           ┌──────────────┐
│ Dave reviews │           │ QC Sample?   │
│ doc, decides │           │ 10-20%       │
└──────┬───────┘           └──────┬───────┘
       │                          │
       ▼                          ▼
┌──────────────┐           ┌──────────────┐
│ Merge / More │           │ Human QC     │
│ changes      │           │ reviews      │
└──────────────┘           │ rejection    │
                           └──────┬───────┘
                                  │
                                  ▼
                           ┌──────────────┐
                           │ Calibration  │
                           │ signal       │
                           └──────────────┘
```

---

## 6. Implementation Tasks

| Task | Description | Effort |
|------|-------------|--------|
| TASK-030 | Create G-Drive interface PyBee | 4 hrs |
| TASK-031 | Design tribunal review doc template | 2 hrs |
| TASK-032 | Update aggregator to write consensus narrative | 3 hrs |
| TASK-033 | Implement QC sampling for rejects | 2 hrs |
| TASK-034 | Add calibration signal to judge prompt tuning | 3 hrs |
| TASK-035 | Create QC Queue folder and workflow | 2 hrs |

---

## 7. Open Questions

1. **Polling frequency:** How often does aggregator check for human decision?
2. **Template format:** What exact sections in the Google Doc template?
3. **QC sample rate:** 10%? 20%? Configurable per project?
4. **Multi-reviewer:** Can multiple humans comment on same doc?

---

*Addendum to BOK-REVIEW-001. G-Drive becomes the human-readable record of tribunal decisions.*
