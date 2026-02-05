# Current Change Process as a Governance Configuration

**Date:** 2026-02-05

**Author:** Gemini

## Preamble

As per **ADR-002: Configurable Change Governance as a Product Feature**, we must document our existing change management process as the first configuration instance of the new framework. This document serves as that initial test case and configuration example.

Our current process for managing code changes in the `simdecisions` repository maps directly to the concepts of Change Zones, Change Types, and Approval Flows.

## Configuration Mapping

Here is our `tribunal + PR` process expressed in the language of the new governance framework:

### 1. The Change Type

*   **`type`**: `code`
*   **Description**: This applies to any change to the source code of the SimDecisions platform on the `main` branch.

### 2. The Change Zone

*   **`zone`**: `production`
*   **Description**: The `main` branch is considered our production environment. It contains the code that is considered stable and is the source for future deployments.

### 3. The Approval Flow

*   **`flow_id`**: `tribunal_approval`
*   **Description**: A heavyweight process requiring explicit approval from a qualified human quorum.
*   **Steps**:
    1.  **Gate**: `human_review`
        *   **Approvers**: `role: tribunal_judge`
        *   **Quorum**: `3`
        *   **Mechanism**: GitHub Pull Request approvals.
    2.  **Gate**: `human_gate`
        *   **Approvers**: `role: lead_developer` (the person merging the PR)
        *   **Quorum**: `1`
        *   **Mechanism**: The final act of merging the pull request after approvals are secured.

## YAML Representation

If this were represented in the `kb/change_governance.yml` file, it would look like this:

```yaml
# This specific rule would be part of a larger ruleset
# that links a type/zone pair to a flow.
- rule:
    change_type: "code"
    change_zone: "production"
    approval_flow: "tribunal_approval"

# The flow itself is defined in the 'approval_flows' section.
approval_flows:
  - id: tribunal_approval
    description: "Requires approval from the 3-judge tribunal via GitHub PR."
    steps:
      - gate: "review"
        approvers:
          role: "tribunal_judge"
          quorum: 3
        # In our current setup, the mechanism is an external GitHub PR.
        # The engine would eventually have a way to represent this.
        mechanism: "github_pr_approval"
      - gate: "merge"
        approvers:
          role: "lead_developer"
          quorum: 1
        mechanism: "github_pr_merge"
```

This document formally bootstraps our own governance, making us the first customer of the Configurable Change Governance feature.
