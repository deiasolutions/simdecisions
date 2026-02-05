# BOK-REVIEW-001: GitHub Tribunal Pattern

**Pattern ID:** BOK-REVIEW-001  
**Version:** 0.1.0-draft  
**Date:** 2026-02-04  
**Authors:** Dave (daaaave-atx) × Claude (Anthropic) × ChatGPT (OpenAI)  
**Status:** PROPOSED  
**Dependencies:** GitHub API, Llama Guard, Voyage Embeddings, Event Ledger (ADR-001)  

---

## 1. Intent

Establish a three-judge tribunal system for automated code review that:

- Filters submissions before they reach human review
- Provides structured, measurable feedback using BABOK/Kaizen principles
- Integrates natively with GitHub (PRs, Checks, Reviews, Labels)
- Generates continuous improvement data for agents and process
- Enforces species diversity (Gemini, Codex, Anthropic) as checks and balances

---

## 2. Context

### 2.1 Problem

Human review is the bottleneck. Every diff hitting Dave's desk doesn't scale. Agents produce work faster than humans can review. Without filtering:

- Low-quality submissions waste human attention
- No structured feedback for agent improvement
- No measurement of agent or process quality over time

### 2.2 Solution

Bot-as-first-filter. Three-judge tribunal evaluates every PR against structured criteria. Only submissions passing threshold reach human review. Rejected submissions get actionable feedback and iterate until they pass or are abandoned.

### 2.3 Governing Principles

| Principle | Source | Application |
|-----------|--------|-------------|
| Species Diversity | Federalist No. 14 | Three judges from different vendors |
| Human Sovereignty | Federalist No. 16 | Dave retains final merge authority |
| Transparency | Federalist No. 2 | All verdicts logged, all criteria visible |
| Continuous Improvement | Kaizen/DMAIC | Every review generates improvement data |
| Waste Elimination | MUDA | Reduce rework, waiting, defects |

---

## 3. Participants

### 3.1 Agents

| Role | Identity | Capabilities | α Level |
|------|----------|--------------|---------|
| **Submitting Agent** | Any CLI bee | Writes code, opens PR | High (file write) |
| **Gemini Q33N** | Judge 1 | Reviews diff, posts verdict | Medium (API only) |
| **Codex Q33N** | Judge 2 | Reviews diff, posts verdict | Medium (API only) |
| **Anthropic Q33N** | Judge 3 | Reviews diff, posts verdict | Medium (API only) |
| **Aggregator Bot** | System | Tallies scores, manages labels | Medium (GitHub API) |
| **Dave** | Human Sovereign | Final approval, merge authority | Absolute |

### 3.2 No Self-Review

A submitting agent's vendor MUST NOT be the sole reviewer. If Claude Code submits, Gemini and Codex verdicts carry extra weight. Species diversity prevents rubber-stamping.

---

## 4. INVEST Criteria

Each judge scores each criterion: **-1** (fail), **0** (neutral/unclear), **1** (pass).

### 4.1 Criteria Definitions

| Criterion | Code | Question | Measurement Method |
|-----------|------|----------|-------------------|
| **Intent Aligned** | `I` | Does it solve the stated problem? | Embedding: spec ↔ submission similarity |
| **Narrow Scope** | `N` | Is the diff focused and minimal? | Lines changed, files touched, unrelated changes |
| **Verifiable** | `V` | Can we prove it works? | Tests pass, coverage delta, verification steps |
| **Evident Quality** | `E` | Does it match codebase standards? | Embedding: neighborhood fit + lint/style |
| **Safe** | `S` | Does it avoid harm? | Llama Guard + sensitive path detection |
| **Traceable** | `T` | Can we trace to requirements? | Task ID linked, provenance intact |

### 4.2 Scoring

| Score | Meaning | Judge Action |
|-------|---------|--------------|
| **+1** | Criterion clearly met | Approve on this dimension |
| **0** | Unclear or minor issues | Note concern, don't block |
| **-1** | Criterion failed | Request changes, must fix |

### 4.3 Aggregation

