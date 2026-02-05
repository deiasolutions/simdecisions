# Hive Code Specification v0.2

**Author:** Q33N (Gemini)
**Status:** DRAFT
**Related ADR:** ADR-010

---

## 1. Overview

Hive Code is a low-level, symbolic, machine-parsable language designed for the Hive Control Plane's core execution engine. Its vocabulary is based on Basque, and its structure mimics Basque grammar, using verbs, nouns, and case suffixes. This structure, while more complex than s-expressions, provides a rich, thematic command language. String literals within the commands remain in their original language.

## 2. General Syntax

The syntax is sentence-like, generally following a `[VERB] [NOUN] [PARAMETERS...]` structure. Case suffixes are attached to nouns to denote their role in the sentence.

*   **VERB (Command):** A Basque-derived verb indicating the action (e.g., `SORTU`, `ESLEITU`).
*   **NOUN (Object):** A Basque-derived noun, often with a definite article suffix (`-a`), indicating the primary object (e.g., `ZEREGINA` - "the task").
*   **PARAMETERS:** A series of literals and keywords with case suffixes (e.g., `"New Title"` `izenburuarekin` - "with title 'New Title'").

## 3. Core Vocabulary & Grammar (v0.2)

### 3.1 Vocabulary

| English | Hive Code | Type | Notes |
|---|---|---|---|
| Create | `SORTU` | VERB | |
| List | `ZERRENDATU`| VERB | |
| Get | `LORTU` | VERB | |
| Assign | `ESLEITU` | VERB | |
| Send | `BIDALI` | VERB | |
| Task | `ZEREGINA` | NOUN | "The task" (singular, definite) |
| Tasks | `ZEREGINAK` | NOUN | "The tasks" (plural, definite) |
| Agent | `eragile` | NOUN | Base form for agent |
| Message | `MEZUA` | NOUN | "The message" |
| Channel | `kanal` | NOUN | Base form for channel |
| with title | `izenburuarekin`| KEYWORD | `izenburu` + `-arekin` (with) |
| with status| `egoerarekin` | KEYWORD | `egoera` + `-arekin` (with) |
| to agent | `eragileari` | SUFFIX | `-ari` (to, dative) attached to agent ID |
| to channel | `kanalari` | KEYWORD | `kanal` + `-ari` (to) |

### 3.2 Case Suffixes

*   **Dative (`-ri`):** Indicates the indirect object, or "to whom/what" an action is done. `eragileari` -> "to the agent".
*   **Comitative (`-arekin`):** Indicates "with" or accompaniment. `izenburuarekin` -> "with the title".

## 4. Core Commands (v0.2)

### 4.1 Create Task

**Syntax:**
`SORTU ZEREGINA "title" izenburuarekin [eta "description" deskribapenarekin]`

**Description:**
Creates a new task. The title is required. The description is optional and preceded by `eta` (and).

**Example:**
`SORTU ZEREGINA "Review ADR-010" izenburuarekin eta "A new language spec" deskribapenarekin`

---

### 4.2 List Tasks

**Syntax:**
`ZERRENDATU ZEREGINAK ["status" egoerarekin]`

**Description:**
Lists tasks. Filtering by status is optional.

**Example:**
`ZERRENDATU ZEREGINAK "pending" egoerarekin`

---

### 4.3 Get Task

**Syntax:**
`LORTU ZEREGINA "task-id"`

**Description:**
Retrieves a single task by its unique ID.

**Example:**
`LORTU ZEREGINA "a1b2c3d4-e5f6-..."`

---

### 4.4 Assign Task

**Syntax:**
`ESLEITU ZEREGINA "task-id" "agent-id" eragileari`

**Description:**
Assigns a task to an agent.

**Example:**
`ESLEITU ZEREGINA "a1b2c3d4-..." "BEE-001" eragileari`

---

### 4.5 Send Message

**Syntax:**
`BIDALI MEZUA "message content" "channel-name" kanalari`

**Description:**
Sends a message to a channel.

**Example:**
`BIDALI MEZUA "Hello World" "general" kanalari`

---

## 5. Execution

The Hive Control Plane's `/api/v1/hive-code` endpoint will receive these sentences as strings. A formal parser (e.g., using `lark-parser`) will be required to deconstruct the sentence based on its grammar to identify the command, objects, and parameters.
