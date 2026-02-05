# Metamorphosis-Inspired Repository Refactor Specification

## 1. Purpose
This document defines a refactoring strategy that treats the repository as a living system capable of metamorphosis.
Rather than incrementally refactoring existing code (bottom-up), this strategy preserves memory, intent, and architectural DNA while allowing implementation to be regenerated.

## 2. Core Metaphor: Biological Metamorphosis
- Caterpillar / Larva → legacy repository
- Chrysalis / Pupa → archival and semantic extraction
- Imaginal Discs → architectural primitives
- Genetic Memory → specs, stories, constraints
- Epigenetics & Pheromones → contextual signaling
- Adult Form → regenerated system

## 3. Guiding Principles
1. Memory over implementation  
2. Top-down before bottom-up  
3. Nothing is truly deleted  
4. Architecture is the primary artifact  

## 4. Phase 1: Chrysalis — Repository Audit
Inventory all code, backlog items, experiments, and ideas.
Extract intent, users, problems, and outcomes.
Output: archive/, repo_memory.md

## 5. Phase 2: Genetic Memory — User Stories
Translate everything into user stories and use cases.
Include rejected and abandoned ideas.
Output: user_stories.md, embeddings

## 6. Phase 3: Imaginal Discs — Primitives
Define minimal architectural components without implementation.
Output: architecture_primitives.md

## 7. Phase 4: Orchestration-First Reconstruction
Design orchestration layers before code.
Support N-level and meta-orchestration.
Output: orchestration_model.md

## 8. Phase 5: Epigenetics & Pheromones
Introduce distance-based semantic signals.
Use embedding similarity (e.g., cosine distance).
Signals bias decisions but do not override specs.

## 9. Phase 6: Regeneration
Rebuild implementation from structure and stories.
Specs remain the source of truth.

## 10. Benefits
- Architectural clarity
- Lossless idea preservation
- Long-term evolvability

## 11. Closing
This is not a refactor but a controlled metamorphosis.
