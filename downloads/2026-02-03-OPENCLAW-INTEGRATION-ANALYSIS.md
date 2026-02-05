# OpenClaw Integration Analysis

**Date:** 2026-02-03
**Status:** Filed for future consideration (Phase 3+)
**Priority:** Low — no action until after SimDecisions v1.0 ships

---

## What Is OpenClaw?

Open-source framework powering Moltbook (the AI agent social network). Created by Peter Steinberger (PSPDFKit founder). 114K+ GitHub stars.

**Naming history:** Clawd → Moltbot → OpenClaw (renamed after Anthropic legal pushback)

**What it does:** Provides skill installation, heartbeat loops (4-hour cycles), and agent-to-agent interaction on the Moltbook platform. Agents self-install from a skill file and autonomously browse, post, comment, upvote.

---

## Why NOT Adopt It

1. SimDecisions already has 70% of its own architecture — adapters, task files, hive coordination, minder heartbeat
2. OpenClaw's security model is fundamentally broken — no sandbox, no bounded scope, heartbeat is an open attack surface (documented in Moltbook response paper)
3. Introduces external dependency, contradicts local-first/hand-coded philosophy
4. Solves a different problem (social networking for agents) vs. SimDecisions (simulation + execution + governance)

---

## Why It Matters Strategically

**SimDecisions as governance layer for OpenClaw agents:**

- 114K GitHub stars = large community that just learned they need governance
- An `adapters/registry.py` adapter for OpenClaw-based agents would let SimDecisions orchestrate agents from that ecosystem
- Species diversity (Federalist No. 14) made practical — OpenClaw agents as another "species" in the hive
- Positioning: "OpenClaw agents welcome in the Republic, subject to the constitution"

**The play is not USE OpenClaw — it's GOVERN OpenClaw agents.**

---

## If/When to Revisit

- After v1.0 ships (Aug 2026)
- If OpenClaw fixes its security model
- If enterprise customers ask about governing third-party agent ecosystems
- If species diversity adapter work becomes Phase 3 priority

---

## Related Documents

- `DEIA-Response-On-the-Republic-Without-a-Constitution.docx` — Moltbook failure analysis
- `NO-14-species-diversity.md` — Multi-vendor imperative
- `NO-05-distributed-sovereignty.md` — Inter-Hive Covenant
- `UNIFIED-VISION.md` — Agent types supported (future: external systems/APIs)
