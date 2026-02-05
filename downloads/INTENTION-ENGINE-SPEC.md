# Intention Engine Specification
## Semantic Extraction, Embedding & Refactoring System

**Version:** 0.1.0
**Date:** 2026-02-03
**Author:** daaaave-atx × Claude (Anthropic)
**Status:** SPEC — Ready for bee implementation
**Project:** SimDecisions / DEIA

---

## 1. Purpose

The Intention Engine extracts explicit and structural intentions from a codebase, embeds them as semantic vectors, and provides a queryable intention graph that serves as the authoritative spec for refactoring, gap analysis, and architectural alignment.

**Core thesis:** The codebase already contains its own specification — scattered across comments, docstrings, naming conventions, architectural choices, and companion documents. The Intention Engine makes that implicit spec explicit, searchable, and measurable.

---

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Intention** | A captured thought representing a goal, constraint, principle, or architectural decision |
| **Intention Record** | Structured JSON object containing the extracted intention, its source, category, and embedding vector |
| **Intention Graph** | The complete set of intention records with their semantic relationships (clusters, contradictions, orphans) |
| **Drift** | Measurable distance between stated intention and implemented behavior |
| **Ghost** | Implemented code with no discoverable intention (undocumented purpose) |
| **Orphan** | Stated intention with no corresponding implementation |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  INTENTION ENGINE                     │
│                                                       │
│  ┌─────────┐   ┌──────────┐   ┌───────────────────┐ │
│  │ Scanner │──▶│ Classifier│──▶│ Embedding Service │ │
│  └─────────┘   └──────────┘   └───────────────────┘ │
│       │              │                  │             │
│       ▼              ▼                  ▼             │
│  ┌─────────┐   ┌──────────┐   ┌───────────────────┐ │
│  │Raw Finds│   │ Intention │   │  Vector Store     │ │
│  │  .jsonl │   │ Records   │   │  (intentions.db)  │ │
│  └─────────┘   │  .json    │   └───────────────────┘ │
│                └──────────┘            │             │
│                      │                  │             │
│                      ▼                  ▼             │
│               ┌──────────────────────────┐           │
│               │    Analyzer / Query API   │           │
│               │  clusters, contradictions │           │
│               │  orphans, ghosts, drift   │           │
│               └──────────────────────────┘           │
└─────────────────────────────────────────────────────┘
```

### 3.1 Components

| Component | Responsibility | Output |
|-----------|---------------|--------|
| **Scanner** | Walk file tree, extract raw intention candidates | `raw_finds.jsonl` |
| **Classifier** | Categorize, deduplicate, score confidence | `intentions.json` |
| **Embedding Service** | Vectorize intention text | Vectors in `intentions.db` |
| **Analyzer** | Cluster, find contradictions, orphans, ghosts | Analysis reports |
| **Query API** | Semantic search over intention space | Search results |

---

## 4. Scanner Specification

### 4.1 File Types to Scan

| Category | Extensions | Priority |
|----------|-----------|----------|
| Python | `.py` | High |
| JavaScript/TypeScript | `.js`, `.ts`, `.tsx`, `.jsx` | High |
| Documentation | `.md`, `.txt` | High |
| Config | `.json`, `.yaml`, `.yml` | Medium |
| HTML | `.html` | Medium |
| Shell | `.bat`, `.sh` | Low |

### 4.2 Exclusions

Skip these paths:
- `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `.venv/`
- Any path matching `.deia/hive/archive/`
- Binary files (images, compiled, etc.)
- Files > 100KB (log files, generated output)

### 4.3 Extraction Triggers

The scanner identifies intention candidates through three methods:

#### 4.3.1 Keyword Triggers (Explicit Intentions)

Scan for lines containing these patterns. Extract the full containing comment/docstring/paragraph.

**Strong signals (high confidence):**
```
"I intend", "Goal:", "Constraint:", "Principle:", "Avoid:",
"Purpose:", "Why:", "Requirement:", "Must:", "Must not:",
"Never:", "Always:", "Ensure:", "Prevent:", "Guarantee:",
"Invariant:", "Contract:", "Promise:", "Assumption:"
```

**Medium signals:**
```
"TODO:", "FIXME:", "HACK:", "NOTE:", "WARNING:",
"IMPORTANT:", "DECISION:", "RATIONALE:", "TRADEOFF:"
```

