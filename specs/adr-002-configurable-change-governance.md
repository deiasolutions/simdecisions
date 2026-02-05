# ADR 002: Configurable Change Governance as a Product Feature

**Status:** Proposed

## 1. Context

SimDecisions is an orchestration platform for complex, multi-agent systems. As these systems (hives) execute tasks and modify their own code and configuration, they require a robust governance layer. Enterprise customers in regulated industries (SOX, HIPAA, SOC 2) need auditable proof that changes made by both humans and AI agents follow established policies.

Current solutions are inadequate:
*   **Internal Tooling:** Ad-hoc scripts and manual review processes don't scale and lack auditability.
*   **Enterprise Change Management Tools (ServiceNow, Jira):** These are built for human-centric workflows and are disconnected from the high-velocity, automated changes occurring in an AI orchestration environment.
*   **Competitors (Gas Town, Roo Code):** These platforms focus on execution, not governance. They lack native capabilities to enforce change policies on the agents they orchestrate.

This ADR proposes that **Configurable Change Governance** become a core, shipping feature of the SimDecisions platform itself. SimDecisions will not only orchestrate agents but also govern their actions, providing a unified change management system for human/AI collaboration.

This capability directly operationalizes the principles outlined in our foundational papers:
*   **Federalist Paper No. 2 (Queens and Tyranny):** The defense layers against unilateral action are implemented as configurable approval flows.
*   **Federalist Paper No. 13 (Evolutionary Governance):** The Tripartite Experimentation Protocol is realized by allowing governance policies themselves to be simulated and tested.
*   **The Four-Vector Model:** An entity's autonomy (α-vector) in a given domain directly determines their ability to execute changes within a specific Change Zone.

## 2. Decision

We will build a "Configurable Change Governance" module as a core product feature. This module will be designed for enterprise use, allowing organizations to define and enforce change management policies across different operational zones and for various types of changes. We will be the first customer of this feature, using it to govern the development of SimDecisions itself.

The core components of this feature are:

1.  **Change Zones:** Configurable environments (e.g., Sandbox, Production) with varying levels of governance intensity.
2.  **Change Types:** A classification system for changes (e.g., Code, Schema, Policy) that allows for differential routing and approval.
3.  **Approval Flows:** A configurable engine for defining the sequence of approvals (quorum, timing, escalation) required for a change to be applied.
4.  **Dynamic Gates:** The existing gate system will be extended to become a dynamic function of `zone + change_type + entity_α + approval_state`.
5.  **Audit Trail:** The event ledger will be the immutable source of truth, recording the entire lifecycle of every change proposal for compliance and reporting.
6.  **Protocol of Grace:** A structured conflict resolution workflow is integrated into the rejection path, a unique feature of SimDecisions.

## 3. Feature Specification

### 3.1. Change Zones

Organizations will define Change Zones in a configuration file (`kb/change_governance.yml`). Each zone has a default approval flow and a set of rules.

| Zone       | Example                      | Approval Weight | Typical Flow                             |
|------------|------------------------------|-----------------|------------------------------------------|
| `sandbox`  | Local dev, experimentation   | None            | Act, Log                                 |
| `beta`     | Staging, test environments   | Lightweight     | Propose → Review → Apply                 |
| `production`| Live systems, customer-facing| Heavyweight     | Propose → Review → Approve → Stage → Apply |
| `critical` | Security, compliance, finance| Maximum         | Propose → Multi-Review → Board Approve → Apply → Audit |

### 3.2. Change Types

The system will classify changes to determine which approval flow to trigger.

| Change Type     | Examples                                    | Default Zone |
|-----------------|---------------------------------------------|--------------|
| `configuration` | Feature flags, thresholds, routing rules    | `beta`       |
| `schema`        | Event ledger fields, entity model changes   | `production` |
| `policy`        | Gate definitions, autonomy boundaries       | `critical`   |
| `code`          | Agent logic, adapters, core components      | `beta`       |
| `content`       | KB entities, documentation, templates       | `sandbox`    |
| `operational`   | Deployments, rollbacks, infrastructure changes| `production` |

