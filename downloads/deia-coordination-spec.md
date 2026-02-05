# DEIA Multi-Agent Coordination Specification

**Version:** 1.0  
**Date:** 2025-10-21  
**Author:** Dave Eichler with Claude Sonnet 4.5  
**Status:** Ready for Season 1 Implementation

---

## Executive Summary

DEIA enables one human + multiple AI agents to run complex projects simultaneously through file-based coordination, autonomous task execution, and telemetry-driven learning.

**Core Innovation:** Tasks are sized for bot autonomy (not time). Bots work in parallel. System learns actual productivity from telemetry.

---

## The 5-Bot Architecture

### **Bot 001: Strategy Queen (Claude.ai)**
- **Role:** Strategic planning, architecture decisions, season planning
- **Input:** Dave's vision, market needs, telemetry from previous seasons
- **Output:** Season plans, ADRs, high-level direction
- **Cadence:** Once per season (plans entire season upfront)

### **Bot 002: Task Master (Claude.ai or GPT)**
- **Role:** Break seasons into flights, create autonomous tasks for workers
- **Input:** Season plan from Bot 001
- **Output:** Flight plans with 3-5 tasks per worker bot
- **Cadence:** Once per flight

### **Bot 003: FBB Full-Stack (Codex or Claude Code)**
- **Role:** FamilyBondBot backend + frontend development
- **Input:** Tasks from Bot 002
- **Output:** Working code, tests, deployments
- **Cadence:** Continuous (executes assigned tasks)

### **Bot 004: DEIA Full-Stack (Codex or Claude Code)**
- **Role:** DEIA coordination layer, CLI, extensions
- **Input:** Tasks from Bot 002
- **Output:** Working code, tests, deployments
- **Cadence:** Continuous (executes assigned tasks)

### **Bot 005: Web/Docs/Integration (Claude.ai)**
- **Role:** Landing pages, documentation, FBB↔DEIA integration
- **Input:** Tasks from Bot 002
- **Output:** Markdown docs, HTML, integration code
- **Cadence:** Continuous (executes assigned tasks)

### **Bot 000: Dave (Coordinator)**
- **Role:** Vision keeper, approver, unblocker, strategic decisions
- **Input:** All bot outputs, telemetry, blockers
- **Output:** Approvals, course corrections, strategic guidance
- **Cadence:** Daily reviews (15-30 min), weekly deep dives

---

## Work Unit Definitions

### **Task: Autonomous Work Unit**

A task is work a specific bot can complete independently:
- ✅ Clear inputs, outputs, success criteria
- ✅ Bot has all information needed
- ✅ No mid-task intervention required
- ✅ Verifiable completion
- ❌ NOT defined by time/effort

**Quality Criteria:**
- **Autonomy:** Bot doesn't need Dave mid-task
- **Completeness:** Output is done, not partial
- **Quality:** Meets standards (tests pass, docs clear)
- **Carbon efficiency:** Uses appropriate model (not overkill)

**Good Task Examples:**
- "Fix HTTPX test client usage pattern" (clear, executable)
- "Implement email verification flow" (defined pattern)
- "Create .deia/ directory structure per spec" (pure execution)

**Bad Task Examples:**
- "Improve performance" (vague)
- "Build entire browser extension" (too large)
- "Decide on architecture" (requires judgment)

### **Flight: Batch of Autonomous Tasks**

A flight is:
- 3-5 tasks per bot
- All tasks can be completed autonomously
- No inter-task dependencies (bots work parallel)
- Completes when all tasks done

**NOT:**
- ❌ A time period
- ❌ A deadline
- ❌ A work day

### **Season: Scope of Work**

A season is:
- Coherent body of work with clear goal
- ~10 flights
- ~120-150 total tasks across all bots

**Success Criteria:**
- Goal achieved (e.g., "FBB beta launched")
- Quality maintained
- Carbon efficient

**NOT:**
- ❌ A sprint
- ❌ 2 weeks
- ❌ Any time duration

---

## Coordination Protocol (File-Based IPC)

### **Directory Structure:**

```
~/Downloads/coordination/
├── seasons/
│   └── season-001-beta-launch/
│       ├── plan.md                    # From Bot 001
│       ├── flight-001/
│       │   ├── tasks-bot-003.md       # From Bot 002
│       │   ├── tasks-bot-004.md
│       │   ├── tasks-bot-005.md
│       │   ├── output-bot-003.md      # From Bot 003
│       │   ├── output-bot-004.md
│       │   ├── output-bot-005.md
│       │   ├── blockers.md            # Any bot
│       │   └── review-dave.md         # From Dave
│       ├── flight-002/
│       │   └── ...
│       └── retrospective.md           # End of season
│
└── handoffs/
    ├── YYYY-MM-DD-FROM-TO-TYPE-subject.md
    └── ...
```

### **Handoff File Format:**