**Docstring triggers:**
```python
# Python: first line of any docstring
"""This function ensures that..."""

# Also capture Args/Returns/Raises as sub-intentions
```

#### 4.3.2 Structural Triggers (Implicit Intentions)

These require parsing, not just text matching:

| Structure | Implied Intention | How to Detect |
|-----------|------------------|---------------|
| Function name starts with `ensure_`, `validate_`, `prevent_`, `check_`, `require_` | Enforcement intention | Regex on function defs |
| Gate/guard clauses | Access control intention | `if not ...: raise/return` at function top |
| Error handling patterns | Resilience intention | `try/except` with specific exception types |
| Abstract base classes | Interface contract intention | Classes with `raise NotImplementedError` |
| Config files with defaults | Default behavior intention | Key-value pairs with comments |
| File/directory organization | Separation of concerns intention | Directory names and `__init__.py` contents |
| Import structure | Dependency intention | What imports what |
| Constants/enums at module top | Constraint intention | ALL_CAPS variables |

#### 4.3.3 Document Triggers (Narrative Intentions)

For `.md` and `.txt` files:

| Trigger | What to Extract |
|---------|----------------|
| H1/H2 headers | Section as high-level intention |
| Bullet lists under "Requirements", "Goals", "Constraints", "Principles" | Each bullet as separate intention |
| Tables with "Status", "Purpose", "Description" columns | Each row as intention |
| Blockquotes | Often contain principles or mottos |
| Mermaid/code blocks with comments | Architecture intentions |
| YAML frontmatter | Metadata intentions (tags, purpose, routing) |

### 4.4 Scanner Output Format

Each raw find is a single JSONL line:

```json
{
  "scan_id": "scan-2026-02-03-143022",
  "source_file": "runtime/server.py",
  "line_start": 348,
  "line_end": 370,
  "trigger_type": "keyword",
  "trigger_match": "gate check",
  "raw_text": "Checks allow_q33n_git and pre_sprint_review gates before permitting git commit",
  "context_before": "2 lines above for context",
  "context_after": "2 lines below for context",
  "language": "python",
  "confidence": 0.85
}
```

### 4.5 Scanner Configuration

```yaml
# intention_scan_config.yaml
scan_roots:
  - path: "."
    label: "main_codebase"
  - path: "../docs"
    label: "documentation"

exclude_patterns:
  - "node_modules/**"
  - "__pycache__/**"
  - ".git/**"
  - "*.pyc"

max_file_size_kb: 100
context_lines: 2
min_confidence: 0.3
```

---

## 5. Classifier Specification

### 5.1 Intention Categories

Each raw find is classified into exactly one primary category and zero or more secondary tags.

| Category | Code | Description | Example |
|----------|------|-------------|---------|
| **Use Case** | `UC` | "The system should do X for user Y" | "Operator can launch a CLI bee from the UI" |
| **Constraint** | `CON` | "The system must/must not do X" | "Never commit without gate approval" |
| **Architectural Decision** | `AD` | "We chose X because of Y" | "File-based storage over database for simplicity" |
| **Pattern** | `PAT` | "This is the standard way to solve X" | "Claim-based task assignment prevents race conditions" |
| **Anti-Pattern** | `AP` | "Avoid doing X because Y" | "Don't use massive instruction docs, use Golden Rules" |
| **Guiding Principle** | `GP` | "High-level law governing behavior" | "Human sovereignty over all agent actions" |
| **Interface Contract** | `IC` | "Module X promises Y to consumers" | "POST /api/tasks returns task ID and route decision" |
| **Quality Attribute** | `QA` | "The system should be X (fast, safe, etc.)" | "All actions logged for auditability" |
| **Operational Rule** | `OR` | "In production, do X" | "Minder pings every 600 seconds" |
| **Temporal** | `TMP` | "At phase X, do Y / By date Z, achieve W" | "Phase 2 adds DES engine" |

### 5.2 Confidence Scoring

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.9 - 1.0 | Explicit, unambiguous intention | Auto-accept |
| 0.7 - 0.89 | Strong signal, clear meaning | Auto-accept, flag for review |
| 0.5 - 0.69 | Probable intention, some ambiguity | Escalate to Tier 2 or 3 |
| 0.3 - 0.49 | Weak signal, may be noise | Escalate to Tier 3 or discard |
| < 0.3 | Likely noise | Discard |

### 5.3 Three-Tier Classification

Classification runs through escalating tiers. Most finds resolve at Tier 1. The expensive tiers only fire when needed.

