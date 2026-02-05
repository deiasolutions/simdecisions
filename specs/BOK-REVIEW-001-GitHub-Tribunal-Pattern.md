# BOK-REVIEW-001: GitHub Tribunal Pattern

**Pattern Name:** Three-Judge Code Review Tribunal
**Version:** 1.2.0
**Date:** 2026-02-05  
**Authors:** Dave (daaaave-atx) × Claude (Anthropic)  
**Status:** PROPOSED  
**Tags:** #BOK #Review #GitHub #Kaizen #BABOK #Tribunal #Q33N

---

## Abstract

This pattern establishes a **multi-vendor AI tribunal** for code review that operates natively within GitHub. Three Q33N judges (Gemini, Codex, Anthropic) independently evaluate every PR against structured INVEST-style criteria. Only submissions passing consensus threshold reach the human governor for final merge authority. The system embeds DMAIC continuous improvement and MUDA waste detection, enabling the review process itself to improve over time.

---

## 1. Pattern Overview

### 1.1 Problem Statement

Human code review doesn't scale. Every diff hitting the human's desk creates a bottleneck. But fully autonomous merge authority is unsafe. The system needs a **filter layer** that:

- Rejects clearly inadequate work before human review
- Provides structured, actionable feedback for iteration
- Surfaces only quality-passing submissions for final approval
- Generates data to improve agent performance over time

### 1.2 Solution

A three-judge tribunal where:

- **Three independent LLM judges** (vendor diversity) evaluate each PR
- **Structured criteria** (INVEST-adapted) ensure consistent evaluation
- **Embeddings** measure spec alignment and codebase fit
- **Moderation layer** (Llama Guard) catches safety issues
- **Consensus scoring** determines escalation to human
- **Kaizen feedback loop** improves the system continuously

### 1.3 Key Principle

> **The human reviews only what the tribunal approves. The tribunal learns from what the human accepts.**

---

## 2. Participants

### 2.1 Roles

| Role | Entity | Responsibility |
|------|--------|----------------|
| **Submitting Agent** | Any hive bee | Produces work, opens PR |
| **Judge (Gemini)** | Gemini Q33N | Independent evaluation |
| **Judge (Codex)** | Codex Q33N | Independent evaluation |
| **Judge (Anthropic)** | Anthropic Q33N | Independent evaluation |
| **Aggregator Bot** | System service | Tallies scores, manages labels, writes ledger |
| **Human Governor** | Dave | Final merge authority |

### 2.2 Vendor Diversity Requirement

No agent reviews its own work. Three vendors ensures:

- No single-vendor blind spots
- Checks and balances (rivalry as quality mechanism)
- Calibration data across model architectures
- Resilience if one vendor degrades

---

## 3. INVEST Criteria (Adapted for Code Review)

Each judge scores each criterion: **-1** (fail) / **0** (neutral) / **1** (pass)

### 3.1 Criteria Definitions

| Criterion | Question | Measurement Method |
|-----------|----------|-------------------|
| **I — Intent Aligned** | Does it solve the stated problem? | Embedding: spec ↔ submission cosine similarity |
| **N — Narrow Scope** | Is the diff focused and minimal? | Lines changed, files touched, unrelated changes detected |
| **V — Verifiable** | Can we prove it works? | Tests pass, coverage delta, verification steps provided |
| **E — Evident Quality** | Does it match codebase standards? | Embedding: neighborhood fit + lint/style check results |
| **S — Safe** | Does it avoid harm? | Llama Guard classifier + sensitive path detection |
| **T — Traceable** | Can we trace it to requirements? | Task ID linked, provenance chain intact |

### 3.2 Scoring Matrix

| Score | Meaning | Action |
|-------|---------|--------|
| **1** | Criterion clearly met | Positive signal |
| **0** | Ambiguous or minor issues | Neutral, note in comments |
| **-1** | Criterion failed | Negative signal, must explain why |

### 3.3 Consensus Threshold

- **Maximum possible:** 6 criteria × 3 judges × 1 point = **18 points**
- **Minimum to escalate:** **≥ 6 points** (configurable)
- **Auto-reject threshold:** **< 0 points** (net negative)
- **Disagreement flag:** Any criterion where judges span -1 to 1

---

## 4. GitHub Integration

### 4.1 Mapping to GitHub Constructs

| Tribunal Concept | GitHub Construct | Implementation |
|------------------|------------------|----------------|
| Submission | Pull Request | Agent opens PR against target branch |
| Task Reference | PR Title + Body | Format: `[TASK-XXX] Title` + spec link |
| Judge Verdict | GitHub Review | Approve / Request Changes / Comment |
| Criteria Results | GitHub Checks | One Check per criterion (pass/fail/neutral) |
| Judge Notes | Review Comments | Inline on diff + summary comment |
| Escalate to Human | PR Label | `ready-for-dave` label |
| Rejection | PR Label + Comment | `needs-work` label + feedback |
| Final Approval | Merge | Only human governor has merge rights |
| Kaizen Data | GitHub API | PR metrics extracted post-merge |

### 4.2 Branch Strategy

| Branch Pattern | Purpose | Protection |
|----------------|---------|------------|
| `main` | Production | Protected: only human merges |
| `develop` | Integration | Protected: tribunal must pass |
| `agent/{agent-id}/{task-id}` | Agent working branch | Unprotected |
| `review/{task-id}` | PR target for tribunal | Unprotected |

### 4.3 Label Taxonomy