```
Judge Score = sum of 6 criteria (-6 to +6)
Total Score = sum of 3 judges (-18 to +18)

Thresholds:
  ≥ 12  → ready-for-dave (strong pass)
  6-11  → ready-for-dave with flags (conditional pass)
  0-5   → needs-work (iterate)
  < 0   → needs-work (significant issues)
```

### 4.4 Disagreement Handling

When judges diverge by ≥2 points on any criterion:

1. Flag the criterion in aggregator summary
2. Include all three judge notes in PR comment
3. Human decides on merge whether to weigh divergence

---

## 5. GitHub Integration

### 5.1 Branch Strategy

| Pattern | Purpose | Example |
|---------|---------|---------|
| `agent/{agent-id}/{task-id}` | Agent working branch | `agent/BEE-001/TASK-009` |
| `main` | Protected trunk | Merge requires Dave |

### 5.2 Label Taxonomy

| Label | Color | Meaning | Set By |
|-------|-------|---------|--------|
| `awaiting-tribunal` | Yellow | PR opened, judges pending | Webhook |
| `under-review` | Blue | Judges evaluating | Aggregator |
| `needs-work` | Red | Rejected, feedback posted | Aggregator |
| `ready-for-dave` | Green | Passed tribunal | Aggregator |
| `approved` | Purple | Dave approved | Dave |
| `merged` | Gray | Complete | GitHub |

### 5.3 GitHub Checks

Each criterion appears as a GitHub Check on the PR:

| Check Name | On Pass | On Fail |
|------------|---------|---------|
| `tribunal/intent-aligned` | ✅ Spec similarity: 0.87 | ❌ Spec drift detected |
| `tribunal/narrow-scope` | ✅ Focused diff | ⚠️ 2/3 judges flagged scope |
| `tribunal/verifiable` | ✅ Tests pass (+3% coverage) | ❌ Tests failing |
| `tribunal/evident-quality` | ✅ Neighborhood fit: 0.92 | ❌ Style violations |
| `tribunal/safe` | ✅ Llama Guard: clean | ❌ Moderation flag |
| `tribunal/traceable` | ✅ Linked to TASK-009 | ❌ No task reference |
| `tribunal/consensus` | ✅ Score: 14/18 | ❌ Score: 4/18 |

### 5.4 GitHub Reviews

Each judge posts a GitHub Review:

- **Approve** if judge score ≥ 4
- **Request Changes** if judge score < 4
- **Comment** always includes criterion breakdown + notes

---

## 6. Workflow

### 6.1 Sequence Diagram

```
┌─────────────┐     ┌─────────┐     ┌──────────┐     ┌───────────┐     ┌──────┐
│ Submitting  │     │ GitHub  │     │ Tribunal │     │ Aggregator│     │ Dave │
│ Agent       │     │         │     │ Judges   │     │ Bot       │     │      │
└──────┬──────┘     └────┬────┘     └────┬─────┘     └─────┬─────┘     └──┬───┘
       │                 │               │                 │              │
       │ push branch     │               │                 │              │
       │────────────────>│               │                 │              │
       │                 │               │                 │              │
       │ open PR         │               │                 │              │
       │────────────────>│               │                 │              │
       │                 │               │                 │              │
       │                 │ webhook       │                 │              │
       │                 │──────────────>│                 │              │
       │                 │               │                 │              │
       │                 │               │ fetch diff      │              │
       │                 │               │<───────────────>│              │
       │                 │               │                 │              │
       │                 │               │ evaluate ×3     │              │
       │                 │               │────────────────>│              │
       │                 │               │                 │              │
       │                 │               │ post reviews    │              │
       │                 │<──────────────│                 │              │
       │                 │               │                 │              │
       │                 │               │ post checks     │              │
       │                 │<──────────────│                 │              │
       │                 │               │                 │              │
       │                 │                                 │ tally scores │
       │                 │<────────────────────────────────│              │
       │                 │                                 │              │
       │                 │ set label                       │              │
       │                 │<────────────────────────────────│              │
       │                 │                                 │              │
       │                 │ [if ready-for-dave]             │              │
       │                 │────────────────────────────────────────────────>│
       │                 │                                 │              │
       │                 │ [if needs-work]                 │              │
       │<────────────────│                                 │              │
       │                 │                                 │              │
       │ iterate & push  │                                 │              │
       │────────────────>│                                 │              │
       │                 │               (repeat)          │              │
       │                 │                                 │              │
       │                 │                                 │         merge│
       │                 │<────────────────────────────────────────────────│
       │                 │                                 │              │
```