```
Raw Find ──▶ Tier 1 (Heuristic) ──▶ [confidence ≥ 0.7?] ──▶ ACCEPT
                    │
                    ▼ [confidence 0.5 - 0.69]
             Tier 2 (Embedding) ──▶ [confidence ≥ 0.7?] ──▶ ACCEPT
                    │
                    ▼ [confidence < 0.7 OR flagged as high-importance]
             Tier 3 (LLM) ──▶ ACCEPT / REJECT / REWRITE
```

#### Tier 1 — Heuristic (Free, Instant)

Keyword matching and structural pattern detection as defined in Section 4.3. Handles ~60-70% of finds. No API calls.

#### Tier 2 — Embedding Similarity (Cheap, Fast)

For ambiguous finds, embed the raw text and compare cosine similarity against **category exemplars** — a curated set of 5-10 gold-standard intentions per category.

```yaml
# exemplars.yaml
CON:
  - "No agent may act without human consent"
  - "Gate flags must be checked before git operations"
  - "Tasks cannot bypass routing"
GP:
  - "Human sovereignty over all agent actions"
  - "Coordination shall never outrun conscience"
  - "Diversity of reasoning paths is mandated"
```

Assign the category of the nearest exemplar if similarity > 0.7. Uses Voyage — cost is negligible (one embedding per find, one-time exemplar embedding).

#### Tier 3 — LLM Escalation (Powerful, Reserved)

For finds that remain ambiguous after Tier 2, or that are flagged as high-importance (from Federalist Papers, architecture docs, or spec files), escalate to an LLM for nuanced understanding.

**When to escalate:**
- Confidence still < 0.7 after Tier 2
- Source file is a governance/philosophy document (`.md` in federalist/, architecture docs)
- Find contains complex conditional logic or nuanced tradeoffs
- Find spans multiple paragraphs (narrative intentions)
- Contradiction detected between two finds (LLM adjudicates)

**LLM provider selection:**

| Provider | Model | Use When | Cost |
|----------|-------|----------|------|
| Anthropic | `claude-sonnet-4-5-20250929` | Nuance, philosophy, governance docs, contradiction resolution | ~$3/1M input |
| OpenAI | `codex` / `gpt-4o` | Code-heavy intentions, implementation contracts | ~$2.50/1M input |

Provider is configurable via the same adapter pattern as embeddings:

```yaml
# intention_scan_config.yaml
llm_classifier:
  provider: "anthropic"
  model: "claude-sonnet-4-5-20250929"
  api_key_env: "ANTHROPIC_API_KEY"
  max_escalations_per_scan: 100        # budget guard
  temperature: 0.2                      # low creativity, high precision
```

**LLM prompt template:**

```
You are classifying intentions extracted from a codebase and its documentation.

An "intention" is a captured thought representing a goal, constraint, principle, or architectural decision.

Given the following text extracted from {source_file} (lines {line_start}-{line_end}):

---
{raw_text}
---

Context before: {context_before}
Context after: {context_after}

Classify this into exactly ONE of these categories:
- UC (Use Case): "The system should do X for user Y"
- CON (Constraint): "The system must/must not do X"
- AD (Architectural Decision): "We chose X because Y"
- PAT (Pattern): "Standard way to solve X"
- AP (Anti-Pattern): "Avoid X because Y"
- GP (Guiding Principle): "High-level law"
- IC (Interface Contract): "Module X promises Y"
- QA (Quality Attribute): "System should be X"
- OR (Operational Rule): "In production, do X"
- TMP (Temporal): "At phase X, do Y"
- NOISE: Not an intention, discard

Respond with JSON only:
{
  "category": "...",
  "confidence": 0.0-1.0,
  "refined_text": "rewrite the intention as a clean, standalone statement",
  "reasoning": "one sentence explaining your classification",
  "gravitas": "low|medium|high|foundational"
}
```

**The `gravitas` field** is unique to Tier 3. It captures the weight/importance of the intention — something heuristics and embeddings can't assess. A `foundational` intention (e.g., "Human sovereignty over all agent actions") carries different architectural weight than a `low` intention (e.g., "Default PTY buffer is 4000 chars").

**The `refined_text` field** lets the LLM rewrite ambiguous or poorly-phrased intentions into clean, standalone statements. This is the "higher level intention documentation" — the LLM doesn't just classify, it *understands and restates*.

### 5.4 Classification Budget