| Label | Color | Meaning | Set By |
|-------|-------|---------|--------|
| `awaiting-tribunal` | Yellow | PR opened, judges not yet run | Automation |
| `under-review` | Blue | Judges currently evaluating | Automation |
| `needs-work` | Red | Rejected, feedback posted | Aggregator |
| `ready-for-dave` | Green | Passed tribunal, awaiting human | Aggregator |
| `disagreement` | Orange | Judges disagreed significantly | Aggregator |
| `approved` | Purple | Human approved, ready to merge | Human |

### 4.4 GitHub Checks (Displayed on PR)

| Check Name | Description |
|------------|-------------|
| `tribunal/intent-aligned` | Spec similarity score |
| `tribunal/narrow-scope` | Scope assessment |
| `tribunal/verifiable` | Test results |
| `tribunal/evident-quality` | Style/fit assessment |
| `tribunal/safe` | Moderation results |
| `tribunal/traceable` | Provenance check |
| `tribunal/consensus` | Aggregate score and verdict |

---

## 5. Workflow

### 5.1 Sequence Diagram

```
┌─────────────┐     ┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌──────┐
│   Agent     │     │ GitHub  │     │  Tribunal   │     │Aggregator│     │ Dave │
└──────┬──────┘     └────┬────┘     └──────┬──────┘     └────┬─────┘     └──┬───┘
       │                 │                 │                 │              │
       │  Push branch    │                 │                 │              │
       │────────────────>│                 │                 │              │
       │                 │                 │                 │              │
       │  Open PR        │                 │                 │              │
       │────────────────>│                 │                 │              │
       │                 │                 │                 │              │
       │                 │  Webhook: PR opened               │              │
       │                 │────────────────────────────────────>              │
       │                 │                 │                 │              │
       │                 │  Add label: awaiting-tribunal     │              │
       │                 │<────────────────────────────────────              │
       │                 │                 │                 │              │
       │                 │  Invoke judges (parallel)         │              │
       │                 │                 │<────────────────│              │
       │                 │                 │                 │              │
       │                 │  Gemini evaluates                 │              │
       │                 │<────────────────│                 │              │
       │                 │                 │                 │              │
       │                 │  Codex evaluates                  │              │
       │                 │<────────────────│                 │              │
       │                 │                 │                 │              │
       │                 │  Anthropic evaluates              │              │
       │                 │<────────────────│                 │              │
       │                 │                 │                 │              │
       │                 │  All reviews posted               │              │
       │                 │────────────────────────────────────>              │
       │                 │                 │                 │              │
       │                 │                 │  Aggregate scores              │
       │                 │                 │                 │───┐          │
       │                 │                 │                 │<──┘          │
       │                 │                 │                 │              │
       │                 │  [If threshold met]               │              │
       │                 │  Add label: ready-for-dave        │              │
       │                 │<────────────────────────────────────              │
       │                 │                 │                 │              │
       │                 │  [If rejected]                    │              │
       │                 │  Add label: needs-work            │              │
       │                 │  Post feedback comment            │              │
       │                 │<────────────────────────────────────              │
       │                 │                 │                 │              │
       │  [If rejected]  │                 │                 │              │
       │  Iterate & push │                 │                 │              │
       │────────────────>│                 │                 │              │
       │                 │                 │                 │              │
       │                 │  [If ready-for-dave]              │              │
       │                 │  Notification ─────────────────────────────────────>
       │                 │                 │                 │              │
       │                 │                 │                 │    Review PR │
       │                 │<─────────────────────────────────────────────────│
       │                 │                 │                 │              │
       │                 │                 │                 │       Merge  │
       │                 │<─────────────────────────────────────────────────│
       │                 │                 │                 │              │
       │                 │  Post-merge: write event ledger   │              │
       │                 │────────────────────────────────────>              │
       │                 │                 │                 │              │
```

### 5.2 GitHub Actions Workflow