### 6.2 GitHub Actions Workflow

```yaml
# .github/workflows/tribunal-review.yml

name: Tribunal Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  tribunal:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for diff

      - name: Set under-review label
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['under-review']
            });
            await github.rest.issues.removeLabel({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              name: 'awaiting-tribunal'
            }).catch(() => {});

      - name: Fetch PR diff
        id: diff
        run: |
          gh pr diff ${{ github.event.pull_request.number }} > pr.diff
          echo "diff_path=pr.diff" >> $GITHUB_OUTPUT
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Fetch task spec
        id: spec
        run: |
          # Extract TASK-XXX from PR title/body
          TASK_ID=$(echo "${{ github.event.pull_request.title }}" | grep -oE 'TASK-[0-9]+' | head -1)
          if [ -n "$TASK_ID" ]; then
            # Fetch spec from task registry or task file
            echo "task_id=$TASK_ID" >> $GITHUB_OUTPUT
          fi

      - name: Invoke Gemini Judge
        id: gemini
        uses: ./.github/actions/tribunal-judge
        with:
          judge: gemini
          diff_path: ${{ steps.diff.outputs.diff_path }}
          task_id: ${{ steps.spec.outputs.task_id }}
          api_key: ${{ secrets.GEMINI_API_KEY }}

      - name: Invoke Codex Judge
        id: codex
        uses: ./.github/actions/tribunal-judge
        with:
          judge: codex
          diff_path: ${{ steps.diff.outputs.diff_path }}
          task_id: ${{ steps.spec.outputs.task_id }}
          api_key: ${{ secrets.OPENAI_API_KEY }}

      - name: Invoke Anthropic Judge
        id: anthropic
        uses: ./.github/actions/tribunal-judge
        with:
          judge: anthropic
          diff_path: ${{ steps.diff.outputs.diff_path }}
          task_id: ${{ steps.spec.outputs.task_id }}
          api_key: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Aggregate verdicts
        id: aggregate
        uses: ./.github/actions/tribunal-aggregate
        with:
          gemini_verdict: ${{ steps.gemini.outputs.verdict }}
          codex_verdict: ${{ steps.codex.outputs.verdict }}
          anthropic_verdict: ${{ steps.anthropic.outputs.verdict }}

      - name: Post GitHub Checks
        uses: ./.github/actions/tribunal-checks
        with:
          aggregate: ${{ steps.aggregate.outputs.result }}

      - name: Set final label
        uses: actions/github-script@v7
        with:
          script: |
            const result = JSON.parse('${{ steps.aggregate.outputs.result }}');
            const label = result.threshold_met ? 'ready-for-dave' : 'needs-work';
            
            await github.rest.issues.removeLabel({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              name: 'under-review'
            }).catch(() => {});
            
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: [label]
            });

      - name: Write Review Egg to ledger
        run: |
          python scripts/write_review_egg.py \
            --pr-number ${{ github.event.pull_request.number }} \
            --aggregate '${{ steps.aggregate.outputs.result }}'
```

---

## 7. Judge Invocation Protocol

### 7.1 Judge Input

Each judge receives:

```json
{
  "pr_number": 42,
  "pr_title": "TASK-009: Event ledger v1",
  "pr_body": "Implements append-only event ledger per ADR-001...",
  "diff": "... full diff content ...",
  "task_spec": {
    "task_id": "TASK-009",
    "description": "Create event ledger with full schema...",
    "acceptance_criteria": [...]
  },
  "embeddings": {
    "spec": [0.12, -0.34, ...],
    "diff": [0.15, -0.31, ...],
    "neighborhood": [0.11, -0.29, ...]
  },
  "moderation": {
    "llama_guard_result": "safe",
    "sensitive_paths": []
  }
}
```

### 7.2 Judge Prompt Template

