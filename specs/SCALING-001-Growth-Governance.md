# SCALING-001: Growth & Governance Scaling Roadmap

**Status:** ROADMAP (implement when needed)
**Date:** 2026-02-04
**Author:** Q33N (Dave) + BEE-001

---

## Purpose

This document captures scaling strategies to implement **when the project grows**. These are not needed now but are designed and ready.

**Principle:** Start simple, add complexity only when the pain justifies it.

---

## Current State (1-2 Contributors)

```
main (protected)
  │
  └── PRs from bees/contributors
          │
          ▼
      Tribunal (3 Q33N judges)
          │
          ├── Pass + Author=Dave → Auto-merge
          └── Pass + Author≠Dave → Dave approves → Merge
```

**Works for:** Solo development with automated bees.

---

## Scaling Trigger Points

| Trigger | Symptom | Action |
|---------|---------|--------|
| 5+ active contributors | PR review backlog | Add CODEOWNERS |
| Dave is bottleneck | PRs waiting days for review | Add maintainer pool |
| Need stable releases | Users need reliability | Add `develop` branch |
| 20+ PRs/week | Can't review everything | Tiered review |
| Multiple teams | Coordination overhead | Team-based CODEOWNERS |

---

## Level 1: Add CODEOWNERS (5+ Contributors)

### When to Implement

- Multiple people contributing regularly
- Dave can't review everything
- Different people have expertise in different areas

### Implementation

Create `.github/CODEOWNERS`:

```
# Default: Dave approves everything
* @deiasolutions

# Delegate specific areas to trusted maintainers
/core/           @alice @deiasolutions
/runtime/        @alice @deiasolutions
/docs/           @bob
/specs/          @deiasolutions
/tests/          @charlie @alice
/.github/        @deiasolutions
```

### Resulting Flow

```
PR touches /core/ → Tribunal → Alice OR Dave approves → Merge
PR touches /docs/ → Tribunal → Bob approves → Merge
PR touches /specs/ → Tribunal → Dave approves → Merge
```

### Branch Protection Update

```yaml
required_pull_request_reviews:
  require_code_owner_reviews: true
  required_approving_review_count: 1
```

---

## Level 2: Maintainer Pool (Dave as Bottleneck)

### When to Implement

- PRs sitting for days waiting for Dave
- Dave wants to step back from daily review
- Trusted maintainers have proven track record

### Implementation

Create maintainer team in GitHub:

```
Team: @simdecisions/maintainers
Members: @alice, @bob, @charlie
```

Update CODEOWNERS:

```
# Maintainer team can approve most things
* @simdecisions/maintainers

# Critical paths still require Dave
/specs/ADR-*     @deiasolutions
/.github/        @deiasolutions
/core/security/  @deiasolutions
```

### Resulting Flow

```
PR (normal) → Tribunal → Any maintainer approves → Merge
PR (critical) → Tribunal → Dave approves → Merge
```

---

## Level 3: Add `develop` Branch (Releases Matter)

### When to Implement

- Users depend on stable releases
- Need to batch changes before release
- Want release notes and versioning

### Implementation

```
main (releases only)
  ↑
  │ Release PR (maintainer merges, tagged)
  │
develop (integration)
  ↑
  │ Normal PRs merge here
  │
feature branches
```

### Branch Protection

**`main`:**
- Only maintainers can merge
- Requires release checklist
- Tagged with version

**`develop`:**
- Tribunal required
- CODEOWNER approval required
- Default PR target

### Release Process

1. Maintainer creates PR: `develop` → `main`
2. Release checklist completed
3. Merge creates release tag
4. Automated release notes

---

## Level 4: Tiered Review (High Volume)

### When to Implement

- 20+ PRs per week
- Tribunal catching most issues
- Human review is rubber-stamp for passing PRs

### Implementation

```yaml
# Tiered review rules

tier_1_auto_merge:
  # Auto-merge if ALL conditions met
  conditions:
    - tribunal_score >= 15  # High confidence
    - files_changed <= 5
    - no_sensitive_paths
    - author_trust_score >= 0.9

tier_2_single_maintainer:
  # One maintainer approval
  conditions:
    - tribunal_score >= 6
    - no_critical_paths

tier_3_dave_required:
  # Dave must approve
  conditions:
    - critical_paths_touched
    - OR tribunal_score < 6
    - OR author_trust_score < 0.5
```

### Trust Scores

Build trust scores from history:

```python
author_trust_score = (
    approved_prs / total_prs * 0.5 +
    first_pass_approval_rate * 0.3 +
    average_tribunal_score / 18 * 0.2
)
```

High-trust authors get faster path to merge.

---

## Level 5: Team-Based CODEOWNERS (Multiple Teams)

### When to Implement

- Distinct teams working on different areas
- Teams want autonomy over their domain
- Cross-team coordination needed

### Implementation

```
# .github/CODEOWNERS

# Core team owns runtime
/core/     @simdecisions/core-team
/runtime/  @simdecisions/core-team

# Platform team owns infrastructure
/.github/  @simdecisions/platform-team
/deploy/   @simdecisions/platform-team

# Docs team owns documentation
/docs/     @simdecisions/docs-team
/specs/    @simdecisions/docs-team @deiasolutions

# Security team must approve security-sensitive changes
/core/auth/     @simdecisions/security-team
/core/crypto/   @simdecisions/security-team
```

### Team Leads

Each team has a lead who can:
- Approve PRs in their domain
- Add/remove team members
- Escalate to Dave when needed

---

## Implementation Checklist

### Level 1: CODEOWNERS
- [ ] Create `.github/CODEOWNERS` file
- [ ] Identify trusted contributors for each area
- [ ] Update branch protection rules
- [ ] Document in CONTRIBUTING.md

### Level 2: Maintainer Pool
- [ ] Create GitHub team
- [ ] Add trusted maintainers
- [ ] Update CODEOWNERS to use team
- [ ] Define critical paths that still need Dave

### Level 3: Develop Branch
- [ ] Create `develop` branch
- [ ] Set `develop` as default PR target
- [ ] Create release PR template
- [ ] Set up release tagging automation

### Level 4: Tiered Review
- [ ] Implement trust scoring
- [ ] Define tier thresholds
- [ ] Update tribunal to output tier recommendation
- [ ] Create auto-merge rules

### Level 5: Team-Based
- [ ] Create team structure
- [ ] Assign team leads
- [ ] Update CODEOWNERS
- [ ] Create team onboarding docs

---

## Not Implementing (And Why)

| Pattern | Why Not |
|---------|---------|
| Gitflow (release/hotfix branches) | Overkill, develop + main is enough |
| Required 2+ approvals everywhere | Slows everything, tribunal is the gate |
| Commit signing required | Friction for new contributors |
| Forking-only (no direct branches) | Bees need branches in main repo |

---

*"Add governance when the pain demands it, not before."*
