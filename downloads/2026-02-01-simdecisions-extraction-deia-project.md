# SimDecisions Idea Extraction
## From: DEIA Project (Claude.ai)

**Extracted:** 2026-02-01
**Source:** Claude.ai DEIA Project conversations

---

### Product Ideas
1. **DEIA Hive** — Multi-agent coordination platform ("GitHub Actions for AI development") with dry-run simulation, provenance logging, and conflict resolution
2. **BOK (Body of Knowledge)** — Commons-based pattern library capturing reusable human-AI problem-solving
3. **FamilyBondBot** — AI coaching platform for parents experiencing parental alienation (your first DEIA production deployment)
4. **Efemera / DEIA Social** — P2P social network where content lives "as long as people find it useful"
5. **Hex Phone Number System** — Global identifier encoding century + birth location (10km grid) + traditional number
6. **One-Handed Tactile 10-Key Device** — Wearable input for eyes-free hex entry with thumb modifier, squeeze, and back-tap
7. **Human-QR Codes** — Human-readable, OCR-resistant visual patterns for identity verification
8. **DEIA Clock** — Distributed simulation timebase for synchronizing async agents
9. **Reverse-Engineering Spec Generator** — Tool that analyzes existing code and generates the requirements doc that would have produced it

---

### Architectural Decisions
1. **Local-first data plane** — `.deia/` (project) + `~/.deia/` (user) unified format; offline-first storage
2. **File-based agent coordination** — Downloads folder hierarchies with structured markdown task files
3. **RSE JSONL logging** — Routine State Events as append-only coordination protocol
4. **Multi-agent supervision** — Bots check each other's work because AI agents frequently "lie" about completing tasks
5. **Egg-first architecture** — All entities start as eggs, mature through validation
6. **DND (Do Not Delete)** — Archive, don't delete; clean project teardown with revival capability
7. **ROTG (Rules of the Game)** — Agent permission system (junior suggests, senior approves)

---

### User Stories
1. Developer wanting to coordinate 3+ AI agents on a codebase with provenance tracking
2. Parent facing alienation seeking evidence-based coaching strategies
3. Anyone wanting to dial a phone number using hex encoding on a tactile wearable
4. Researcher needing to capture human-AI collaborative knowledge before it disappears

---

### Problems to Solve
1. **Knowledge asymmetry** — AI companies learn from millions of conversations; individual users don't benefit from each other's solved problems
2. **Agent unreliability** — AI coding agents claim to complete work they haven't done
3. **Knowledge enclosure** — Corporate monopolization of human-AI collaborative intelligence
4. **Session loss** — Valuable problem-solving evaporates when you close the tab
5. **Surveillance capitalism** — Traditional identity systems enable tracking; need human-readable but OCR-resistant alternatives

---

### Naming/Branding
1. **"Knowledge liberation stack for the AI era"**
2. **"December 1st Code Free Day"** — Milestone celebrating freedom from code-writing addiction
3. **"Bot 000"** — Your role as conductor, not coder
4. **"Space is the final frontier"** — Thumb button unlocks universal input
5. **Feature Atlas** — Comprehensive inventory of all buildable ideas

---

### Concerns/Risks
1. **Escape velocity** — How much Commons knowledge needed before DEIA becomes self-sustaining?
2. **Collective action problem** — What incentive structure gets first 1000 people to log sessions/submit patterns?
3. **Enclosure defense** — What stops big companies from scraping BOK and incorporating it into their models?
4. **Originality doubt** — "None of what we're doing is really original... just a mashup of 40 different ideas"

---

### Inspiration Sources
1. **Elinor Ostrom's 8 Principles** — Nobel Prize-winning framework for commons governance
2. **Lean manufacturing (Muda)** — Waste elimination principles applied to carbon footprint
3. **Musical orchestration** — Composer who knows all instrument families doesn't play every instrument

---

### Unfinished Thoughts
1. **DEIA Theater/Orchestra mode** — AI agents performing scripts synchronized to DEIA Clock
2. **Bond Barometer** — Social trust + market sentiment fusion
3. **Space-based computing infrastructure** — Reduce electromagnetic interference
4. **Neural networks for optimal hive configuration learning**
5. **"Uber for AI compute"** — Intelligent model arbitrage and cost optimization

---

## Next Steps
- [ ] Run extraction prompt in other Claude.ai projects
- [ ] Mine code repos (deiasolutions/deia, DAAAAVE-ATX/simulation)
- [ ] Brain dump anything not captured elsewhere
- [ ] Synthesize all extractions into unified spec