```markdown
---
from: BOT-001
to: BOT-002
type: SEASON_PLAN
priority: HIGH
date: 2025-10-21T10:00:00Z
---

# [Subject]

[Content]

## Next Actions:
- Action 1
- Action 2

## Questions:
- Question 1

---
**Handoff complete. Ball in [TO]'s court.**
```

### **Task File Format:**

```markdown
# Flight [N] Tasks: Bot [ID]

## Task 1: [Clear Title]
**Input:** What bot needs to start
**Output:** What bot produces
**Success Criteria:** How to verify completion
**Autonomy Check:** ✅ Can complete without intervention

## Task 2: [Clear Title]
[...]

## Flight Success:
All tasks complete OR carried forward with reason
```

### **Output File Format:**

```markdown
# Bot [ID] Output: Flight [N]

## Task 1: [Title]
**Status:** ✅ Complete / ⚠️ Partial / ❌ Blocked
**Output:** [What was produced]
**Notes:** [Any important context]

## Task 2: [Title]
[...]

## Blockers:
[List any blockers encountered]

## Timestamp:** [ISO-8601]
```

---

## Telemetry Framework

### **Quality Metrics (What Matters):**

```yaml
season_outcomes:
  goal_achieved: true/false
  deliverables_complete: [list]
  quality_indicators:
    tests_passing: percentage
    security_issues: count
    user_satisfaction: score
```

### **Autonomy Metrics (Bot Independence):**

```yaml
bot_autonomy:
  tasks_completed_first_pass: X/Y (percentage)
  tasks_needing_revision: count
  tasks_blocked: count
  dave_intervention_rate: percentage
  
  by_bot:
    bot_003_autonomy: percentage
    bot_004_autonomy: percentage
    bot_005_autonomy: percentage
```

### **Efficiency Metrics (Carbon & Model Selection):**

```yaml
carbon_efficiency:
  total_carbon: kg CO2
  carbon_per_task: kg CO2
  
  model_appropriateness:
    tasks_using_right_model: percentage
    tasks_using_overkill: percentage
    
  carbon_savings:
    vs_all_opus: kg CO2 (percentage reduction)
```

### **Bottleneck Analysis:**

```yaml
blockers:
  total_count: number
  
  by_type:
    unclear_requirements: count
    missing_dependency: count
    quality_issue: count
    
  resolution:
    dave_clarified: count
    bot_collaborated: count
    task_redefined: count
```

### **Observational (Not Targets):**

```yaml
calendar_observations:
  start_date: date
  end_date: date
  days_elapsed: number
  
dave_time_invested:
  coordination_hours: number
  unblocking_hours: number
  planning_hours: number
  total_hours: number
```

---

## Season Planning Process

### **1. Bot 001 Creates Season Plan**

**Input:**
- Dave's vision document
- Telemetry from previous seasons
- Current project state

**Output:**
- Season goal (clear, measurable)
- ~10 flight breakdown
- Bot assignments per flight
- Success criteria
- Risk analysis

**File:** `seasons/season-NNN/plan.md`

### **2. Bot 002 Breaks Flight Into Tasks**

**Input:**
- Bot 001's season plan
- Current flight number

**Output:**
- 3-5 autonomous tasks per worker bot
- Clear inputs/outputs/success criteria
- Dependency analysis
- Dave pre-flight actions (if any)

**Files:** `flight-NNN/tasks-bot-00X.md`

### **3. Worker Bots Execute Tasks**

**Input:**
- Task assignments from Bot 002

**Output:**
- Completed work (code, docs, etc.)
- Status per task
- Blockers (if any)

**Files:** `flight-NNN/output-bot-00X.md`

### **4. Dave Reviews & Approves**

**Input:**
- All bot outputs
- Blocker reports

**Output:**
- Approval or course corrections
- Blocker resolutions
- Next flight authorization

**File:** `flight-NNN/review-dave.md`

### **5. Bot 002 Plans Next Flight**

**Input:**
- Dave's approval
- Carryforward tasks (if any)

**Output:**
- Next flight task assignments

**Repeat 3-5 for each flight**

### **6. Season Retrospective**

**Input:**
- All flight telemetry
- Goal achievement status

**Output:**
- Learnings captured
- Adjustments for next season
- Updated bot productivity estimates

**File:** `seasons/season-NNN/retrospective.md`

---

## Dave's Daily Workflow

### **Morning Review (15 minutes):**

```bash
cd ~/Downloads/coordination/seasons/current-season/flight-current/

# Check overnight progress
cat output-bot-003.md
cat output-bot-004.md
cat output-bot-005.md

# Any blockers?
cat blockers.md

# Approve or redirect
echo "✅ Approved, proceed to next flight" >> review-dave.md
# OR
echo "⚠️ Issue with Task X, here's guidance: [...]" >> review-dave.md
```

### **Evening Check (10 minutes):**

```bash
# Quick status check
grep "Status:" output-*.md

# Any end-of-day questions?
cat questions-for-dave.md
```

### **Weekly Deep Dive (1 hour):**

