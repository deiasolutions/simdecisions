# ADR-010: "Script Language" and "Hive Code" for System Commands

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Q33N (Gemini)
**Reviewers:** [Pending]

---

## Summary

This ADR proposes the creation of a two-tiered command language system to provide a powerful, yet user-friendly, method for interacting with the Hive Control Plane. This system will consist of:
1.  **Script Language:** A high-level, formulaic English language for human operators.
2.  **Hive Code:** A low-level, Basque-based symbolic language that the Hive's core components will execute.
3.  **Translator:** A service that translates Script Language into Hive Code.

---

## Context

### Problem

Direct API calls are precise but not user-friendly for rapid command and control. Natural Language Processing (NLP) is user-friendly but can be ambiguous. A middle ground is needed: a structured, human-readable language that can be reliably translated into machine-executable code for the Hive. This provides both power and clarity. The choice of a Basque-based low-level language adds a unique, thematic layer consistent with the project's creative vision.

### Requirements

1.  **Human Readability:** A high-level language that is easy for humans to write and understand.
2.  **Machine Executability:** A low-level language that is unambiguous for the Hive to parse and execute.
3.  **Translation Layer:** A reliable translator between the two languages.
4.  **Extensibility:** The system must be designed to accommodate new commands and parameters over time.

---

## Decision

Adopt a two-tiered language system. A `Translator` service will convert high-level **Script Language** into low-level **Hive Code**. The Hive Control Plane will be extended with an endpoint (`/api/v1/hive-code`) to accept and execute Hive Code, which will then perform actions via the existing `crud` and service layers.

---

## Architecture and Design

### 1. Script Language (High-Level)

A formulaic English language that serves as a user-friendly abstraction for commands. String literals are enclosed in double quotes.

**Examples:**
*   `CREATE TASK with title "Review new language spec" and description "ADR-010 defines ScriptLang and HiveCode."`
*   `LIST TASKS with status "pending"`
*   `ASSIGN TASK "task-uuid-123" to AGENT "BEE-001"`
*   `GET TASK "task-uuid-123"`
*   `SEND MESSAGE "hello world" to CHANNEL "general"`

### 2. Hive Code (Low-Level, Basque-based)

A symbolic, machine-parsable language that mimics Basque grammar. It uses Basque keywords and suffixes for structure, while keeping user-provided string literals (e.g., task titles) in their original language.

**Vocabulary:**
*   **Verbs (Commands):** `sortu` (create), `zerrendatu` (list), `lortu` (get), `esleitu` (assign), `bidali` (send)
*   **Nouns:** `zeregina` (the task), `zereginak` (the tasks), `eragilea` (the agent), `mezua` (the message)
*   **Cases/Suffixes:** `-ri` (to, dative case), `-arekin` (with, comitative case)
*   **Keywords:** `izenburuarekin` (with title), `egoerarekin` (with status), `kanalari` (to the channel)

**Examples (Translation of Script Language):**
*   **Script:** `CREATE TASK with title "New Task"`
*   **Hive Code:** `SORTU ZEREGINA "New Task" izenburuarekin`
*   **Script:** `LIST TASKS with status "pending"`
*   **Hive Code:** `ZERRENDATU ZEREGINAK "pending" egoerarekin`
*   **Script:** `ASSIGN TASK "task-1" to AGENT "bee-1"`
*   **Hive Code:** `ESLEITU ZEREGINA "task-1" "bee-1" eragileari`
*   **Script:** `SEND MESSAGE "hello world" to CHANNEL "general"`
*   **Hive Code:** `BIDALI MEZUA "hello world" "general" kanalari`

### 3. The Translator: A Hybrid Approach

To achieve both speed and flexibility, the Translator will be implemented with a hybrid, two-stage architecture:

1.  **Fast Path (Rule-Based Parser):** The primary translator will be a formal parser built with `lark-parser`. It will be designed to handle the well-defined, formulaic English of the Script Language. This path is extremely fast, deterministic, and cost-free.

