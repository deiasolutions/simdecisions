# ADR-008: Integrate Model Context Protocol (MCP) for AI Agent Communication

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Gemini
**Reviewers:** [Pending]

---

## Summary

This ADR proposes the adoption of the **Model Context Protocol (MCP)** as a critical, third, first-class communication method for the `simdecisions` project. While strategically phased for future implementation, MCP's importance for AI agent interaction is considered on par with existing communication methods. It will serve as a standardized interface specifically for AI agents ("bees") to interact with the Hive Control Plane, access tools, and retrieve external context, complementing the existing File-Driven and API-Driven communication methods.

---

## Context

### Problem

Our AI agents ("bees") require a structured and scalable way to connect with external systems. This includes accessing real-time data, using external tools (e.g., search engines, calculators), and performing actions on behalf of a user. Creating custom, one-off integrations for each tool and data source is inefficient, brittle, and does not scale as the number of agents and tools grows.

### Requirements

1.  **Standardization:** A standard protocol for AI-to-system communication is needed to avoid building proprietary integrations.
2.  **Tool & Data Access:** Agents must be able to discover and use external tools and data sources.
3.  **Action Performing:** Agents must be able to perform actions in external systems.
4.  **Coexistence:** The new method must coexist with the established File-Driven and API-Driven (REST/WebSocket) communication methods.
5.  **Security:** All communication must be secure and auditable.

---

## Decision

Adopt the **Model Context Protocol (MCP)** as a primary, specialized communication interface for AI agents ("bees"). This adoption is considered a strategic future addition, holding equivalent architectural significance to the File-Driven and API-Driven methods. The Hive Control Plane will be extended to expose an MCP-compliant server endpoint, which will act as the gateway for agents to access tools and data.

This establishes three strategically important, first-class communication methods:
1.  **File-Driven:** For CLI-only workflows and local Git repository interaction.
2.  **API-Driven (REST/WebSocket):** For general system management, human-facing UIs, and non-agent communication.
3.  **MCP-Driven:** For AI agents to request context, use tools, and perform actions in a standardized way.

---

## Architecture/Design

The MCP endpoint will be a new component of the Hive Control Plane backend (running on Railway).

```
                            ┌─────────────────────────────────┐
                            │      HIVE CONTROL PLANE         │
                            │                                 │
┌──────────────┐            │  ┌────────────┐  ┌──────────┐   │
│   LLM Bees   │──(MCP)────▶│  │ MCP Server │──│ Tool     │   │
│ (AI Agents)  │            │  │ Endpoint   │  │ Registry │   │
└──────────────┘            │  └────────────┘  └──────────┘   │
                            │                                 │
┌──────────────┐            │  ┌────────────┐  ┌──────────┐   │
│ Human User / │──(REST)───▶│  │ REST API   │  │ Task     │   │
│      UI      │            │  │ Endpoint   │  │ Service  │   │
└──────────────┘            │  └────────────┘  └──────────┘   │
                            │                                 │
┌──────────────┐            │  ┌────────────┐                 │
│  CLI Agent   │──(Files)──▶│  │ File Sync  │                 │
│ (Local Repo) │            │  │ Service    │                 │
└──────────────┘            │  └────────────┘                 │
                            │                                 │
                            └─────────────────────────────────┘
```

*   **Bees as MCP Clients:** AI agents will be designed to act as MCP clients. When they need to use a tool or access external data, they will make a request to the MCP endpoint on the Hive Control Plane.
*   **Hive as MCP Server:** The Hive Control Plane will parse these MCP requests, invoke the appropriate registered tool (e.g., an internal function, an external API call), and return the result to the bee in the standard MCP format.
*   **Separation of Concerns:**
    *   **MCP:** Used by AI agents for *contextual task execution* (e.g., "search the web," "read this file," "calculate the total").
    *   **REST API:** Used by UIs and management scripts for *system orchestration* (e.g., "list all tasks," "get bee status," "create new task").
    *   **File System:** Used for simple, offline-first interactions.

---

## Pros

*   **Standardization:** Adopts an emerging industry standard for AI interaction, reducing the need for proprietary solutions.
*   **Enhanced AI Capabilities:** Empowers bees to perform a wider range of tasks by providing a structured way to access tools.
*   **Future-Proofing:** Aligns the project with the direction the AI industry is heading regarding agent-tool interaction.
*   **Clear Separation of Concerns:** Distinguishes between agent-level communication (MCP) and system-level management (REST API), leading to a cleaner architecture.
*   **Interoperability:** Potentially allows third-party MCP-compliant agents to interact with the hive in the future.

---

## Cons

*   **New Protocol:** MCP is a relatively new protocol (late 2024), meaning best practices and mature libraries are still under development.
*   **Implementation Overhead:** Requires adding a new MCP-compliant component to the Hive Control Plane backend.
*   **Potential Overlap:** Care must be taken to define the clear boundary between what actions belong in the REST API versus the MCP endpoint to avoid confusion.

---

## Alternatives Considered

*   **Custom Tool-Use API:** Developing a proprietary API for tool use. This would require more design work and would be less standard and interoperable than MCP.
*   **Relying Solely on the REST API:** Overloading the existing REST API with endpoints for tool use. This would mix the concerns of system management and agent task execution, leading to a more complex and less intuitive API.

---

## Implementation Phases

1.  **Phase 1: Research & Prototyping:** Evaluate existing open-source MCP server implementations and libraries. Build a minimal proof-of-concept.
2.  **Phase 2: Read-Only Tool Integration:** Implement a basic MCP endpoint on the Hive Control Plane that exposes a simple, read-only tool (e.g., `get_current_time`).
3.  **Phase 3: Action Tool Integration:** Extend the MCP server to support tools that perform actions (e.g., "create_file," "send_message").
4.  **Phase 4: Agent Migration:** Update the primary "bee" agents to utilize MCP for all tool and external data access.

---
