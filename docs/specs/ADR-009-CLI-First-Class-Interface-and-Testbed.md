# ADR-009: CLI as a First-Class Interface and Testbed

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Q33N (Gemini)
**Reviewers:** [Pending]

---

## Summary

This ADR formally defines the **Command-Line Interface (CLI)** as a first-class citizen within the `simdecisions` ecosystem. It confirms the existing foundation for CLI interaction via file-driven communication and outlines a plan to further develop a dedicated `simdecisions` CLI tool. Crucially, this CLI will serve as a strategic testbed, validating API functionality and user workflows before, and in parallel with, the development of web-based tools.

---

## Context

### Problem

While the Hive Control Plane (ADR-006) establishes file-driven communication, a dedicated CLI tool for `simdecisions` has not yet been explicitly defined as a distinct interface. Clear articulation of CLI capabilities and its role as a testing mechanism is necessary to ensure consistent development and validation across interaction paradigms (file, CLI, web).

### Requirements

1.  **Confirmation of Existing CLI Status:** Clearly document how the CLI is already a first-class interaction method.
2.  **Expanded CLI Functionality:** Plan for a dedicated, interactive CLI tool that goes beyond direct file manipulation.
3.  **CLI as Testbed:** Establish the CLI as a primary means to test and validate API functionality for web tools.
4.  **Consistency:** Ensure CLI, file-driven, and web interfaces operate on the same underlying logic.

---

## Decision

The CLI is a **first-class interface** for `simdecisions`. Its initial realization through file-driven communication will be expanded with a dedicated `simdecisions` CLI tool. This tool will directly leverage the Hive Control Plane's API, serving as a primary validation mechanism for backend functionality that will eventually power web-based user interfaces.

---

## Existing CLI First-Class Status (Confirmation)

The foundation for CLI-first-class interaction is already established and implemented through the **File-Driven Communication** mechanism of the Hive Control Plane (ADR-006):

*   **Mechanism:** CLI users and agents (like the `hello_bee.py` agent) interact with the system by directly reading and writing Markdown files in the `.deia/hive/` directory. These files represent tasks, responses, and other state.
*   **Core Features:**
    *   **One-Way Sync (API-to-Files):** Tasks created via the API are automatically translated into Markdown files.
    *   **Bidirectional Sync (Files-to-DB):** Changes made to Markdown files are detected by a file watcher and synchronized back to the database.
    *   **LLM-Powered Conflict Resolution:** Intelligent resolution of conflicts when both API and file modifications occur, ensuring data integrity.
*   **Validation:** The `hello_bee.py` agent successfully demonstrates this end-to-end file-driven workflow, where a CLI-initiated agent can discover, claim, and complete tasks purely through filesystem interaction, with the Hive Control Plane managing synchronization.

---

## Plan to Build Out Remaining CLI Functionality

Beyond file-driven interaction, a dedicated `simdecisions` CLI tool will be developed, directly interacting with the Hive Control Plane's API. This will provide a richer, more interactive experience for human operators and advanced agents.

### Proposed CLI Tool Features:

*   **Dedicated CLI Tool:** A standalone Python (or Go) command-line application (e.g., `sd task create`, `sd task list`).
*   **Task Management:**
    *   `sd task create [title] --desc="..." --ref="..."`: Create tasks via API.
    *   `sd task list [--status=pending]`: List tasks from API.
    *   `sd task show [id]`: View full task details.
    *   `sd task update [id] --status=in_progress`: Update task status.
    *   `sd task claim [id]`: Claim a task.
    *   `sd task complete [id]`: Mark a task as complete.
*   **Messaging:**
    *   `sd msg send [channel] "message"`: Send messages to a channel.
    *   `sd msg watch [channel]`: Stream messages (basic polling or WebSocket integration).
*   **Agent Management:**
    *   `sd bee list`: List active bees.
    *   `sd bee status [id]`: Get status of a specific bee.
*   **Configuration:**
    *   `sd config set api-key [...]`: Manage API keys.
    *   `sd config show`: Display current configuration.
*   **Integrated File Sync Commands:**
    *   `sd hive pull [--task-id=...]`: Explicitly pull the latest state of tasks from the database to their Markdown files.
    *   `sd hive push [--task-id=...]`: Explicitly push local Markdown file changes to the database (bypassing the watcher if desired, or triggering a sync).

---

## CLI as a Testbed for Web Tools

The development of the dedicated `simdecisions` CLI tool will inherently serve as a critical testbed for the underlying API and business logic that will also power the web-based interfaces.

### Benefits of CLI-First Testing:

*   **API Validation:** Any API endpoint consumed by the CLI tool is directly validated for functionality, input/output schemas, and error handling. This ensures the backend API is robust and correct for *any* client.
*   **Workflow Validation:** Complex user workflows (e.g., creating a task, claiming it, completing it) can be thoroughly tested via the CLI before the overhead of a full GUI is built.
*   **Speed of Iteration:** CLI development and testing cycles are typically faster than GUI development, allowing quicker iteration on backend features.
*   **Regression Prevention:** CLI tests can become automated integration tests for the API, preventing regressions as web tools are developed.
*   **Headless Operations:** CLI provides a headless means to interact with the system, essential for automation and scripting, and mirroring AI agent behavior.

### Workflow for CLI as Testbed:

1.  **Define Core API Endpoints:** (Already mostly done in ADR-006).
2.  **Develop CLI Commands:** Implement `simdecisions` CLI commands that call these API endpoints.
3.  **Validate CLI Functionality:** Ensure CLI commands work correctly and provide expected output.
4.  **Develop Web UI Components:** Build web UI components that consume the *same* API endpoints validated by the CLI.
5.  **Automated Testing:** CLI commands can be easily integrated into automated test suites (e.g., Python `unittest`, `pytest`) to form robust integration tests for the backend API.

---

## Implications

*   New `simdecisions-cli` repository or subdirectory in `simdecisions` project.
*   Dependencies on `requests` (for API calls) and potentially `click` or `typer` for CLI framework.
*   Potential for shared libraries/schemas between backend and CLI.
*   CLI development will inform and validate the API design for web clients.

---

## Implementation Phases

1.  **Phase 1: Basic Task Management CLI:** Implement `sd task create`, `sd task list`, `sd task show` directly against the Hive Control Plane API.
2.  **Phase 2: Task Update & Claiming:** Implement `sd task update`, `sd task claim`, `sd task complete`.
3.  **Phase 3: Basic File Sync Commands:** Implement `sd hive pull`, `sd hive push` (interacting with the file sync API endpoints).
4.  **Phase 4: Advanced Features & Messaging:** Implement messaging, agent management, and other advanced features.

---