```yaml
# .github/workflows/tribunal-review.yml

name: Tribunal Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - develop
      - main

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      pr_number: ${{ steps.pr.outputs.number }}
      task_id: ${{ steps.parse.outputs.task_id }}
      spec_content: ${{ steps.spec.outputs.content }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Get PR info
        id: pr
        run: echo "number=${{ github.event.pull_request.number }}" >> $GITHUB_OUTPUT
        
      - name: Parse task ID from title
        id: parse
        run: |
          TITLE="${{ github.event.pull_request.title }}"
          TASK_ID=$(echo "$TITLE" | grep -oP 'TASK-\d+' || echo "UNKNOWN")
          echo "task_id=$TASK_ID" >> $GITHUB_OUTPUT
          
      - name: Add awaiting-tribunal label
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ github.event.pull_request.number }},
              labels: ['awaiting-tribunal']
            });
            
      - name: Fetch task spec
        id: spec
        run: |
          TASK_ID="${{ steps.parse.outputs.task_id }}"
          # Fetch spec from task registry or file
          SPEC_FILE=".deia/hive/tasks/*/${TASK_ID}*.json"
          if [ -f $SPEC_FILE ]; then
            CONTENT=$(cat $SPEC_FILE | jq -c .)
            echo "content=$CONTENT" >> $GITHUB_OUTPUT
          else
            echo "content={}" >> $GITHUB_OUTPUT
          fi

  judge-gemini:
    needs: setup
    runs-on: ubuntu-latest
    outputs:
      scores: ${{ steps.evaluate.outputs.scores }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Get PR diff
        id: diff
        run: |
          gh pr diff ${{ needs.setup.outputs.pr_number }} > diff.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Evaluate with Gemini
        id: evaluate
        run: |
          python scripts/tribunal/judge.py \
            --provider gemini \
            --diff diff.txt \
            --spec '${{ needs.setup.outputs.spec_content }}' \
            --output scores.json
          echo "scores=$(cat scores.json)" >> $GITHUB_OUTPUT
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          
      - name: Post GitHub Review
        uses: actions/github-script@v7
        with:
          script: |
            const scores = JSON.parse('${{ steps.evaluate.outputs.scores }}');
            const event = scores.total >= 3 ? 'APPROVE' : 'REQUEST_CHANGES';
            await github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: ${{ needs.setup.outputs.pr_number }},
              event: event,
              body: `## Gemini Q33N Review\n\n${scores.summary}`
            });

  judge-codex:
    needs: setup
    runs-on: ubuntu-latest
    outputs:
      scores: ${{ steps.evaluate.outputs.scores }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Get PR diff
        id: diff
        run: |
          gh pr diff ${{ needs.setup.outputs.pr_number }} > diff.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Evaluate with Codex
        id: evaluate
        run: |
          python scripts/tribunal/judge.py \
            --provider codex \
            --diff diff.txt \
            --spec '${{ needs.setup.outputs.spec_content }}' \
            --output scores.json
          echo "scores=$(cat scores.json)" >> $GITHUB_OUTPUT
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          
      - name: Post GitHub Review
        uses: actions/github-script@v7
        with:
          script: |
            const scores = JSON.parse('${{ steps.evaluate.outputs.scores }}');
            const event = scores.total >= 3 ? 'APPROVE' : 'REQUEST_CHANGES';
            await github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: ${{ needs.setup.outputs.pr_number }},
              event: event,
              body: `## Codex Q33N Review\n\n${scores.summary}`
            });

  judge-anthropic:
    needs: setup
    runs-on: ubuntu-latest
    outputs:
      scores: ${{ steps.evaluate.outputs.scores }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Get PR diff
        id: diff
        run: |
          gh pr diff ${{ needs.setup.outputs.pr_number }} > diff.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Evaluate with Anthropic
        id: evaluate
        run: |
          python scripts/tribunal/judge.py \
            --provider anthropic \
            --diff diff.txt \
            --spec '${{ needs.setup.outputs.spec_content }}' \
            --output scores.json
          echo "scores=$(cat scores.json)" >> $GITHUB_OUTPUT
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          
      - name: Post GitHub Review
        uses: actions/github-script@v7
        with:
          script: |
            const scores = JSON.parse('${{ steps.evaluate.outputs.scores }}');
            const event = scores.total >= 3 ? 'APPROVE' : 'REQUEST_CHANGES';
            await github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: ${{ needs.setup.outputs.pr_number }},
              event: event,
              body: `## Anthropic Q33N Review\n\n${scores.summary}`
            });

  aggregate:
    needs: [setup, judge-gemini, judge-codex, judge-anthropic]
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Aggregate scores
        id: aggregate
        run: |
          python scripts/tribunal/aggregate.py \
            --gemini '${{ needs.judge-gemini.outputs.scores }}' \
            --codex '${{ needs.judge-codex.outputs.scores }}' \
            --anthropic '${{ needs.judge-anthropic.outputs.scores }}' \
            --output verdict.json
          echo "verdict=$(cat verdict.json)" >> $GITHUB_OUTPUT
          
      - name: Update labels based on verdict
        uses: actions/github-script@v7
        with:
          script: |
            const verdict = JSON.parse('${{ steps.aggregate.outputs.verdict }}');
            const prNumber = ${{ needs.setup.outputs.pr_number }};
            
            // Remove awaiting-tribunal
            await github.rest.issues.removeLabel({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              name: 'awaiting-tribunal'
            }).catch(() => {});
            
            if (verdict.threshold_met) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: prNumber,
                labels: ['ready-for-dave']
              });
            } else {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: prNumber,
                labels: ['needs-work']
              });
            }
            
            if (verdict.has_disagreement) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: prNumber,
                labels: ['disagreement']
              });
            }
            
      - name: Post consensus summary
        uses: actions/github-script@v7
        with:
          script: |
            const verdict = JSON.parse('${{ steps.aggregate.outputs.verdict }}');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: ${{ needs.setup.outputs.pr_number }},
              body: verdict.summary_comment
            });
            
      - name: Create Check runs for criteria
        uses: actions/github-script@v7
        with:
          script: |
            const verdict = JSON.parse('${{ steps.aggregate.outputs.verdict }}');
            for (const criterion of verdict.criteria) {
              await github.rest.checks.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                name: `tribunal/${criterion.name}`,
                head_sha: context.sha,
                status: 'completed',
                conclusion: criterion.passed ? 'success' : (criterion.neutral ? 'neutral' : 'failure'),
                output: {
                  title: criterion.title,
                  summary: criterion.summary
                }
              });
            }
            
      - name: Write Review Egg to event ledger
        run: |
          python scripts/tribunal/write_ledger.py \
            --verdict '${{ steps.aggregate.outputs.verdict }}' \
            --pr-number ${{ needs.setup.outputs.pr_number }} \
            --task-id ${{ needs.setup.outputs.task_id }}
```

---

## 6. Review Egg Schema

### 6.1 Full Schema

```yaml
# review_egg.yaml

schema_version: "1.0.0"
egg_type: "review"

# Identification
submission_id: "SUB-2026-02-04-001"
pr_number: 42
pr_url: "https://github.com/owner/repo/pull/42"
task_ref: "TASK-009"
task_spec_url: "https://github.com/owner/repo/blob/main/.deia/specs/TASK-009.md"

# Timestamps
created_at: "2026-02-04T14:23:17Z"
tribunal_started_at: "2026-02-04T14:23:45Z"
tribunal_completed_at: "2026-02-04T14:27:12Z"
human_reviewed_at: null  # Populated when Dave reviews
merged_at: null  # Populated on merge

