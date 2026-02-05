# PROCESS-0005: Intention Engine Refactoring Methodology

**Version:** 1.0
**Status:** Active
**Created:** 2026-02-04
**Author:** daaaave-atx
**Participants:** Claude (Anthropic), GPT-5 (OpenAI Codex), Claude Code, Gemini CLI

---

## 1. Purpose

This process defines the **Intention Engine** methodology for refactoring codebases. Rather than asking "does the code still work?" we ask: **"does the code still _mean_ what it meant?"**

The methodology combines semantic embeddings, BPMN process modeling, and multi-LLM review to validate that architectural intent survives structural change.

---

## 2. When to Use

Apply this process when:

- 2.1. The intent has drifted from the implementation over time.
- 2.2. Specs are scattered across code, docs, conversations, and tribal knowledge.
- 2.3. Multiple contributors (human or AI) have added code without a unified architectural vision.
- 2.4. The codebase is too large for any single reviewer to hold in their head.
- 2.5. Massive instruction documents are being ignored by AI agents (indicating the codebase has outgrown its documentation).

---

## 3. Core Insight

Traditional refactoring works **backward** from what the code does. Intention-first refactoring works **forward** from what the code was meant to do.

The process treats intention extraction as the first step: extract the embedded intentions, create semantic embeddings of them, and then use the intention graph as the authoritative specification for rebuilding — rather than using the existing code as the source of truth.

---

## 4. Procedure

### 4.1 Choose Your Approach

Run one or both approaches in parallel:

#### Method A — Fresh Start (Bottom-Up)

1. Create a clean new directory structure.
2. Run the Intention Engine scan across the entire existing repo (all code, docs, markdown, JSON schemas, HTML mockups).
3. Extract intentions at three layers:
   - **Explicit** — comments, docstrings, markdown headers, naming conventions (`ensure_`, `prevent_`, `validate_`)
   - **Structural** — architectural choices as implicit intentions (separation of concerns, file organization, import graphs)
   - **Negative space** — what was conspicuously absent (anti-patterns, things deliberately not built)
4. Embed all extracted intentions using Voyage AI, creating a unified semantic space.
5. Cluster and deduplicate intentions, reducing raw count to canonical set.
6. Rebuild the codebase into the fresh directory using the intention graph as the spec.

#### Method B — Top-Down (Intentions-First)

1. Start with just the intentions and process design — no code.
2. Pull specs from multiple sources: the repo itself, plus documents from Claude conversation history and ChatGPT conversation history where specs had been discussed and refined.
3. Construct the "spec as built" and "spec as desired" through a combination of actual construction artifacts, specification documents, and conversational dialog history.
4. Use BPMN process modeling to map the intended process flows.
5. Build the new version from the top-down spec, with the intention graph as the authoritative reference.

### 4.2 Semantic Embedding Pipeline (IE-001 through IE-007)

| Phase | Name | Action |
|-------|------|--------|
| IE-001 | **Scan** | Walk every `.py`, `.md`, `.json`, `.html` file. Extract intentions from comments, docstrings, headers, naming patterns, structural choices. |
| IE-002 | **Categorize** | Classify by type: RULE, PATTERN, SNIPPET, PLAYBOOK, anti-pattern, guiding principle. |
| IE-003 | **Embed** | Generate Voyage AI embeddings (voyage-3-lite, 512 dimensions). |
| IE-004 | **Cluster** | Group semantically similar intentions. Identify redundancy, contradictions, orphans, ghosts. |
| IE-005 | **Deduplicate** | Consolidate clusters into canonical intention statements. |
| IE-006 | **Graph** | Produce the intention graph — a queryable semantic map. |
| IE-007 | **Validate** | Cross-reference intention graph against rebuilt code. |

### 4.3 BPMN Process Flow Modeling

1. Map the **intended workflow**: task creation → routing → KB injection → execution → response capture → archival.
2. Map the **actual workflow** as observed in the existing code.
3. Compare intended vs. actual to identify process gaps.
4. Use BPMN as complementary validation — semantic embeddings catch meaning drift; BPMN catches flow drift.

### 4.4 Multi-LLM Review

Engage multiple AI species for review:

| LLM | Role |
|-----|------|
| Claude Code | Implementation work |
| OpenAI Codex | Independent review and gap identification |
| Gemini CLI | Initial spec extraction, results review |

Each LLM brings different cognitive strengths — different pattern recognition, different blind spots. This multi-vendor diversity is a core DEIA principle (Federalist Papers No. 14).

---

## 5. Post-Build Validation (Critical Step)

After the new build is complete, run the Intention Engine and BPMN analysis **again** on the new version, then compare old-to-new:

### 5.1 Semantic Intention Comparison

1. Extract intentions from the new codebase.
2. Generate Voyage AI embeddings for new intentions.
3. Compute cosine similarity between old and new intention embeddings.
4. Score each intention pair:
   - **PRESERVED**: ≥0.85 similarity
   - **PARTIAL**: 0.55–0.84 similarity
   - **MISSING**: <0.55 similarity
5. Manual review all MISSING items — confirm whether noise or genuine gaps.

### 5.2 BPMN Process Flow Comparison

1. Generate BPMN diagrams for new build's process flows.
2. Compare old BPMN flows to new BPMN flows.
3. Identify process steps present in old design but missing from new build.

### 5.3 Combined Gap Resolution

1. Both methods independently identify missing elements the other missed.
2. Union of both gap analyses produces comprehensive list.
3. Triage gaps:
   - Genuine omissions → fix
   - Intentional simplifications → document
   - Obsolete features → formally deprecate

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| Semantic coverage of core principles | 100% |
| Theme cluster reduction | ≥5:1 |
| Low-match items (after triage) | All confirmed non-essential |
| Gaps found by semantic analysis | Documented and resolved |
| Gaps found by BPMN analysis | Documented and resolved |

---

## 7. Key Learnings (Reference)

1. **"Does it still mean what it meant?" is better than "does it still work?"** — Functional correctness is table stakes. Semantic preservation ensures you didn't lobotomize the architecture's DNA.

2. **Two validation methods are better than one.** — Semantic embeddings catch meaning drift. BPMN catches flow drift. Each finds gaps the other misses.

3. **Multi-LLM review catches more than single-vendor review.** — Different models have different blind spots.

4. **Intention extraction works as a novel refactoring method.** — The intention graph becomes your spec. The old code becomes reference material, not source of truth.

5. **Massive redundancy is the norm in evolved codebases.** — 9:1 theme compression is typical. Consolidation is healthier for both humans and AI agents.

6. **Anti-patterns are intentions too.** — Capturing what the code deliberately avoids is as important as what it does. Negative space is signal.

---

## 8. Tools

- **Voyage AI**: Semantic embeddings (voyage-3-lite model)
- **Intention Engine**: `intention_engine/` in deiasolutions-3-chrysalis
- **Code Flow Analyzer**: `intention_engine/code_flow_analyzer.py`
- **deia-viz**: Unified visualization library for ArchiMate/BPMN/Mermaid export

---

## 9. Related Processes

- PROCESS-0001: Always Check and Submit
- PROCESS-0002: Task Completion and Archival
- PROCESS-0003: Process Discovery and Contribution
- PROCESS-0004: Activity Logging

---

## 10. Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-04 | 1.0 | Initial process definition from working proof of concept |

---

*Methodology: Intention Engine + BPMN + Multi-LLM Review*
*Status: Validated on deiasolutions repo refactor*