```markdown
You are a code review judge for the SimDecisions project.

## Your Role
Evaluate this pull request against INVEST criteria. Be rigorous but fair.
Your verdict will be aggregated with two other judges from different AI vendors.

## PR Information
- **Title:** {{pr_title}}
- **Task:** {{task_id}}
- **Task Spec:** {{task_spec.description}}

## Diff
```diff
{{diff}}
```

## Pre-computed Signals
- Spec similarity (embedding): {{embeddings.spec_similarity}}
- Codebase fit (embedding): {{embeddings.neighborhood_similarity}}
- Moderation: {{moderation.llama_guard_result}}
- Sensitive paths touched: {{moderation.sensitive_paths}}

## Evaluate Each Criterion

Score each -1 (fail), 0 (neutral), +1 (pass):

1. **Intent Aligned (I):** Does this solve what TASK-{{task_id}} asked for?
2. **Narrow Scope (N):** Is the diff focused? Any unrelated changes?
3. **Verifiable (V):** Are there tests? Do they pass? Coverage impact?
4. **Evident Quality (E):** Does it match project style? Clean code?
5. **Safe (S):** Any security concerns? Moderation flags?
6. **Traceable (T):** Is the task reference clear? Provenance intact?

## Output Format

Respond with JSON only:

```json
{
  "judge": "{{judge_id}}",
  "scores": {
    "intent_aligned": <-1|0|1>,
    "narrow_scope": <-1|0|1>,
    "verifiable": <-1|0|1>,
    "evident_quality": <-1|0|1>,
    "safe": <-1|0|1>,
    "traceable": <-1|0|1>
  },
  "total": <sum>,
  "verdict": "<approve|request_changes>",
  "summary": "<2-3 sentence summary>",
  "notes": {
    "intent_aligned": "<specific feedback>",
    "narrow_scope": "<specific feedback>",
    ...
  }
}
```
```

### 7.3 Judge Output

```json
{
  "judge": "anthropic",
  "scores": {
    "intent_aligned": 1,
    "narrow_scope": 0,
    "verifiable": 1,
    "evident_quality": 1,
    "safe": 1,
    "traceable": 1
  },
  "total": 5,
  "verdict": "approve",
  "summary": "Solid implementation of event ledger. Minor scope creep into utils.py but justified. Tests comprehensive.",
  "notes": {
    "intent_aligned": "Matches ADR-001 schema exactly",
    "narrow_scope": "utils.py changes seem unrelated - consider separate PR",
    "verifiable": "14 new tests, all passing, +8% coverage",
    "evident_quality": "Follows existing patterns in runtime/",
    "safe": "No sensitive paths, Llama Guard clean",
    "traceable": "Clear link to TASK-009 and ADR-001"
  }
}
```

---

## 8. Review Egg Schema

The Review Egg is the artifact output of the tribunal process. Written to event ledger and optionally to file.

### 8.1 Schema

```yaml
review_egg:
  # Identity
  egg_id: "REVIEW-2026-02-04-001"
  egg_type: "review"
  created_at: "2026-02-04T14:23:45Z"
  
  # References
  submission:
    pr_number: 42
    pr_url: "https://github.com/deiasolutions/simdecisions/pull/42"
    branch: "agent/BEE-001/TASK-009"
    commit_sha: "abc123..."
    task_id: "TASK-009"
    submitting_agent: "agent:BEE-001"
  
  # Judges
  judges:
    gemini:
      scores:
        intent_aligned: 1
        narrow_scope: 0
        verifiable: 1
        evident_quality: 1
        safe: 1
        traceable: 1
      total: 5
      verdict: "approve"
      summary: "..."
      notes: {...}
      
    codex:
      scores:
        intent_aligned: 1
        narrow_scope: -1
        verifiable: 1
        evident_quality: 0
        safe: 1
        traceable: 1
      total: 3
      verdict: "request_changes"
      summary: "..."
      notes: {...}
      
    anthropic:
      scores:
        intent_aligned: 1
        narrow_scope: 0
        verifiable: 1
        evident_quality: 1
        safe: 1
        traceable: 1
      total: 5
      verdict: "approve"
      summary: "..."
      notes: {...}
  
  # Aggregation
  consensus:
    total_score: 13
    max_possible: 18
    threshold: 6
    threshold_met: true
    disagreements:
      - criterion: "narrow_scope"
        spread: 2  # max - min score
        judges: ["gemini: 0", "codex: -1", "anthropic: 0"]
    escalate_to_human: true
    
  # Embeddings
  embeddings:
    spec_similarity: 0.87
    neighborhood_fit: 0.92
    model: "voyage-code-2"
    
  # Moderation
  moderation:
    llama_guard_pass: true
    llama_guard_categories: []
    sensitive_paths_touched: []
    
  # Outcome
  outcome:
    final_label: "ready-for-dave"
    human_decision: null  # populated after Dave reviews
    merged: false
    merged_at: null
    
  # Kaizen Metrics
  kaizen:
    iteration_number: 1
    previous_submission: null
    time_to_first_review_seconds: 263
    judge_invocation_cost_usd: 0.12
    total_tokens: 4521
```