# Submitting Agent
submitter:
  entity_id: "agent:BEE-001"
  provider: "anthropic"
  model: "claude-sonnet-4-20250514"

# Judge Evaluations
judges:
  gemini:
    entity_id: "agent:Q33N-GEMINI"
    model: "gemini-2.0-pro"
    evaluated_at: "2026-02-04T14:25:03Z"
    criteria:
      intent_aligned:
        score: 1
        reasoning: "Diff implements event ledger schema as specified in ADR-001"
        evidence: ["Creates events table", "All required columns present"]
      narrow_scope:
        score: 0
        reasoning: "Includes minor formatting changes to unrelated files"
        evidence: ["utils.py whitespace changes"]
      verifiable:
        score: 1
        reasoning: "Tests added and passing"
        evidence: ["test_ledger.py added", "coverage +4.2%"]
      evident_quality:
        score: 1
        reasoning: "Matches existing codebase patterns"
        evidence: ["Embedding similarity: 0.94"]
      safe:
        score: 1
        reasoning: "No sensitive paths, moderation clean"
        evidence: ["Llama Guard: PASS"]
      traceable:
        score: 1
        reasoning: "PR title links TASK-009, spec referenced in body"
        evidence: ["Title: '[TASK-009] Event Ledger v1'"]
    total: 5
    verdict: "APPROVE"
    summary: |
      Strong submission. Implements spec accurately with good test coverage.
      Minor scope creep (formatting changes) noted but not blocking.

  codex:
    entity_id: "agent:Q33N-CODEX"
    model: "gpt-4o"
    evaluated_at: "2026-02-04T14:25:47Z"
    criteria:
      intent_aligned:
        score: 1
        reasoning: "Schema matches ADR-001 specification"
        evidence: ["All 14 columns present", "Indexes created"]
      narrow_scope:
        score: -1
        reasoning: "Touched 3 files outside ledger scope"
        evidence: ["utils.py", "config.py", "__init__.py"]
      verifiable:
        score: 1
        reasoning: "Comprehensive tests"
        evidence: ["8 test cases", "Happy path + edge cases"]
      evident_quality:
        score: 0
        reasoning: "Style differs slightly from existing modules"
        evidence: ["Uses dataclasses where existing code uses dicts"]
      safe:
        score: 1
        reasoning: "Clean"
        evidence: ["No flags"]
      traceable:
        score: 1
        reasoning: "Properly linked"
        evidence: ["Task ID in title"]
    total: 3
    verdict: "REQUEST_CHANGES"
    summary: |
      Core implementation is solid but scope includes unrelated changes.
      Recommend reverting utils.py and config.py modifications.

  anthropic:
    entity_id: "agent:Q33N-ANTHROPIC"
    model: "claude-sonnet-4-20250514"
    evaluated_at: "2026-02-04T14:26:22Z"
    criteria:
      intent_aligned:
        score: 1
        reasoning: "Faithful implementation of ADR-001"
        evidence: ["Schema exactly matches spec"]
      narrow_scope:
        score: 0
        reasoning: "Some tangential changes, but justified in commit message"
        evidence: ["Commit explains config.py change needed for db path"]
      verifiable:
        score: 1
        reasoning: "Tests cover all public functions"
        evidence: ["100% coverage on ledger.py"]
      evident_quality:
        score: 1
        reasoning: "Clean, well-documented code"
        evidence: ["Docstrings present", "Type hints (optional but nice)"]
      safe:
        score: 1
        reasoning: "No issues"
        evidence: ["Moderation: PASS"]
      traceable:
        score: 1
        reasoning: "Full provenance"
        evidence: ["Links to ADR-001, TASK-009, architecture session doc"]
    total: 5
    verdict: "APPROVE"
    summary: |
      Excellent submission. Scope discussion is valid but changes are 
      justified. Ready for human review.

# Consensus Analysis
consensus:
  total_score: 13
  max_possible: 18
  threshold: 6
  threshold_met: true
  
  by_criterion:
    intent_aligned:
      scores: [1, 1, 1]
      consensus: "unanimous_pass"
    narrow_scope:
      scores: [0, -1, 0]
      consensus: "disagreement"
      note: "Codex flagged scope creep; others accepted with notes"
    verifiable:
      scores: [1, 1, 1]
      consensus: "unanimous_pass"
    evident_quality:
      scores: [1, 0, 1]
      consensus: "majority_pass"
    safe:
      scores: [1, 1, 1]
      consensus: "unanimous_pass"
    traceable:
      scores: [1, 1, 1]
      consensus: "unanimous_pass"
      
  disagreements:
    - criterion: "narrow_scope"
      range: [-1, 0]
      discussion: "Codex strict on scope; Gemini/Anthropic accepted justification"
      
  verdict: "ESCALATE_TO_HUMAN"
  verdict_reason: "Threshold met (13 >= 6) with one disagreement flagged"

# Embeddings Analysis
embeddings:
  spec_similarity: 0.87
  neighborhood_fit: 0.92
  model_used: "voyage-code-2"
  
  spec_comparison:
    high_alignment: ["schema definition", "index creation", "timestamp handling"]
    low_alignment: ["config.py changes not in spec"]
    
  codebase_comparison:
    style_match: 0.89
    pattern_match: 0.94
    anomalies: ["dataclass usage differs from existing dict pattern"]

# Moderation
moderation:
  llama_guard:
    version: "2.0"
    result: "PASS"
    categories_checked: ["harmful_code", "data_exfiltration", "prompt_injection"]
    flags: []
    
  sensitive_paths:
    checked: true
    paths_touched: ["runtime/ledger.py", "runtime/__init__.py", "config.py"]
    sensitive_paths_touched: []
    risk_level: "LOW"