| Tier | Cost per Find | Expected Volume | Total Cost |
|------|--------------|----------------|------------|
| Tier 1 | Free | ~1,400 finds (70%) | $0 |
| Tier 2 | ~$0.000003 | ~400 finds (20%) | $0.001 |
| Tier 3 | ~$0.002 | ~200 finds (10%) | $0.40 |
| **Total** | | **~2,000 finds** | **< $1.00** |

Budget guard: `max_escalations_per_scan` prevents runaway LLM costs. If exceeded, remaining ambiguous finds queue for human review.

### 5.5 Deduplication

Two finds are duplicates if:
- Same `raw_text` (exact match after whitespace normalization)
- OR cosine similarity > 0.92 on embedded text
- AND same `category`

Keep the instance with highest confidence. Record all source locations.

### 5.6 Classifier Output Format

```json
{
  "intention_id": "INT-0042",
  "text": "All gate flags must be checked before permitting git operations",
  "category": "CON",
  "secondary_tags": ["security", "git", "gates"],
  "confidence": 0.92,
  "classification_tier": 1,
  "gravitas": "high",
  "sources": [
    {"file": "runtime/server.py", "lines": [348, 370]},
    {"file": "docs/ideation-notes.md", "lines": [112, 118]}
  ],
  "related_kb_entity": "RULE-gate-enforcement",
  "created_at": "2026-02-03T14:30:22Z",
  "status": "accepted"
}
```

**New fields vs. original:**
- `classification_tier` — which tier resolved this (1, 2, or 3)
- `gravitas` — importance weight (only set by Tier 3; Tiers 1-2 default to `null`)

---

## 6. Embedding Specification

### 6.1 Embedding Strategy

Each intention record gets embedded as a vector for semantic search and clustering.

**What to embed:** Concatenation of:
```
[CATEGORY] text | tags: tag1, tag2 | source: filename
```

Example:
```
[CONSTRAINT] All gate flags must be checked before permitting git operations | tags: security, git, gates | source: server.py
```

This format gives the embedding model category context, the core meaning, domain tags, and source locality.

### 6.2 Model Selection

**Primary model:** Voyage AI (existing capability in place).

| Option | Dimensions | Quality | Cost | Role |
|--------|-----------|---------|------|------|
| `voyage-code-3` (Voyage AI) | 1024 | Best for code + docs | $0.06/1M tokens | **PRIMARY** — all production embedding |
| `voyage-3` (Voyage AI) | 1024 | Best general | $0.06/1M tokens | **FALLBACK** — if code-3 underperforms on philosophy docs |
| `all-MiniLM-L6-v2` (local) | 384 | Adequate | Free | **PARALLEL TRIAL** — separate repo, benchmarking only |

**Cost estimate:** ~2,000 intentions × 50 avg tokens = 100K tokens = ~$0.006. Negligible.

**MiniLM parallel trial:** Run in a separate repo to benchmark against Voyage on the same query set. Keep the comparison data. Don't block production on it.

### 6.3 Model Adapter Pattern

All embedding calls go through an adapter so the model is swappable via config, not code changes.

```python
# embedder.py

class EmbeddingAdapter:
    """Swappable embedding backend."""

    def __init__(self, provider, model_name, api_key=None):
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key

    def embed(self, texts):
        """Embed a list of strings. Returns list of numpy arrays."""
        if self.provider == "voyage":
            return self._voyage_embed(texts)
        elif self.provider == "local":
            return self._local_embed(texts)
        elif self.provider == "openai":
            return self._openai_embed(texts)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _voyage_embed(self, texts):
        import voyageai
        client = voyageai.Client(api_key=self.api_key)
        result = client.embed(texts, model=self.model_name)
        return [np.array(e) for e in result.embeddings]

    def _local_embed(self, texts):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(self.model_name)
        return [np.array(e) for e in model.encode(texts)]

    def _openai_embed(self, texts):
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        result = client.embeddings.create(input=texts, model=self.model_name)
        return [np.array(e.embedding) for e in result.data]
```

**Configuration:**

```yaml
# intention_scan_config.yaml
embedding:
  provider: "voyage"
  model: "voyage-code-3"
  api_key_env: "VOYAGE_API_KEY"     # reads from environment variable
  batch_size: 50                     # Voyage supports batch embedding
```

### 6.4 Vector Storage

SQLite with a simple schema (no exotic vector DB needed at this scale):