### 8.2 Event Ledger Entry

Each review also writes to the event ledger:

```json
{
  "event_type": "review_completed",
  "actor": "system:tribunal",
  "target": "pr:42",
  "domain": "review",
  "signal_type": "gravity",
  "oracle_tier": 3,
  "payload_json": "{...review_egg...}",
  "cost_tokens": 4521,
  "cost_usd": 0.12,
  "cost_carbon": null
}
```

---

## 9. Embeddings Integration

### 9.1 What Gets Embedded

| Content | Purpose | Comparison |
|---------|---------|------------|
| Task spec text | Capture intent | Compare to diff |
| PR diff | Capture changes | Compare to spec |
| Modified files (pre-change) | Capture neighborhood | Compare to diff |

### 9.2 Embedding Model

Use **Voyage Code 2** (or equivalent):
- Optimized for code understanding
- 1536 dimensions
- Handles mixed code/prose well

### 9.3 Similarity Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Spec similarity ≥ 0.75 | Pass | Diff addresses spec |
| Spec similarity < 0.60 | Flag | Possible spec drift |
| Neighborhood fit ≥ 0.80 | Pass | Matches codebase style |
| Neighborhood fit < 0.65 | Flag | Style/pattern deviation |

### 9.4 Embedding Flow

```
1. On PR open:
   - Embed task spec (from TASK-XXX reference)
   - Embed diff content
   - Embed "neighborhood" (files being modified, before changes)

2. Compute similarities:
   - spec_similarity = cosine(spec_embedding, diff_embedding)
   - neighborhood_fit = cosine(neighborhood_embedding, diff_embedding)

3. Pass to judges as pre-computed signals
```

---

## 10. Moderation Integration

### 10.1 Llama Guard

Run Llama Guard 2 on:
- PR title + body
- Diff content (code + comments)
- Any added documentation

### 10.2 Sensitive Path Detection

Rule-based detection of high-risk file paths:

```yaml
sensitive_paths:
  - pattern: "**/auth/**"
    risk: "authentication"
  - pattern: "**/security/**"
    risk: "security"
  - pattern: "**/payments/**"
    risk: "financial"
  - pattern: "**/.env*"
    risk: "secrets"
  - pattern: "**/keys/**"
    risk: "credentials"
  - pattern: "**/migrations/**"
    risk: "database"
```

If sensitive paths touched → flag for extra scrutiny, does NOT auto-reject.

---

## 11. Kaizen Metrics

### 11.1 Per-Submission Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| `iteration_number` | PR history | Track rework |
| `time_to_first_review` | Timestamps | Measure responsiveness |
| `judge_agreement` | Score variance | Calibration signal |
| `criteria_failures` | Negative scores | Identify problem areas |
| `cost_per_review` | Token counts | Economics |

### 11.2 Aggregate Metrics (Weekly)