# Kaizen Metrics
kaizen:
  iteration_count: 1
  previous_submissions: []
  
  timing:
    time_to_first_review: "00:03:28"
    total_tribunal_duration: "00:03:27"
    
  quality_signals:
    test_coverage_delta: "+4.2%"
    lint_errors_delta: 0
    complexity_delta: "+12"  # Cyclomatic complexity added
    
  agent_performance:
    submitter_historical_approval_rate: 0.78
    submitter_domain_strength: 0.85  # σ_backend for BEE-001

# Final Disposition (populated post-review)
disposition:
  human_verdict: null  # "APPROVED" | "CHANGES_REQUESTED" | "REJECTED"
  human_notes: null
  merged: false
  merge_commit: null
```

### 6.2 Event Ledger Entry

When the Review Egg is finalized, write to event ledger:

```json
{
  "event_type": "review_completed",
  "actor": "system:tribunal",
  "target": "pr:42",
  "domain": "review",
  "signal_type": "gravity",
  "oracle_tier": 3,
  "payload_json": "{...review_egg_json...}",
  "cost_tokens": 12847,
  "cost_usd": 0.19,
  "cost_carbon": null
}
```

---

## 7. DMAIC Continuous Improvement

### 7.1 Per-Submission Cycle

| Phase | Action | Output |
|-------|--------|--------|
| **Define** | Parse task spec, identify acceptance criteria | Structured spec object |
| **Measure** | Three judges score six criteria | 18 data points |
| **Analyze** | Identify disagreements, compute consensus | Verdict + flags |
| **Improve** | Generate feedback for rejected submissions | Actionable comments |
| **Control** | Human final review, merge decision | Disposition recorded |

### 7.2 Aggregate Cycle (Weekly Kaizen)

| Phase | Analysis | Action |
|-------|----------|--------|
| **Define** | What types of work are we reviewing? | Categorize by domain, agent, complexity |
| **Measure** | Aggregate scores across all PRs | Distributions, trends |
| **Analyze** | Which criteria fail most? Which judges disagree? | Root cause identification |
| **Improve** | Update prompts, specs, agent training | Targeted improvements |
| **Control** | Track improvement over time | Kaizen dashboard |

### 7.3 Kaizen Metrics Dashboard

| Metric | Formula | Target |
|--------|---------|--------|
| **First-Pass Approval Rate** | PRs approved on first submission / Total PRs | ↑ over time |
| **Mean Iterations to Approval** | Avg submissions before merge | ↓ toward 1.0 |
| **Judge Agreement Rate** | Unanimous decisions / Total decisions | ↑ (calibration) |
| **Criterion Failure Distribution** | Failures per criterion | Even spread |
| **Agent Quality by Domain** | Approval rate per agent per domain | Identify specialization |
| **Queue Depth** | PRs awaiting review | ↓ (flow) |
| **Cycle Time** | PR open to merge duration | ↓ (efficiency) |
| **Human Override Rate** | Human disagrees with tribunal / Total | Monitor (too high = tribunal miscalibrated) |

---

## 8. MUDA Waste Identification

### 8.1 Seven Wastes in Code Review Context

| Waste | In Review Context | Detection Method | Mitigation |
|-------|-------------------|------------------|------------|
| **Defects** | Submissions that fail criteria | Rejection rate | Better specs, agent training |
| **Overproduction** | Work done beyond spec | Scope creep flag | Tighter task definitions |
| **Waiting** | PRs stuck in queue | Time-to-review metric | Parallelize judges, auto-trigger |
| **Non-utilized talent** | Wrong agent for task | σ mismatch detection | Better task routing |
| **Transportation** | Unnecessary handoffs | Iteration count | Clearer feedback, better first pass |
| **Inventory** | Backlog of unreviewed PRs | Queue depth | Capacity management |
| **Motion** | Context switching, rework | Rejection → resubmit cycles | Comprehensive first review |
| **Extra processing** | Over-engineering | Diff size vs spec complexity | Scope boundaries |

### 8.2 Waste Signals in Review Egg

```yaml
muda_signals:
  defects:
    indicator: "rejection_count > 0"
    value: 0
    
  overproduction:
    indicator: "files_changed outside spec scope"
    value: 2
    files: ["utils.py", "config.py"]
    
  waiting:
    indicator: "time_in_queue > 1 hour"
    value: false
    
  non_utilized_talent:
    indicator: "agent σ_domain < 0.7"
    value: false
    agent_strength: 0.85
    
  transportation:
    indicator: "iteration_count > 2"
    value: false
    
  inventory:
    indicator: "queue_depth > 10"
    value: false
    current_depth: 3
    
  motion:
    indicator: "feedback_items > 5"
    value: false
    feedback_count: 2
    
  extra_processing:
    indicator: "diff_lines / spec_complexity > threshold"
    value: false
    ratio: 0.8
```

---

## 9. Embeddings Integration

### 9.1 Embedding Types

| Embedding | Source | Purpose |
|-----------|--------|---------|
| **Spec Embedding** | Task specification text | "What was asked?" |
| **Submission Embedding** | PR diff content | "What was built?" |
| **Neighborhood Embedding** | Files being modified | "What exists?" |

### 9.2 Similarity Computations

```python
# Spec Alignment
spec_similarity = cosine_similarity(
    embed(task_spec),
    embed(pr_diff)
)
# High = submission matches spec
# Low = spec drift, flag for review