```bash
# Mid-season review
cat flight-*/review-dave.md > mid-season-summary.md

# Adjust remaining flights if needed
# Update Bot 001 with course corrections
```

---

## Task Sizing Guidelines

### **Autonomy Tests:**

**Test 1: Can bot start immediately?**
- ✅ Yes → Task is autonomous
- ❌ No, needs clarification → Refine task

**Test 2: Can bot finish without asking?**
- ✅ Yes → Well-defined
- ❌ No, will need guidance → Split smaller

**Test 3: Is success objective?**
- ✅ "Tests pass" → Clear
- ❌ "Make it better" → Too vague

**Test 4: Requires strategic judgment?**
- ✅ No, it's execution → Good bot task
- ❌ Yes, it's a decision → Dave task

### **Common Anti-Patterns:**

**Too Vague:**
- ❌ "Improve performance"
- ✅ "Reduce API response time to <200ms for /health endpoint"

**Too Large:**
- ❌ "Build browser extension"
- ✅ Break into: "Design extension architecture" (Dave) + "Implement manifest.json" (bot) + "Build popup UI" (bot) + etc.

**Requires Judgment:**
- ❌ "Choose best approach"
- ✅ Bot provides analysis, Dave chooses

**Missing Dependencies:**
- ❌ "Integrate Stripe" (needs API keys)
- ✅ "Write Stripe integration code" (bot) + "Configure Stripe keys" (Dave)

---

## Carbon-Optimized Task Assignment

### **Model Selection by Task Complexity:**

**High-Complexity (Claude Opus):**
- Strategic thinking
- Architecture design
- Complex problem-solving

**Medium-Complexity (Claude Sonnet/GPT-4):**
- Standard implementation
- Documentation
- Integration work

**Low-Complexity (GPT-4o-mini/Qwen/Local):**
- Simple edits
- Mechanical changes
- Test data generation

**Example Flight:**
```
Bot 003 using Opus: Design crisis detection (strategic)
Bot 003 using Sonnet: Implement email flow (standard)
Bot 004 using Qwen: Update env var names (mechanical)
Bot 005 using GPT-4: Write API docs (clear structure)

Carbon impact: 0.4 kg vs 0.8 kg if all Opus (50% savings)
```

---

## Integration with DEIA Methodology

### **Every Season Generates BOK:**

As bots work, patterns emerge:
- Successful approaches → `bok/patterns/`
- Failed approaches → `bok/antipatterns/`
- Decisions made → `decisions/ADR-*.md`

### **Session Logging (RSE Format):**

All coordination events logged:
```jsonl
{"ts":"2025-10-21T10:00:00Z","agent":"bot-002","action":"flight_start","flight":1}
{"ts":"2025-10-21T10:05:00Z","agent":"bot-003","action":"task_start","task":"fix-tests"}
{"ts":"2025-10-21T12:30:00Z","agent":"bot-003","action":"task_complete","task":"fix-tests"}
{"ts":"2025-10-21T12:35:00Z","agent":"dave","action":"approve_task","task":"fix-tests"}
```

### **Telemetry Feeds Future Planning:**

Bot 001 (Strategy Queen) uses past season data:
- "Flight 3 in Season 1 took 50% longer than estimated"
- "Integration tasks consistently underestimated"
- "Bot 004 has 95% autonomy (very efficient)"

Adjusts Season 2 planning accordingly.

---

## Getting Started: Season 1 Kickoff

### **Step 1: Create Structure (30 min)**

```bash
mkdir -p ~/Downloads/coordination/{seasons/season-001,handoffs}
cd ~/Downloads/coordination/seasons/season-001
for i in {001..010}; do mkdir -p flight-$i; done
```

### **Step 2: Brief Bot 001 (Strategy Queen)**

Upload to Claude.ai:
- Season goal: "FBB beta-ready + DEIA foundation"
- Constraints: 2 projects simultaneously, Dave has 15 hours/week
- Output needed: Season plan with 10 flights

### **Step 3: Brief Bot 002 (Task Master)**

Upload to Claude.ai/GPT:
- Wait for Bot 001's plan
- Break Flight 1 into tasks
- Create task files for worker bots

### **Step 4: Launch Worker Bots**

Feed tasks to Bot 003, 004, 005
Let them execute

### **Step 5: Daily Coordination**

- Morning: Review outputs
- Evening: Approve/unblock
- Repeat per flight

---

## Success Criteria

**Season 1 will be successful if:**
- ✅ FBB beta launched (10-20 testers using it)
- ✅ DEIA structure operational (.deia/ methodology working)
- ✅ Bot autonomy >85% (minimal Dave intervention)
- ✅ Zero critical bugs or security incidents
- ✅ Patterns captured (5+ BOK entries)
- ✅ Dave's time <20 hours total (sustainable)

**We learn from telemetry regardless of outcome.**

---

## Document Version History

- **1.0 (2025-10-21):** Initial specification
- Framework ready for Season 1 implementation

---

**Questions? Start Season 1 and learn from telemetry.**