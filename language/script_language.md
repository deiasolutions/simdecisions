# Script Language Specification v0.1

**Author:** Q33N (Gemini)
**Status:** DRAFT
**Related ADR:** ADR-010

---

## 1. Overview

Script Language is a high-level, formulaic English language designed for human operators to interact with the SimDecisions Hive Control Plane. It prioritizes readability and ease of use, while maintaining a structure that allows for reliable translation into low-level Hive Code.

## 2. General Syntax

The general syntax follows a `COMMAND [NOUN] {parameters}` pattern.

*   **COMMAND:** An imperative verb (e.g., `CREATE`, `LIST`, `GET`, `ASSIGN`).
*   **NOUN:** The object of the command (e.g., `TASK`, `AGENT`).
*   **Parameters:** A JSON-like object `{ key: "value", ... }` or a series of identifiers and literals.

## 3. Core Commands (v0.1)

### 3.1 `CREATE TASK`

**Syntax:**
`CREATE TASK { title: "string", description: "string", [other_params...] }`

**Description:**
Creates a new task in the system.

**Parameters:**
*   `title` (string, required): The title of the task.
*   `description` (string, optional): A longer description of the task.
*   `task_ref` (string, optional): A reference ID for the task.
*   `created_by` (string, optional): The entity creating the task.

**Example:**
`CREATE TASK { title: "Review ADR-010", description: "Review the new language spec." }`

---

### 3.2 `LIST TASKS`

**Syntax:**
`LIST TASKS { [key: "value", ...] }`

**Description:**
Lists tasks that match the given filter parameters.

**Parameters:**
*   `status` (string, optional): Filter tasks by status (e.g., "pending", "in_progress").
*   `assigned_to` (string, optional): Filter tasks by the assigned agent.

**Example:**
`LIST TASKS { status: "pending" }`

---

### 3.3 `GET TASK`

**Syntax:**
`GET TASK "task-id"`

**Description:**
Retrieves a single task by its unique ID.

**Parameters:**
*   A single string literal representing the task ID.

**Example:**
`GET TASK "a1b2c3d4-e5f6-..."`

---

### 3.4 `ASSIGN TASK`

**Syntax:**
`ASSIGN TASK "task-id" to AGENT "agent-id"`

**Description:**
Assigns a task to a specific agent.

**Parameters:**
*   A string literal for the task ID.
*   The keyword `to AGENT`.
*   A string literal for the agent ID.

**Example:**
`ASSIGN TASK "a1b2c3d4-..." to AGENT "BEE-001"`

---

## 4. Future Expansions

Future versions of the language will include commands for:
*   `UPDATE TASK`
*   `CREATE AGENT`, `LIST AGENTS`
*   `SEND MESSAGE`
*   More complex filtering in `LIST` commands.
