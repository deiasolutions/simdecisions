# SimDecisions Specifications

## Organization

| Prefix | Type | Purpose |
|--------|------|---------|
| `ADR-*` | Architecture Decision Record | Foundational decisions, schemas, conventions |
| `BOK-*` | Book of Knowledge Pattern | Reusable patterns and practices |
| `SPEC-*` | Feature Specification | Detailed specs for specific features |
| `SCALING-*` | Scaling Roadmap | Future improvements for when we grow |

## Subdirectories

| Directory | Contents |
|-----------|----------|
| `architecture/` | Architecture diagrams and deep-dives |
| `dave/inputs/` | Raw Q33N input for refinement into formal specs |

## Current Specs

### ADRs (Architecture Decisions)

| ID | Title | Status |
|----|-------|--------|
| ADR-001 | Event Ledger Foundation | IMPLEMENTED |
| ADR-002 | API Endpoint Registry | IMPLEMENTED |
| ADR-003 | Entity ID Convention | IMPLEMENTED |
| ADR-004 | G-Drive Coordination Layer | PROPOSED |
| ADR-005 | Dual-Publish Knowledge | PROPOSED |
| ADR-006 | Hive Control Plane | PROPOSED |

### BOK Patterns

| ID | Title | Status |
|----|-------|--------|
| BOK-REVIEW-001 | GitHub Tribunal Pattern | PROPOSED |

### Feature Specs

| ID | Title | Status |
|----|-------|--------|
| SPEC-PyBee | Python Executable Species | PROPOSED |
| RAGGIT | Creator Marketplace Protocol | DRAFT |

### Scaling Roadmap

| ID | Title |
|----|-------|
| SCALING-001 | Growth & Governance Scaling |

## Spec Lifecycle

```
DRAFT → PROPOSED → APPROVED → IMPLEMENTED → DEPRECATED
```

| Status | Meaning |
|--------|---------|
| DRAFT | Work in progress, incomplete |
| PROPOSED | Complete, awaiting review |
| APPROVED | Accepted, ready to build |
| IMPLEMENTED | Built and deployed |
| DEPRECATED | Superseded, kept for reference |

## Adding a Spec

1. Check `dave/inputs/` for raw requirements
2. Choose appropriate prefix (ADR/BOK/SPEC/SCALING)
3. Use next available number
4. Follow existing spec format
5. Update this README

---

*Specs live in GitHub (source of truth) and G-Drive (human-readable). See ADR-005.*