```sql
CREATE TABLE intentions (
    intention_id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    category TEXT NOT NULL,
    secondary_tags TEXT,          -- JSON array
    confidence REAL,
    classification_tier INTEGER,  -- 1=heuristic, 2=embedding, 3=LLM
    gravitas TEXT,                -- low|medium|high|foundational (Tier 3 only)
    sources TEXT,                 -- JSON array of {file, lines}
    embedding BLOB,              -- numpy array as bytes
    created_at TEXT,
    status TEXT DEFAULT 'accepted'
);

CREATE TABLE clusters (
    cluster_id TEXT PRIMARY KEY,
    label TEXT,
    intention_ids TEXT,           -- JSON array
    centroid BLOB,
    coherence_score REAL
);

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id TEXT,
    to_id TEXT,
    rel_type TEXT,                -- 'supports', 'contradicts', 'implements', 'orphaned_by'
    similarity REAL,
    FOREIGN KEY (from_id) REFERENCES intentions(intention_id),
    FOREIGN KEY (to_id) REFERENCES intentions(intention_id)
);
```

### 6.5 Similarity Search

Brute-force cosine similarity is fine up to ~10,000 intentions. For a codebase this size, expect 200-2,000 intentions. No need for FAISS or approximate methods.

```python
def search(query_text, top_k=10):
    query_vec = embed(query_text)
    scores = [(iid, cosine_sim(query_vec, vec)) for iid, vec in all_vectors]
    return sorted(scores, key=lambda x: -x[1])[:top_k]
```

---

## 7. Analyzer Specification

The analyzer runs after extraction and embedding to produce actionable insights.

### 7.1 Cluster Analysis

**Method:** Agglomerative clustering with cosine distance, threshold = 0.25.

**Output:** Groups of intentions expressing the same underlying goal.

**Use case:** "12 scattered comments across 8 files all express the same architectural intent" — the cluster reveals the hidden pattern.

**Report format:**
```
CLUSTER: "Human oversight of agent actions" (7 intentions, coherence: 0.89)
  INT-0012: [CON] No agent may act without human consent (server.py:42)
  INT-0034: [GP] Human sovereignty over all decisions (NO-16.md:18)
  INT-0041: [CON] Gate flags block unauthorized commits (server.py:348)
  INT-0055: [AD] Dave retains absolute override (NO-02.md:95)
  INT-0067: [OR] allow_q33n_git defaults to False (server.py:88)
  INT-0072: [UC] Operator can revoke bee authority (ideation.md:45)
  INT-0091: [IC] POST /api/gates requires human action (server.py:340)
```

### 7.2 Contradiction Detection

**Method:** Find pairs where:
- Cosine similarity > 0.7 (related topic)
- BUT category or sentiment conflicts (e.g., one says "always", another says "never" about similar subject)

**Heuristic triggers for contradiction flag:**
- Same subject, opposing verbs (ensure vs. prevent, allow vs. block)
- Same scope, different constraints
- Temporal conflict (Phase 1 says X, Phase 3 says not-X without explicit supersession)

**Output:** Contradiction report with both intentions, similarity score, and conflict description.

### 7.3 Orphan Detection

**Method:** For each intention with category `UC`, `CON`, or `IC`:
- Search the codebase for implementation evidence
- If no code file references the same concepts (low similarity to any code-extracted intention): mark as orphan

**Output:** List of intentions with no apparent implementation.

### 7.4 Ghost Detection

**Method:** For each function/class/endpoint in the codebase:
- Check if any intention record references it (by filename + line range or by semantic match)
- If no intention covers it: mark as ghost

**Output:** List of code elements with no discoverable purpose.

**Note:** Ghosts aren't automatically bad — they may be infrastructure. But they should be documented or removed.

### 7.5 Drift Measurement

**Method:** For intention-implementation pairs:
- Embed the intention text
- Embed the implementation's docstring + comments + function signature
- Measure cosine distance

**Interpretation:**
| Distance | Meaning |
|----------|---------|
| < 0.15 | Tight alignment |
| 0.15 - 0.30 | Acceptable drift |
| 0.30 - 0.50 | Significant drift — review recommended |
| > 0.50 | Major drift — intention and implementation may have diverged |

---

## 8. Query API Specification

