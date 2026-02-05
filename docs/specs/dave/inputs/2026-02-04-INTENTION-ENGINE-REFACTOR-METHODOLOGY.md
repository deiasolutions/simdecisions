# Intention Engine Refactoring Methodology
## Process Reference — deiasolutions Repo Refactor, February 2026

**Date:** 2026-02-04  
**Author:** daaaave-atx  
**Participants:** Claude (Anthropic), GPT-5 (OpenAI Codex), Claude Code, Gemini CLI  
**Status:** Working proof of concept  

---

## 1. Overview

In early February 2026, the deiasolutions repository underwent a major refactoring effort using a novel methodology we're calling the **Intention Engine** approach. Rather than the traditional refactoring question — "does the code still work?" — we asked a different one: **"does the code still _mean_ what it meant?"**

The methodology combines semantic embeddings, BPMN process modeling, and multi-LLM review to validate that architectural intent survives structural change. This document captures the full process for future reference and replication.

---

## 2. The Problem

The deiasolutions codebase had accumulated significant drift between intent and implementation:

2.1. Specs, governance philosophy (Federalist Papers), code, and conversation history each contained pieces of the project's true intentions — but no single artifact held all of them.

2.2. Massive instruction documents (5000+ lines) were being ignored by AI agents, indicating the codebase had outgrown its own documentation.

2.3. Redundancy was rampant — the same principle expressed 9 different ways across 8 files, with a 9:1 theme cluster ratio (243 raw themes → 27 canonical themes).

2.4. Code existed that nobody could explain the purpose of (ghosts), and intentions existed with no corresponding implementation (orphans).

---

## 3. Core Insight

Traditional refactoring works **backward** from what the code does. Intention-first refactoring works **forward** from what the code was meant to do.

The process treats intention extraction as the first step: extract the embedded intentions, create semantic embeddings of them, and then use the intention graph as the authoritative specification for rebuilding — rather than using the existing code as the source of truth.

---

## 4. Two Parallel Refactoring Approaches

We ran two refactors simultaneously, each attacking from a different direction:

### 4.1 Method A — Fresh Start (Bottom-Up)

4.1.1. Created a clean new directory structure.

4.1.2. Ran the Intention Engine scan across the entire existing repo (all code, docs, markdown, JSON schemas, HTML mockups).

4.1.3. Extracted intentions at three layers:
   - **Explicit** — comments, docstrings, markdown headers, naming conventions (`ensure_`, `prevent_`, `validate_`)
   - **Structural** — architectural choices as implicit intentions (separation of concerns, file organization, import graphs)
   - **Negative space** — what was conspicuously absent (anti-patterns, things deliberately not built)

4.1.4. Embedded all extracted intentions using Voyage AI, creating a unified semantic space.

4.1.5. Clustered and deduplicated intentions, reducing raw count to canonical set.

4.1.6. Rebuilt the codebase into the fresh directory using the intention graph as the spec.

### 4.2 Method B — Top-Down (Intentions-First)

4.2.1. Started with just the intentions and process design — no code.

4.2.2. Pulled specs from multiple sources: the repo itself, plus documents from Claude conversation history and ChatGPT conversation history where specs had been discussed and refined. (Note: the cross-platform document harvesting process was clunky and needs improvement.)

4.2.3. Constructed the "spec as built" and "spec as desired" through a combination of actual construction artifacts, specification documents, and conversational dialog history.

4.2.4. Used BPMN process modeling to map the intended process flows.

4.2.5. Built the new version from the top-down spec, with the intention graph as the authoritative reference.

---

## 5. Semantic Embedding Pipeline

The Intention Engine pipeline (IE-001 through IE-007) worked as follows:

5.1. **Scan** — Walk every `.py`, `.md`, `.json`, `.html` file in the repo. Extract intentions from comments, docstrings, headers, naming patterns, and structural choices.

5.2. **Categorize** — Classify each intention by type (maps to existing KB entity taxonomy: RULE, PATTERN, SNIPPET, PLAYBOOK, anti-pattern, guiding principle).

5.3. **Embed** — Generate Voyage AI embeddings for each intention, creating vectors in a unified semantic space.

5.4. **Cluster** — Group semantically similar intentions. Identify redundancy (same principle expressed multiple ways), contradictions (intentions pointing in opposite directions), orphans (intentions with no implementation), and ghosts (code with no discoverable intent).

5.5. **Deduplicate** — Consolidate clusters into canonical intention statements. Achieved 9:1 compression on themes (243 → 27) and 12.5:1 overall compression while preserving 100% semantic coverage of core principles.

5.6. **Graph** — Produce the intention graph — a queryable semantic map of everything the codebase was meant to do.

5.7. **Validate** — Cross-reference the intention graph against the rebuilt code to verify alignment.

---

## 6. BPMN Process Flow Modeling

In parallel with semantic analysis, we modeled the system's process flows using BPMN (Business Process Model and Notation):

6.1. Mapped the intended workflow: task creation → routing → KB injection → execution → response capture → archival.

6.2. Mapped the actual workflow as observed in the existing code.

6.3. Compared intended vs. actual to identify process gaps (e.g., router existed but was never called; KB injection accepted entity IDs but never resolved content).

6.4. Used BPMN as a complementary validation layer — semantic embeddings catch meaning drift; BPMN catches flow drift. Different failure modes, both necessary.

---

## 7. Multi-LLM Review