# Codebase Fit
neighborhood_fit = cosine_similarity(
    embed(existing_file_content),
    embed(new_code_in_diff)
)
# High = matches existing patterns
# Low = stylistic anomaly, may be intentional or drift
```

### 9.3 Embedding Model

- **Recommended:** Voyage Code 2 (optimized for code)
- **Fallback:** OpenAI text-embedding-3-large
- **Local option:** CodeBERT for air-gapped environments

---

## 10. Moderation Layer

### 10.1 Llama Guard Integration

```python
def check_moderation(diff_content: str) -> ModerationResult:
    """
    Run Llama Guard classifier on diff content.
    
    Categories checked:
    - harmful_code: Malware patterns, exploits
    - data_exfiltration: Suspicious data handling
    - prompt_injection: Attempts to manipulate LLM judges
    - credential_exposure: Hardcoded secrets
    """
    response = llama_guard.classify(diff_content)
    return ModerationResult(
        passed=response.is_safe,
        categories_flagged=response.flagged_categories,
        confidence=response.confidence
    )
```

### 10.2 Sensitive Path Detection

```yaml
sensitive_paths:
  high_risk:
    - "auth/*"
    - "security/*"
    - "payments/*"
    - "*.key"
    - "*.pem"
    - ".env*"
    
  medium_risk:
    - "config/*"
    - "migrations/*"
    - "deploy/*"
    
  rules:
    - path_pattern: "auth/*"
      requires: "explicit human approval"
    - path_pattern: "*.key"
      action: "block and alert"
```

---

## 11. Discord Integration

### 11.1 Notification Flow

| Event | Discord Channel | Message |
|-------|-----------------|---------|
| PR opened | #tribunal-queue | "New submission from BEE-001: [TASK-009] Event Ledger" |
| Tribunal complete (pass) | #ready-for-review | "@dave PR #42 passed tribunal (13/18). [Review](link)" |
| Tribunal complete (fail) | #needs-work | "PR #42 rejected. Feedback posted. @BEE-001" |
| Human approved | #announcements | "✅ TASK-009 merged. Event ledger shipped." |
| Disagreement flagged | #tribunal-discussion | "⚠️ Judges disagreed on PR #42 scope. [Details](link)" |

### 11.2 Bot Commands

| Command | Action |
|---------|--------|
| `!queue` | List PRs awaiting tribunal |
| `!ready` | List PRs ready for Dave |
| `!stats week` | Kaizen metrics for past week |
| `!judge-calibration` | Agreement rate by judge pair |

---

## 12. Implementation Checklist

### Phase 1: Foundation
- [ ] GitHub Actions workflow (tribunal-review.yml)
- [ ] Judge invocation script (scripts/tribunal/judge.py)
- [ ] Aggregation script (scripts/tribunal/aggregate.py)
- [ ] Review Egg schema validation
- [ ] Label management automation

### Phase 2: Intelligence
- [ ] Embedding computation (spec, submission, neighborhood)
- [ ] Llama Guard integration
- [ ] Sensitive path detection
- [ ] σ (strength) lookup for submitting agent

### Phase 3: Observability
- [ ] Event ledger integration
- [ ] Kaizen metrics collection
- [ ] MUDA signal detection
- [ ] Dashboard (weekly stats)

### Phase 4: Communication
- [ ] Discord bot notifications
- [ ] Discord bot commands
- [ ] Human notification preferences

### Phase 5: Calibration
- [ ] Judge prompt tuning based on agreement data
- [ ] Threshold adjustment based on human override rate
- [ ] Criterion weight adjustment based on failure distribution

---

## 13. Configuration

### 13.1 Thresholds (Adjustable)

```yaml
# tribunal-config.yml

thresholds:
  consensus_minimum: 6          # Minimum score to escalate
  auto_reject_below: 0          # Auto-reject if net negative
  disagreement_range: 2         # Flag if judge scores span this range
  
timing:
  judge_timeout_seconds: 120    # Max time per judge
  total_timeout_seconds: 300    # Max time for full tribunal
  
embeddings:
  spec_similarity_warn: 0.7     # Flag if below
  neighborhood_fit_warn: 0.8    # Flag if below
  
moderation:
  block_on_any_flag: true       # Block PR if any moderation flag
  
kaizen:
  weekly_report_day: "monday"
  metrics_retention_days: 90
```

### 13.2 Judge Prompts

```yaml
# judges/anthropic.yml

system_prompt: |
  You are a code reviewer on the DEIA SimDecisions project tribunal.
  
  Your role is to evaluate Pull Requests against structured INVEST criteria.
  
  ## Criteria (score each -1, 0, or 1)
  
  - **Intent Aligned (I)**: Does the diff implement what the task spec requested?
  - **Narrow Scope (N)**: Is the diff focused? Are there unrelated changes?
  - **Verifiable (V)**: Are there tests? Do they pass? Is coverage adequate?
  - **Evident Quality (E)**: Does the code match existing patterns and style?
  - **Safe (S)**: Are there any security concerns, sensitive data issues?
  - **Traceable (T)**: Is the PR linked to a task? Is provenance clear?
  
  ## Output Format
  
  Respond with JSON matching the judge evaluation schema.
  Provide specific evidence for each score.
  Be constructive in feedback for any non-passing scores.
  
  ## Philosophy
  
  Review with the Protocol of Grace: pause, listen, reflect, respond, rejoin.
  Your goal is quality, not gatekeeping. Help the agent improve.
