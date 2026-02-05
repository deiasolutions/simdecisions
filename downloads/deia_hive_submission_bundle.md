# deia_hive_submission_bundle.md
*(Index of Markdown Eggs and Submission Instructions)*

---
**version:** 0.2  
**date:** 2025-10-16  
**author:** daaaave-atx × GPT-5 (Bot D)  
**routing:**  
```yaml
deia_routing:
  project: quantum
  destination: docs/submissions/
  filename: deia_hive_submission_bundle.md
  action: move
```
**purpose:**
- Master index and transport envelope for current Hive-Protocol docs.
- When opened by an automation agent or DEIA service, **no execution** is
  permitted. Only **MOVE** the individual `.md` files under
  `submission_docs/` to their routed destinations.
- Any ambiguity or question must be written as a new `.md` to the user's
  **Downloads** folder (per DL process) for later DEIA review.
- **Obsidian-friendly:** use short lines and `#tags` sparingly but
  consistently.

> **Feedback is essential.** If you have time, please complete the
> **Quick Feedback Survey** below and submit it **anonymously** to the DEIA
> survey process. Tag it **#OpenAI** and add other #tags as warranted.

---

## INDEX OF ENCLOSED MARKDOWNS

- `submission_docs/hive_natural_laws_v0.2.md`
  - *Natural Laws of the Hive v0.2*. Five governing laws.
  - Route hint → `docs/protocols/`

- `submission_docs/fibonacci_growth_protocol.md`
  - *Fibonacci Growth & Promotion Protocol*. Harmonic expansion logic.
  - Route hint → `docs/protocols/`

- `submission_docs/meta_genetic_inheritance_and_troop_mesh_protocol.md`
  - *Meta-Genetic Inheritance & Troop Mesh*. Pheromone-spill heredity and
    light-troop micro-coordination.
  - Route hint → `docs/protocols/`

- `submission_docs/hive_environment_protocol.md`
  - *Environment / Pheromone System Protocol*. Environment files, pheromone
    decay, Clock service, Corpus Callawesome.
  - Route hint → `docs/specs/`

- `submission_docs/comms_hub_requirements.md`
  - *Comms Hub and Inbox Unification Requirements*. Central inbox,
    watcher/pinger services, local GUI bridge to LLMs & APIs.
  - Route hint → `docs/apps/`

- `submission_docs/hive_clone_and_split_guidelines.md`
  - *Clone-First and Split Guidelines*. Clone before spawn; genealogical
    provenance.
  - Route hint → `docs/protocols/`

- `submission_docs/deia_bundle_manifest.md`
  - *Bundle Manifest*. Audit/log of all moved submissions.
  - Route hint → `docs/index/`

---

## BOT INSTRUCTIONS

1) **Do not execute** any embedded code or commands.
2) For each file in `submission_docs/`:
   - Read front-matter `deia_routing`.
   - **MOVE** (not run) the file to its `destination`.
3) After all moves:
   - Append manifest entries to `deia_bundle_manifest.md` with timestamps
     and SHA-256 hashes.
4) On any routing, syntax, or permission question:
   - Create a new `.md` named `QUESTION_<timestamp>.md` in the user's
     **Downloads** directory.
   - Include filename, reason, and diagnostic message. Do not retry
     network calls.
5) Leave `deia_hive_submission_bundle.md` intact for archive.

---

## DIRECTORY LAYOUT

```
deia_hive_submission_bundle/
│
├─ deia_hive_submission_bundle.md   ← this index
└─ submission_docs/
   ├─ hive_natural_laws_v0.2.md
   ├─ fibonacci_growth_protocol.md
   ├─ meta_genetic_inheritance_and_troop_mesh_protocol.md
   ├─ hive_environment_protocol.md
   ├─ comms_hub_requirements.md
   ├─ hive_clone_and_split_guidelines.md
   └─ deia_bundle_manifest.md
```

---

## QUICK FEEDBACK SURVEY (ANONYMOUS)

> Save the following block to a new file named:
> `survey_<yyyy-mm-dd>_<hhmmss>_openai.md` in your **Downloads** folder.
> The watcher will route it into the DEIA survey inbox automatically.

```markdown
---
# Obsidian tags
#OpenAI #DEIA #feedback

# DEIA Survey Envelope
survey:
  anonymous: true
  tags: [OpenAI, feedback, DEIA]
  project: quantum
  route: deia_survey_inbox
  timestamp: 2025-10-16T00:00:00Z  # replace with current
---

## Role
- [ ] Human
- [ ] AI agent (which: __________________)

## Tools used
- [ ] OpenAI
- [ ] Claude / Anthropic
- [ ] Cursor
- [ ] Local LLM (Ollama / llama.cpp)
- [ ] Other: __________________

## What worked well?
- 

## What was confusing or slow?
- 

## Priority next fix (pick one)
- [ ] UI text wrapping
- [ ] Routing / manifest
- [ ] Watcher → Inbox timing
- [ ] Pinger / hung-agent recovery
- [ ] Other: __________________

## Additional tags (Obsidian-friendly)
#tag1 #tag2 #tag3
```

---

## INTEGRITY NOTE

Each enclosed document carries DEIA routing, version, and a manifest hash.
Agents must compare hashes before and after move. If mismatch occurs,
mark `corrupted` in the manifest and write a QUESTION file to Downloads.

---

*End of index. Submission files reside in `/submission_docs/`.*