2.  **Fallback Path (LLM Agent):** If the Lark parser fails to understand a command (due to non-standard phrasing or ambiguity), the system will automatically fall back to an LLM-based translator. This LLM's role is to:
    *   Analyze the ambiguous input.
    *   Use the context of the conversation and embedding-based search to understand the user's intent.
    *   **"Push back immediately to ask the clarifying question"** if the ambiguity cannot be resolved with high confidence.
    *   Generate a valid Hive Code string once the intent is clear.

This hybrid model provides immediate, reliable execution for standard commands while offering an intelligent, interactive, and flexible path for handling complex or ambiguous user input.

### 4. Context, Embeddings, and LLM Selection

To empower the LLM-based translator fallback, the system must have a mechanism for understanding context and leveraging robust language models.

*   **Embedding Model:** Standard embedding services like Voyage AI do not have confirmed, high-quality support for Basque. We will use a dedicated, open-source model trained on Basque, such as **`ixa-ehu/berteus-base-cased`** from Hugging Face, to generate high-quality embeddings. These embeddings will enable the LLM to understand semantic similarity and context relevant to ambiguous commands.

*   **LLM for Fallback:** For the LLM component of the hybrid translator, specifically for handling ambiguity and interactive clarification, we will leverage foundational Basque LLMs:
    *   **`Llama-eus-8B`** (Orai NLP Teknologiak)
    *   **`Latxa`** (based on Llama 2)
    These models are specifically trained for understanding and generating Basque text, making them ideal for the nuanced interpretation required.

### 5. Hive Control Plane Integration

The `/api/v1/hive-code` endpoint will receive a Hive Code string. Its internal parser must deconstruct the Basque sentence to identify the command, objects, and parameters before routing to the appropriate service function.

---

## Implications

*   **Increased Complexity:** This design is significantly more complex. The translator is now two-stage, and the Hive Code executor requires a formal grammar parser.
*   **Enhanced Theming & Flexibility:** Provides a rich, thematic language and a graceful path for handling user ambiguity.
*   **New Dependencies:** The system now has a dependency on a formal parsing library (`lark`), a high-quality Basque embedding model (`ixa-ehu/berteus-base-cased`), and a foundational Basque LLM (`Llama-eus-8B` or `Latxa`) for the fallback path.
*   **No Machine Translation Required:** The system still only rearranges the structure of the command, not the content of its string parameters.

---

## Implementation Phases

1.  **Phase 1: Language & Grammar Definition:** Formally define the initial grammar for both Script Language and Hive Code for a core set of commands (`CREATE`, `LIST`, `GET` for tasks).
2.  **Phase 2: Basic Translator & Executor:**
    *   Build a simple translator in Python for the core commands.
    *   Implement the `/api/v1/hive-code` endpoint in `main.py`.
    *   Implement a parser within the endpoint to execute the translated Hive Code for creating and listing tasks.
3.  **Phase 3: Expansion:** Expand the grammar, translator, and executor to support more commands (`ASSIGN`, `UPDATE`, etc.) and nouns (agents, messages).
4.  **Phase 4: CLI Integration:** Integrate the Script Language into the dedicated `simdecisions` CLI tool (from ADR-009) as a primary command method.

---

## Future Consideration: Data Capture for AI-Powered Translator

To create a self-improving system, all translator activity should be captured in the **Event Ledger (ADR-001)**. This creates a unique and valuable parallel corpus (Script Language -> Hive Code) that can be used to train a neural network-based translator in the future.

### Data Capture Mechanism

A new event type, `translation_executed`, will be logged for each translation attempt. The `payload_json` will contain:

```json
{
  "input_script_language": "CREATE TASK with title \"New Task\"",
  "output_hive_code": "SORTU ZEREGINA \"New Task\" izenburuarekin",
  "translation_success": true,
  "parser_version": "lark-v0.2" 
}
```

### Benefits

*   **Self-Improving System:** The captured data provides a training set to evolve the translator from a rule-based parser to a more flexible neural network.
*   **Enhanced Flexibility:** A trained model could eventually handle less formulaic and more "natural" English inputs.
*   **Unique Data Asset:** Creates a proprietary corpus for advanced AI development and analysis.