A critical element of the process was getting feedback from multiple AI species:

7.1. **Claude Code** — Participated in the actual refactoring implementation work.

7.2. **OpenAI Codex** — Provided independent review and gap identification.

7.3. **Gemini CLI** — Originated the initial intention extraction spec via Gemini Live; participated in review of results.

7.4. Each LLM brought different cognitive strengths to the review — different pattern recognition, different blind spots. This multi-vendor diversity is a core principle from the Federalist Papers (No. 14) applied to the engineering process itself.

---

## 8. Post-Build Validation (The Key Innovation)

After the new build was complete, we ran the Intention Engine and BPMN analysis **again** on the new version, then compared old-to-new:

### 8.1 Semantic Intention Comparison

8.1.1. Extracted intentions from the new codebase.

8.1.2. Generated Voyage AI embeddings for the new intentions.

8.1.3. Computed cosine similarity between old intention embeddings and new intention embeddings.

8.1.4. Scored each intention pair: PRESERVED (≥0.85 similarity), PARTIAL (0.55–0.84), MISSING (<0.55).

8.1.5. Results: 17% PRESERVED, bulk in PARTIAL range, 17% MISSING — but manual review confirmed all MISSING items were noise (node_modules artifacts, scratch files, historical logs from the original scan).

8.1.6. **Crucially, this comparison surfaced specific gaps** — intentions from the old build that had not been carried forward into the new version. Some were intentionally dropped (anti-patterns); others needed to be added back.

### 8.2 BPMN Process Flow Comparison

8.2.1. Generated BPMN diagrams for the new build's process flows.

8.2.2. Compared old BPMN flows to new BPMN flows.

8.2.3. **This also found gaps** — process steps present in the old design that were missing from the new build. Different gaps than the semantic analysis found.

### 8.3 Combined Gap Resolution

8.3.1. Both methods (semantic embeddings and BPMN process flow) independently identified missing elements that the other missed.

8.3.2. The union of both gap analyses produced a comprehensive list of items that needed to be included in the new code version.

8.3.3. Gaps were triaged: some were genuine omissions to fix, some were intentional simplifications to document, some were obsolete features to formally deprecate.

---

## 9. Results

| Metric | Value |
|--------|-------|
| Compression ratio | 12.5:1 (codebase size) |
| Semantic coverage of core principles | 100% |
| Theme cluster reduction | 9:1 (243 → 27 canonical themes) |
| Intention count (old) | ~5,400 raw |
| Intention count (new) | ~434 canonical |
| Low-match items (noise) | 52 (all confirmed non-essential) |
| Gaps found by semantic analysis only | Multiple (specific intentions not carried forward) |
| Gaps found by BPMN analysis only | Multiple (process steps not carried forward) |

---

## 10. Key Learnings

10.1. **"Does it still mean what it meant?" is a better refactoring question than "does it still work?"** Functional correctness is table stakes. Semantic preservation ensures you didn't accidentally lobotomize the architecture's DNA.

10.2. **Two validation methods are better than one.** Semantic embeddings catch meaning drift. BPMN catches flow drift. Each found gaps the other missed. Use both.

10.3. **Multi-LLM review catches more than single-vendor review.** Different models have different blind spots. Gemini, Claude, and Codex each flagged different issues.

10.4. **Cross-platform spec harvesting is still painful.** Pulling specs from Claude conversation history and ChatGPT conversation history into a unified format was manual and error-prone. This needs a better process.

10.5. **Intention extraction works as a novel refactoring method.** The intention graph becomes your spec. The old code becomes reference material, not source of truth. This inverts the traditional dependency.

10.6. **Massive redundancy is the norm in evolved codebases.** The 9:1 theme compression ratio suggests that most codebases express the same principles many times in many places. Consolidation into canonical statements is healthier for both humans and AI agents.

10.7. **Anti-patterns are intentions too.** Capturing what the code deliberately avoids is as important as capturing what it does. Negative space is signal.

---

## 11. Future Improvements

11.1. **Automate the cross-platform spec harvesting** — build a pipeline that can pull relevant specs from conversation history across Claude, ChatGPT, and other LLM platforms without manual copy-paste.

11.2. **Wire the Intention Engine into the hive** — make intention scanning a bee task type so it can run periodically and feed results into KB injection automatically.

11.3. **Improve BPMN tooling** — the BPMN modeling is still somewhat manual; better automation of process flow extraction from code would strengthen this leg.

11.4. **Continuous intention drift monitoring** — run embedding comparisons on every commit to detect when code begins drifting from stated intentions, before the gap becomes large.

11.5. **Formalize the two-method validation** — create a standard checklist combining semantic + BPMN comparison that can be run on any refactor.

---

## 12. Applicability

This methodology is not specific to the deiasolutions repo. It applies to any codebase where:

12.1. The intent has drifted from the implementation over time.

12.2. Specs are scattered across code, docs, conversations, and tribal knowledge.

12.3. Multiple contributors (human or AI) have added code without a unified architectural vision.

12.4. The codebase is too large for any single reviewer to hold in their head.

The Intention Engine turns a subjective question ("did we keep the soul?") into a measurable one — and that's the real contribution.

---

*Filed as working reference for the SimDecisions hive.*  
*Methodology: Intention Engine + BPMN + Multi-LLM Review*  
*Status: Proof of concept — validated on deiasolutions repo refactor*
