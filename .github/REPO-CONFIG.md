# Repository Configuration

**Last Updated:** 2026-02-05
**Maintainer:** @deiasolutions (Dave)

---

## Repository

| Setting | Value |
|---------|-------|
| **URL** | https://github.com/deiasolutions/simdecisions |
| **Visibility** | Public |
| **Default Branch** | `main` |
| **License** | TBD |

---

## Branch Protection: `main`

Branch protection is enabled with the following rules:

| Rule | Setting |
|------|---------|
| Require pull request before merging | Yes |
| Required approving reviews | 0 (tribunal provides review) |
| Dismiss stale reviews | Yes |
| Require review from CODEOWNERS | No (Level 0 - not yet implemented) |
| Require status checks | No (tribunal GitHub Actions pending) |
| Require linear history | No |
| Allow force pushes | No |
| Allow deletions | No |
| Enforce for admins | No (admins can bypass when needed) |

---

## Contribution Workflow

### Current State (Level 0)

```
Contributor creates PR
        │
        ▼
   Tribunal Review (3 Q33N judges)
        │
        ├── Author = Dave + Pass → Auto-merge
        └── Author ≠ Dave + Pass → Dave approves → Merge
```

See: `specs/BOK-REVIEW-001-GitHub-Tribunal-Pattern.md` Section 15

### Future Scaling

| Trigger | Action | Reference |
|---------|--------|-----------|
| 5+ contributors | Add CODEOWNERS | SCALING-001 Level 1 |
| Dave is bottleneck | Add maintainer pool | SCALING-001 Level 2 |
| Need stable releases | Add `develop` branch | SCALING-001 Level 3 |
| 20+ PRs/week | Tiered review | SCALING-001 Level 4 |
| Multiple teams | Team-based CODEOWNERS | SCALING-001 Level 5 |

See: `specs/SCALING-001-Growth-Governance.md`

---

## GitHub Actions (Pending)

The following workflows will be implemented:

| Workflow | Purpose | Status |
|----------|---------|--------|
| `tribunal.yml` | Run 3-judge review on PRs | Planned |
| `auto-merge.yml` | Merge Dave's PRs on tribunal pass | Planned |
| `tests.yml` | Run test suite | Planned |

---

## Integrations (Planned)

| Integration | Purpose | Status |
|-------------|---------|--------|
| G-Drive API | Tribunal review docs | Planned (ADR-004) |
| Discord Webhook | Notifications | Planned (ADR-005) |

---

## Access

| Role | Users | Permissions |
|------|-------|-------------|
| Owner | @deiasolutions | Full admin |
| Bees | (service accounts) | Write (via PRs) |
| Contributors | (public) | Fork + PR |

---

## Files to Know

| File | Purpose |
|------|---------|
| `.github/REPO-CONFIG.md` | This file - repo configuration |
| `.github/CODEOWNERS` | Code ownership (Level 1+) |
| `specs/README.md` | Spec organization guide |
| `specs/SCALING-001-*.md` | Governance scaling roadmap |
| `specs/BOK-REVIEW-001-*.md` | Tribunal pattern and workflow |

---

## Change Log

| Date | Change |
|------|--------|
| 2026-02-05 | Made repo public, enabled branch protection |
| 2026-02-05 | Set `main` as default branch, deleted `master` |
| 2026-02-04 | Initial push to deiasolutions/simdecisions |

---

*This document is the source of truth for repository configuration.*