### 8.1 Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/intentions` | List all intentions, filterable by category, tag, confidence |
| GET | `/api/intentions/{id}` | Single intention with full detail |
| POST | `/api/intentions/search` | Semantic search: `{"query": "human oversight", "top_k": 10}` |
| GET | `/api/intentions/clusters` | All clusters with member intentions |
| GET | `/api/intentions/contradictions` | All detected contradictions |
| GET | `/api/intentions/orphans` | Intentions with no implementation |
| GET | `/api/intentions/ghosts` | Code with no intention |
| GET | `/api/intentions/drift` | Drift scores for intention-implementation pairs |
| POST | `/api/intentions/scan` | Trigger a new scan (async) |
| GET | `/api/intentions/stats` | Summary counts by category, confidence distribution |

### 8.2 Search Request/Response

**Request:**
```json
{
  "query": "how do we prevent unauthorized commits",
  "top_k": 5,
  "min_confidence": 0.5,
  "categories": ["CON", "GP", "OR"]
}
```

**Response:**
```json
{
  "results": [
    {
      "intention_id": "INT-0041",
      "text": "All gate flags must be checked before permitting git operations",
      "category": "CON",
      "similarity": 0.94,
      "sources": [{"file": "runtime/server.py", "lines": [348, 370]}]
    }
  ],
  "query_embedding_time_ms": 12,
  "search_time_ms": 3
}
```

---

## 9. KB Integration

### 9.1 Mapping Intentions to KB Entities

| Intention Category | KB Entity Type | Auto-create? |
|-------------------|---------------|-------------|
| Guiding Principle (`GP`) | `RULE` | Yes — with `load_mode: always` |
| Constraint (`CON`) | `RULE` | Yes — with `load_mode: situation` |
| Pattern (`PAT`) | `PATTERN` | Yes |
| Anti-Pattern (`AP`) | `RULE` | Yes — phrased as prohibition |
| Interface Contract (`IC`) | `SNIPPET` | Yes |
| Operational Rule (`OR`) | `PLAYBOOK` | Suggest, human confirms |
| Use Case (`UC`) | — | No auto-create (planning artifact, not KB) |
| Architectural Decision (`AD`) | `REFERENCE` | Yes |

### 9.2 Auto-Population Flow

```
Scan ──▶ Classify ──▶ [confidence > 0.8?] ──▶ Create KB entity draft
                              │
                              ▼ [confidence 0.5-0.8]
                        Queue for human review
```

KB entities created by the Intention Engine get tagged `source: intention-engine` and `auto_generated: true` for traceability.

---

## 10. CLI Interface

Primary interface for running scans and queries from the terminal.

```bash
# Run a full scan
python -m intention_engine scan --config intention_scan_config.yaml

# Search intentions
python -m intention_engine search "human oversight"

# Show clusters
python -m intention_engine clusters

# Show contradictions
python -m intention_engine contradictions

# Show orphans (intentions without implementation)
python -m intention_engine orphans

# Show ghosts (code without intention)
python -m intention_engine ghosts

# Drift report
python -m intention_engine drift

# Export full intention graph
python -m intention_engine export --format json --output intentions_graph.json

# Stats summary
python -m intention_engine stats
```

---

## 11. Implementation Plan (for Bees)

### 11.1 Phase A — Scanner (TASK: IE-001)

**Effort:** 4-6 hours
**Input:** File tree + config YAML
**Output:** `raw_finds.jsonl`
**Dependencies:** None
**Test:** Run against `deia_raqcoon/` directory, verify finds > 50 raw candidates

### 11.2 Phase B — Classifier (TASK: IE-002)

**Effort:** 6-8 hours
**Input:** `raw_finds.jsonl`
**Output:** `intentions.json`
**Dependencies:** IE-001, Voyage API key (for Tier 2), Anthropic API key (for Tier 3)
**Subtasks:**
- Tier 1 heuristic classifier (keyword/pattern matching)
- Tier 2 embedding classifier (Voyage similarity to exemplars)
- Tier 3 LLM classifier (Claude/Codex for ambiguous + high-importance finds)
- Orchestrator (routes finds through tiers based on confidence thresholds)
- Deduplication pass
**Test:** Each record has category, confidence, tier. No duplicates with similarity > 0.92. Tier 3 produces gravitas scores for escalated finds. Total LLM calls < `max_escalations_per_scan`.

### 11.3 Phase C — Embedding Service (TASK: IE-003)

**Effort:** 3-4 hours
**Input:** `intentions.json`
**Output:** `intentions.db` (SQLite with vectors)
**Dependencies:** IE-002
**Test:** Semantic search for "gate enforcement" returns gate-related intentions in top 3 results.

