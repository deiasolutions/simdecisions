# Python Hive Vision

**From:** Q33N (Dave)
**Date:** 2026-02-04
**Type:** Raw architectural input
**Status:** CAPTURE — needs refinement into ADR

---

## The Insight

> "I envision a hive as a jupyter notebook with .md files and .py files, cells as an organizational unit... I want a Python hive. A hive that specializes in Python code."

---

## Core Concept: Python Hive

A **specialized hive** that:

1. **Organizational unit = cells** (like Jupyter)
   - `.md` cells — specs, docs, context
   - `.py` cells — executable code
   - Cells have order, dependencies, outputs

2. **Domain knowledge of Python libraries**
   - Knows when to use a library vs. call an LLM
   - Example: "Parse this JSON" → `json.loads()`, not GPT
   - Example: "Summarize this text" → LLM, not regex
   - Decision engine: **code-or-LLM oracle**

3. **Specialization**
   - Not a general-purpose hive
   - Deep knowledge of Python ecosystem
   - Knows pandas, numpy, requests, etc.
   - Can generate, test, and validate Python code

---

## Code-or-LLM Decision Engine

Need a component with domain knowledge to answer:

> "For this task, should we write Python code or call an LLM?"

### Factors to Consider

| Factor | Favors Code | Favors LLM |
|--------|-------------|------------|
| Determinism needed | ✓ | |
| Speed critical | ✓ | |
| Cost sensitive | ✓ | |
| Well-defined algorithm exists | ✓ | |
| Fuzzy/ambiguous input | | ✓ |
| Natural language understanding | | ✓ |
| Creative generation | | ✓ |
| No library exists | | ✓ |

### Example Decisions

| Task | Decision | Reason |
|------|----------|--------|
| Parse CSV file | CODE | `pandas.read_csv()` |
| Calculate statistics | CODE | `numpy`, `scipy` |
| Extract dates from text | CODE | `dateutil.parser` |
| Summarize document | LLM | Requires understanding |
| Generate test cases | LLM | Creative, edge-case thinking |
| HTTP request | CODE | `requests` library |
| Classify sentiment | HYBRID | `transformers` or LLM API |
| Validate JSON schema | CODE | `jsonschema` library |

---

## Hive Structure (Draft)

```
python-hive/
├── cells/
│   ├── 001-context.md          # What we're trying to do
│   ├── 002-imports.py          # Standard imports
│   ├── 003-data-load.py        # Load data
│   ├── 004-analysis-plan.md    # What analysis to do
│   ├── 005-analysis.py         # The analysis code
│   ├── 006-results.md          # Interpretation
│   └── ...
├── outputs/                     # Cell outputs (cached)
├── hive.json                    # Cell order, dependencies, metadata
└── README.md
```

---

## Questions to Resolve

1. **Cell execution model** — Sequential? DAG? On-demand?
2. **State management** — How do cells share state? (like Jupyter kernel)
3. **Versioning** — Git-friendly cell format?
4. **Library knowledge base** — How to encode "use pandas for this"?
5. **Hybrid cells** — Can a cell be both code and LLM prompt?

---

## Relationship to SimDecisions

This could be:
- A **specialized bee type** — "Python Bee" that lives in Python Hives
- A **domain adapter** — Pluggable knowledge module
- A **decision oracle** — Consulted by any bee for code-vs-LLM decisions

---

## Next Steps

1. Refine into ADR-005 or similar
2. Define the code-or-LLM decision interface
3. Prototype cell execution model
4. Build library knowledge base (start with top 50 Python packages)

---

---

## UPDATE: PyBots (RAGGIT-based)

> "In the organism we're creating pybots - written using the RAGGIT spec! These ones will be dual enacting: 1) a Python executable and CLI run instructions, and 2) an LLM simulator that will either simulate the results of what the..."

### Dual-Enacting PyBot Concept

```
┌─────────────────────────────────────────────────────┐
│  PyBot (RAGGIT-spec)                                │
│                                                     │
│  ┌─────────────────┐    ┌─────────────────┐        │
│  │ MODE 1: Execute │    │ MODE 2: Simulate│        │
│  │ Python + CLI    │ OR │ LLM predicts    │        │
│  │ (deterministic) │    │ (flexible)      │        │
│  └────────┬────────┘    └────────┬────────┘        │
│           │                      │                  │
│           └──────────┬───────────┘                  │
│                      ▼                              │
│              ┌──────────────┐                       │
│              │ Same Output  │                       │
│              │ Contract     │                       │
│              └──────────────┘                       │
└─────────────────────────────────────────────────────┘
```

### Why Dual-Enacting?

| Scenario | Use Execute | Use Simulate |
|----------|-------------|--------------|
| Code exists, deterministic | ✓ | |
| Prototyping, code not written yet | | ✓ |
| Code failed, need fallback | | ✓ |
| Testing: compare real vs predicted | ✓ | ✓ |
| Cost optimization | ✓ | |
| Fuzzy input, needs understanding | | ✓ |

### Q33N — finish the thought:

> "...an LLM simulator that will either simulate the results of what the ___?"

---

*Raw capture from Q33N. Needs bee refinement.*