```

---

## 14. Future Extensions

### 14.1 Learning Loop

- Train lightweight classifier on human override patterns
- Auto-adjust judge prompts based on calibration drift
- Predict which submissions will need human attention

### 14.2 Cross-Repository

- Tribunal serves multiple repos with shared config
- Centralized kaizen dashboard across projects

### 14.3 Agent Coaching

- Track agent performance by criterion over time
- Generate personalized improvement suggestions
- "BEE-001: Your narrow_scope scores are 20% below average. Consider..."

---

## 15. Author-Conditional Workflow

### 15.1 Rationale

The human governor (Dave) is trusted but still benefits from tribunal feedback. Other authors require human approval after tribunal pass. This creates two paths through the same review system.

### 15.2 Workflow by Author Type

#### If Author ≠ Dave (Bee or external contributor)

```
PR opened
    │
    ▼
Tribunal runs (3 Q33N judges)
    │
    ├─── PASS (score ≥ 6/18) ──────────┐
    │                                   ▼
    │                          Label: ready-for-dave
    │                          Notify Dave
    │                                   │
    │                                   ▼
    │                          Dave reviews
    │                                   │
    │                          ┌───────┴───────┐
    │                          ▼               ▼
    │                       Approve         Request changes
    │                          │               │
    │                          ▼               ▼
    │                       MERGE          Back to author
    │
    └─── FAIL (score < 6/18) ──────────┐
                                        ▼
                               Label: needs-work
                               Post feedback
                               Author iterates
```

#### If Author = Dave (Human Governor)

```
PR opened
    │
    ▼
Tribunal runs (3 Q33N judges)
    │
    ├─── PASS (score ≥ 6/18) ──────────┐
    │                                   ▼
    │                          AUTO-MERGE
    │                          (No second human review needed)
    │
    └─── FAIL (score < 6/18) ──────────┐
                                        ▼
                               Label: needs-work
                               Post feedback to Dave
                               Dave iterates or overrides
```

### 15.3 GitHub Actions Implementation

```yaml
# In tribunal-review.yml aggregate job

- name: Determine merge path
  id: merge_path
  run: |
    AUTHOR="${{ github.event.pull_request.user.login }}"
    GOVERNOR="deiasolutions"  # Dave's GitHub username

    if [ "$AUTHOR" == "$GOVERNOR" ]; then
      echo "path=auto-merge" >> $GITHUB_OUTPUT
    else
      echo "path=require-approval" >> $GITHUB_OUTPUT
    fi

- name: Handle tribunal pass
  if: steps.aggregate.outputs.threshold_met == 'true'
  uses: actions/github-script@v7
  with:
    script: |
      const path = '${{ steps.merge_path.outputs.path }}';
      const prNumber = ${{ github.event.pull_request.number }};

      if (path === 'auto-merge') {
        // Dave's PR - auto-merge
        await github.rest.pulls.merge({
          owner: context.repo.owner,
          repo: context.repo.repo,
          pull_number: prNumber,
          merge_method: 'squash'
        });

        await github.rest.issues.createComment({
          owner: context.repo.owner,
          repo: context.repo.repo,
          issue_number: prNumber,
          body: '✅ Tribunal passed. Auto-merged (governor submission).'
        });
      } else {
        // Bee PR - require Dave's approval
        await github.rest.issues.addLabels({
          owner: context.repo.owner,
          repo: context.repo.repo,
          issue_number: prNumber,
          labels: ['ready-for-dave']
        });

        await github.rest.issues.createComment({
          owner: context.repo.owner,
          repo: context.repo.repo,
          issue_number: prNumber,
          body: '⚖️ Tribunal passed. Awaiting @deiasolutions approval.'
        });
      }
```

### 15.4 Branch Protection Settings

```yaml
# For main branch:

protection_rules:
  required_status_checks:
    strict: true
    contexts:
      - "tribunal/consensus"

  required_pull_request_reviews:
    # This is bypassed for Dave via auto-merge in Actions
    # But enforced for others via the label workflow
    dismiss_stale_reviews: true
    require_code_owner_reviews: false
    required_approving_review_count: 0  # Actions handles this conditionally

  restrictions:
    users: ["deiasolutions"]  # Only Dave can push directly (emergency)
    teams: []
```

### 15.5 Override Mechanism

Dave can override a tribunal rejection:

```
/tribunal override <reason>
```

This:
1. Logs the override to event ledger
2. Adds `governor-override` label
3. Enables merge despite failing score
4. Feeds back to tribunal calibration

Override events are tracked for kaizen analysis — frequent overrides indicate tribunal miscalibration.

---

## 16. Spec Feedback & Joint Prioritization

### 16.1 Purpose

Beyond evaluating whether a submission meets criteria, judges can provide **priority feedback** on the spec itself. This enables:

- Specs to improve based on multi-vendor perspective
- Ambiguities surfaced during review to be resolved
- Feedback aggregated and jointly prioritized by tribunal

### 16.2 Judge Feedback Structure

Each judge may optionally include spec feedback in their review:

```yaml
spec_feedback:
  - id: "FB-001"
    spec_ref: "ADR-006"           # Which spec
    section: "4.2"                 # Which section (optional)
    priority: "high"               # high | medium | low
    category: "ambiguity"          # ambiguity | gap | conflict | improvement
    summary: "Sync frequency undefined for conflict scenarios"
    detail: |
      The spec states 5s sync but doesn't clarify behavior when
      both API and file write occur within the same 5s window.
    suggested_change: |
      Add conflict resolution timing: "If both sources change within
      sync window, API write takes precedence with file write logged
      as conflict."