### 11.4 Phase D — Analyzer (TASK: IE-004)

**Effort:** 6-8 hours
**Input:** `intentions.db`
**Output:** Cluster, contradiction, orphan, ghost, drift reports
**Dependencies:** IE-003
**Test:** At least 3 clusters identified. At least 1 orphan or ghost found.

### 11.5 Phase E — Query API (TASK: IE-005)

**Effort:** 4-6 hours
**Input:** `intentions.db`
**Output:** FastAPI endpoints
**Dependencies:** IE-003
**Test:** All endpoints return valid JSON. Search returns ranked results.

### 11.6 Phase F — KB Integration (TASK: IE-006)

**Effort:** 2-3 hours
**Input:** `intentions.json` + existing `kb/store.py`
**Output:** KB entity drafts
**Dependencies:** IE-002 + existing KB system
**Test:** High-confidence intentions auto-create KB entity drafts.

**Total estimated effort:** 26-36 hours

---

## 12. File Structure

```
intention_engine/
├── __init__.py
├── scanner.py           # IE-001: File walking + extraction
├── classifier.py        # IE-002: Tier 1 heuristic + orchestration of Tiers 2-3
├── llm_classifier.py    # IE-002: Tier 3 LLM escalation (Claude/Codex)
├── exemplars.yaml       # IE-002: Tier 2 category exemplar texts
├── embedder.py           # IE-003: EmbeddingAdapter (Voyage primary, swappable)
├── analyzer.py           # IE-004: Clusters, contradictions, orphans, ghosts, drift
├── query_api.py          # IE-005: FastAPI search endpoints
├── kb_bridge.py          # IE-006: KB entity auto-population
├── models.py             # Shared data models (IntentionRecord, RawFind, etc.)
├── config.py             # Config loading
├── __main__.py           # CLI entry point
└── tests/
    ├── test_scanner.py
    ├── test_classifier.py
    ├── test_embedder.py
    ├── test_llm_classifier.py
    └── test_analyzer.py
```

---

## 13. Dependencies

```
# requirements.txt — core
voyageai>=0.3.0                  # Primary embedding model
numpy>=1.24.0                    # Vector operations
scikit-learn>=1.3.0              # Clustering, cosine similarity
pyyaml>=6.0                      # Config loading

# requirements-api.txt — optional, only for IE-005
fastapi>=0.100.0                 # Query API
uvicorn>=0.23.0                  # API server

# requirements-llm.txt — optional, only for Tier 3 classification
anthropic>=0.40.0                # Claude for LLM escalation
openai>=1.0.0                    # Codex/GPT for LLM escalation (alternative)

# requirements-trial.txt — optional, only for MiniLM parallel benchmarking
sentence-transformers>=2.2.0     # Local embedding model (separate repo trial)
```

**Required API keys (via environment variables):**
- `VOYAGE_API_KEY` — required for all production embedding
- `ANTHROPIC_API_KEY` — required only if Tier 3 LLM classification enabled
- `OPENAI_API_KEY` — required only if using OpenAI as Tier 3 provider

---

## 14. Success Criteria

| Criterion | Measure |
|-----------|---------|
| Extraction coverage | > 80% of manually identified intentions found by scanner |
| Classification accuracy | > 75% of auto-classified intentions match human judgment |
| Search quality | Top-3 results for 10 test queries contain correct intention |
| Cluster coherence | Average intra-cluster similarity > 0.75 |
| Actionable insights | At least 5 orphans or ghosts identified that lead to real refactoring decisions |
| KB population | At least 10 new KB entities auto-drafted from scan |

---

## 15. Future Extensions (Out of Scope for MVP)

- **Watch mode:** Re-scan on file change, update embeddings incrementally
- **Cross-repo scanning:** Scan multiple repos, unify intention graph
- **Intention coverage badge:** "87% of code has documented intention" in README
- **IDE integration:** VS Code extension showing intention coverage per file
- **Diff-aware scanning:** On PR/commit, show which intentions are affected by the change
- **Gravitas-weighted refactoring:** Prioritize refactoring based on gravitas scores — foundational intentions get addressed first
- **Conversation mining:** Extract intentions from chat histories and conversation transcripts (not just code/docs)

---

*This spec is the intention of the Intention Engine.*
*It should be the first thing the engine scans when pointed at itself.*