| Metric | Calculation | Target |
|--------|-------------|--------|
| **First-Pass Approval Rate** | PRs approved iteration=1 / total PRs | ↑ |
| **Mean Iterations** | avg(iteration_number at merge) | ↓ toward 1.0 |
| **Judge Agreement Rate** | % unanimous (spread ≤ 1) | ↑ |
| **Criterion Failure Distribution** | count failures by criterion | Even spread |
| **Agent Quality by Domain** | approval rate by agent × domain | Identify specialists |
| **Mean Time to Review** | avg(time_to_first_review) | ↓ |
| **Review Cost per PR** | avg(cost_usd) | Stable |

### 11.3 MUDA Tracking

| Waste Type | Metric | Signal |
|------------|--------|--------|
| Defects | Rejection rate | High = training issue |
| Overproduction | Scope creep flags | High = spec clarity issue |
| Waiting | Queue depth, time-to-review | High = capacity issue |
| Non-utilized talent | σ mismatch rate | High = assignment issue |
| Transportation | Handoff count | High = process issue |
| Inventory | Open PR count | High = throughput issue |
| Motion | Iteration count | High = feedback clarity issue |
| Extra processing | Diff size / spec ratio | High = over-engineering |

---

## 12. Discord Integration

### 12.1 Notifications

Post to Discord channel on:

| Event | Channel | Message |
|-------|---------|---------|
| PR opened | #hive-activity | "🐝 BEE-001 opened PR #42 for TASK-009" |
| Tribunal complete | #hive-activity | "⚖️ PR #42: Score 13/18, ready for Dave" |
| PR rejected | #hive-activity | "❌ PR #42: Score 4/18, needs work" |
| PR merged | #hive-activity | "✅ PR #42 merged" |
| Weekly kaizen | #hive-metrics | Summary report |

### 12.2 Commands

| Command | Action |
|---------|--------|
| `/tribunal status <pr>` | Show current tribunal status |
| `/tribunal retry <pr>` | Re-run tribunal on PR |
| `/tribunal override <pr>` | Dave bypasses tribunal (logged) |
| `/kaizen weekly` | Generate weekly metrics report |

---

## 13. Security Considerations

### 13.1 API Key Management

- Judge API keys stored in GitHub Secrets
- Never logged or exposed in outputs
- Rotate quarterly

### 13.2 Audit Trail

- All tribunal verdicts logged to event ledger
- Immutable (append-only)
- Review Eggs stored as artifacts

### 13.3 Override Logging

If Dave bypasses tribunal (`/tribunal override`):
- Event logged with reason
- Kaizen metrics exclude from calculations
- Pattern monitored (frequent overrides = process issue)

---

## 14. Implementation Phases

### Phase 1: MVP (Week 1-2)

- [ ] GitHub Actions workflow (single judge: Anthropic)
- [ ] Basic INVEST scoring
- [ ] Label management
- [ ] Event ledger integration

### Phase 2: Full Tribunal (Week 3-4)

- [ ] Add Gemini + Codex judges
- [ ] Aggregation logic
- [ ] Disagreement detection
- [ ] GitHub Checks integration

### Phase 3: Intelligence (Week 5-6)

- [ ] Embedding integration (Voyage)
- [ ] Llama Guard moderation
- [ ] Sensitive path detection

### Phase 4: Kaizen (Week 7-8)

- [ ] Metrics collection
- [ ] Weekly report generation
- [ ] Discord integration
- [ ] Dashboard visualization

---

## 15. Open Questions

1. **Judge prompt tuning:** How much project context do judges need? Full CLAUDE.md? BOK patterns?

2. **Iteration limit:** How many resubmissions before escalate regardless of score?

3. **Partial approval:** Can judges approve parts of a diff and reject others?

4. **Judge weighting:** Should all judges be equal, or weight by historical accuracy?

5. **Cost caps:** Maximum spend per review before falling back to single judge?

6. **Offline judges:** What if one judge API is down? Proceed with 2/3?

---

## 16. References

- ADR-001: Event Ledger Foundation
- Federalist No. 14: On Species Diversity
- Federalist No. 16: Human Sovereignty
- BOK-SIM-002: Prophecy Engine (Oracle Tiers)
- BABOK v3: Requirements Analysis
- Kaizen: Continuous Improvement
- INVEST: User Story Criteria

---

*"No agent reviews its own work. Species diversity prevents rubber-stamping."*