### 3.3. Change Governance Schema

The configuration will be stored in `kb/change_governance.yml`. This file defines the zones, types, and approval flows.

```yaml
# kb/change_governance.yml

change_types:
  - id: configuration
    description: "Changes to non-structural parameters, feature flags, or agent routing rules."
    default_zone: beta
  - id: schema
    description: "Structural changes to data models, like the event ledger or entity definitions."
    default_zone: production
  - id: policy
    description: "Changes to governance rules, gate definitions, or autonomy boundaries."
    default_zone: critical
  - id: code
    description: "Changes to the application's source code."
    default_zone: beta
  - id: content
    description: "Changes to knowledge base articles, documentation, or other non-executable content."
    default_zone: sandbox
  - id: operational
    description: "Actions related to the deployment and operation of the system, like deployments or rollbacks."
    default_zone: production

change_zones:
  - id: sandbox
    description: "For local development and experimentation. Full autonomy."
    default_approval_flow: "auto_approve"
  - id: beta
    description: "For staging and pre-production testing. Requires peer review."
    default_approval_flow: "peer_review"
  - id: production
    description: "Live, customer-facing systems. Requires formal tribunal approval."
    default_approval_flow: "tribunal_approval"
  - id: critical
    description: "Core security, financial, or compliance policies. Requires executive sign-off."
    default_approval_flow: "board_approval"

approval_flows:
  - id: auto_approve
    description: "Automatically approve upon proposal."
    steps: []
  - id: peer_review
    description: "Requires one approval from a peer."
    steps:
      - gate: "review"
        approvers:
          role: "developer"
          quorum: 1
  - id: tribunal_approval
    description: "Requires approval from the 3-judge tribunal."
    steps:
      - gate: "review"
        approvers:
          role: "tribunal_judge"
          quorum: 3
        time_limit_hours: 72
        escalation_policy: "notify_lead"
  - id: board_approval
    description: "A multi-stage process for critical changes."
    steps:
      - gate: "technical_review"
        approvers:
          role: "tribunal_judge"
          quorum: 3
      - gate: "executive_signoff"
        approvers:
          role: "board_member"
          quorum: 1
        cooling_period_hours: 24 # Wait 24h after technical review
```

## 4. Roadmap

This feature will be rolled out in phases:

*   **Phase 2 (Current): Foundation.** The work on the Event Ledger (TASK-009) and Cost Tracking (TASK-010) serves as the essential audit and economic substrate for this feature.
*   **Phase 3: TASK-020: Change Zone Framework.**
    *   Implement the `kb/change_governance.yml` configuration.
    *   Extend the gate system from booleans to a dynamic function: `gate_check(entity, change_type, zone)`.
    *   Document our current PR process as the first instance of this configuration (`zone: production`, `type: code`, `flow: tribunal_approval`).
*   **Phase 4: Approval Flow Engine.**
    *   Build the workflow engine that routes a change proposal (as a task file) through the steps defined in its approval flow.
    *   This includes managing state, collecting approvals, and enforcing quorum and time constraints.
*   **Phase 5: Visual Layer.**
    *   Develop a dashboard view for enterprise users to monitor the change pipeline, see pending approvals, and review audit trails.
*   **Phase 6: Policy Experimentation.**
    *   Leverage Alterverse branching to simulate the impact of changes to the governance policies themselves, allowing SimDecisions to "eat its own dog food."

## 5. Next Steps

1.  **Acknowledge and Adopt:** This ADR should be reviewed and adopted as the formal plan.
2.  **Create Roadmap Item:** Add **TASK-020: Change Zone Framework** to the official project roadmap for Phase 3.
3.  **Foundation Tasks:** Continue executing tasks TASK-009 through TASK-012, with the awareness that they are the foundation for this governance feature.
4.  **Document Current Process:** Create a document that maps our current Git/PR process to the new framework, serving as the first configuration example.