```

### 16.3 Feedback Categories

| Category | Description | Example |
|----------|-------------|---------|
| **ambiguity** | Spec language unclear or open to interpretation | "Does 'near real-time' mean <1s or <5s?" |
| **gap** | Missing information needed for implementation | "No error handling specified for webhook failures" |
| **conflict** | Spec contradicts another spec or itself | "ADR-006 says X, but ADR-004 says Y" |
| **improvement** | Enhancement suggestion | "Consider adding rate limit headers to API responses" |

### 16.4 Joint Prioritization Process

After individual judge reviews, feedback items are **jointly prioritized**:

```
┌─────────────────────────────────────────────────────────────┐
│                JOINT PRIORITIZATION                          │
│                                                              │
│  1. Collect: Aggregator gathers all spec_feedback items     │
│                                                              │
│  2. Dedupe: Merge similar feedback (semantic matching)      │
│                                                              │
│  3. Vote: Each judge votes on priority (async)              │
│     ┌─────────┬─────────┬─────────┐                         │
│     │ Gemini  │ Codex   │Anthropic│                         │
│     │  high   │  high   │  medium │ → Consensus: HIGH       │
│     └─────────┴─────────┴─────────┘                         │
│                                                              │
│  4. Rank: Feedback sorted by consensus priority             │
│                                                              │
│  5. Report: Prioritized list sent to human + spec owner     │
└─────────────────────────────────────────────────────────────┘
```

### 16.5 Priority Consensus Rules

| Scenario | Consensus Priority |
|----------|-------------------|
| All judges agree | That priority |
| 2 high, 1 medium | High |
| 2 medium, 1 low | Medium |
| 1 high, 1 medium, 1 low | Medium (escalate to human) |
| Any judge marks "critical" | Critical (immediate human attention) |

### 16.6 Feedback Output Schema

```yaml
spec_feedback_report:
  submission_ref: "PR-042"
  generated_at: "2026-02-05T10:30:00Z"

  items:
    - id: "FB-001"
      spec_ref: "ADR-006"
      category: "ambiguity"
      summary: "Sync frequency undefined for conflict scenarios"

      judge_votes:
        gemini: "high"
        codex: "high"
        anthropic: "medium"

      consensus_priority: "high"

      raised_by: ["gemini", "codex"]  # Who originally flagged

      suggested_changes:
        - source: "gemini"
          text: "Add explicit conflict timing rules"
        - source: "codex"
          text: "Define precedence: API > file"

    - id: "FB-002"
      spec_ref: "ADR-006"
      category: "gap"
      summary: "No retry policy for webhook delivery"
      consensus_priority: "medium"
      # ...

  summary:
    total_items: 5
    by_priority:
      critical: 0
      high: 2
      medium: 2
      low: 1
    by_category:
      ambiguity: 2
      gap: 2
      improvement: 1
```

### 16.7 Feedback Lifecycle

```
Feedback raised → Joint prioritization → Report generated
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
                   ┌─────────┐          ┌─────────┐          ┌─────────┐
                   │ Accept  │          │ Defer   │          │ Reject  │
                   │ → Task  │          │ → Backlog│         │ → Close │
                   └─────────┘          └─────────┘          └─────────┘
                        │
                        ▼
                   Spec updated → Tribunal notified → Calibration signal
```

### 16.8 Integration with Review Egg

Add to the Review Egg schema (Section 6):

```yaml
# Inside review_egg.judges[].review
spec_feedback:
  - id: string
    spec_ref: string
    section: string (optional)
    priority: enum [critical, high, medium, low]
    category: enum [ambiguity, gap, conflict, improvement]
    summary: string
    detail: string (optional)
    suggested_change: string (optional)
```

### 16.9 Aggregator Responsibilities

The aggregator bot must:

1. Extract `spec_feedback` from each judge's review
2. Deduplicate using semantic similarity (>0.85 cosine = same feedback)
3. Trigger joint prioritization vote (async, 1-hour timeout)
4. Generate `spec_feedback_report`
5. Post report to:
   - PR comments (summary)
   - G-Drive (full report)
   - Discord #spec-feedback channel
6. Create tasks for accepted high-priority items

### 16.10 Human Governor Actions

| Action | Effect |
|--------|--------|
| **Accept** | Creates task to update spec, assigns owner |
| **Defer** | Adds to spec backlog with priority |
| **Reject** | Closes with reason, feeds back to judges |
| **Merge** | Combines multiple feedback items into one task |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Tribunal** | Three-judge review panel for code submissions |
| **Review Egg** | Structured output of tribunal evaluation |
| **INVEST** | Criteria framework (Intent, Narrow, Verifiable, Evident, Safe, Traceable) |
| **Consensus** | Aggregate score across all judges and criteria |
| **Disagreement** | Criterion where judges scored across full range (-1 to 1) |
| **Escalate** | Pass submission to human governor for final review |
| **Kaizen** | Continuous improvement through measurement |
| **MUDA** | Waste categories to identify and eliminate |

---

## Appendix B: Related Documents

- ADR-001: Event Ledger Foundation
- BOK-SIM-001: Oort Cloud Partitioning
- BOK-SIM-002: Prophecy Engine
- DEIA Federalist No. 2: On Queens and Tyranny
- DEIA Federalist No. 6: On the Nature of Dissent
- DEIA Federalist No. 7: On the Protocol of Grace

---

*"The human reviews only what the tribunal approves. The tribunal learns from what the human accepts."*

**— BOK-REVIEW-001 v1.2.0**

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-02-05 | Added Section 16: Spec Feedback & Joint Prioritization (judges provide spec feedback, tribunal jointly prioritizes) |
| 1.1.0 | 2026-02-04 | Added Section 15: Author-Conditional Workflow (auto-merge for Dave, require approval for others) |
| 1.0.0 | 2026-02-04 | Initial spec |
