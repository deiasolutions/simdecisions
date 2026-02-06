# ADR-011: High-Performance Architecture for Discrete Event Simulation

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Q33N (Gemini)
**Reviewers:** [Pending]

---

## Summary

To meet the high-performance requirement of `1,000,000x` faster-than-realtime simulations, this ADR proposes a fundamental architectural pivot for the Discrete Event Simulation (DES) component. We will create a core **`SimDecisions Engine`** in **Rust**. This engine will be compiled to both **WebAssembly (WASM)** for client-side execution and a **native Python module** for server-side execution, providing maximum performance and flexibility.

---

## Context

### Problem

The initial Hive Control Plane architecture (FastAPI + PostgreSQL) is designed for transactional, real-time production workloads, not high-speed simulation. A performance target of `1,000,000x` real-time makes database I/O and Python's interpreted nature prohibitive bottlenecks. A new architecture is required to meet this DES ambition.

### Requirements

1.  **Extreme Performance:** Must be capable of simulating events at speeds far exceeding real-time (`>1,000,000x`).
2.  **In-Memory & OOP:** The simulation logic must be object-oriented and run entirely in memory, as requested.
3.  **Flexible Execution:** The engine must be runnable on the server (for batch jobs, testing) and offloaded to the client's machine (for interactive use, leveraging user hardware).
4.  **Data Persistence:** Simulation results (the event ledger) must be persistable to the central database *after* the simulation run is complete.

---

## Decision

The `SimDecisions` DES will be powered by a new, core **`simdecisions-engine`** library written in **Rust**. This single Rust codebase will be compiled to two targets:

1.  A **WebAssembly (WASM) module** to be loaded and executed by the Next.js frontend, directly in the user's browser.
2.  A **native Python module** (using `PyO3`) to be imported and executed by the FastAPI backend.

This hybrid approach provides a unified, high-performance engine that satisfies all stated requirements.

---

## New Architecture: The "Pluggable Reality Kernel"

The `simdecisions-engine` will be designed as a "Pluggable Reality Kernel." This means the core simulation logic will be generic, and the specific "reality" it operates in—either a high-speed simulation or a real-time production environment—will be determined by pluggable components.

### 1. `simdecisions-engine` (New Rust Crate)

*   **Language:** Rust
*   **Core Logic:** An in-memory, object-oriented DES core containing:
    *   **Entities:** `SimAgent`, `SimTask` structs.
    *   **`EventScheduler`:** A priority queue of future events.
    *   **In-Memory `EventLedger`:** A `Vec<Event>` for capturing results.
*   **Pluggable Clock (`Clock` Trait):**
    *   **`SimulatedClock`:** Advances time instantly to the next scheduled event for faster-than-realtime simulation.
    *   **`RealtimeClock`:** Uses the system's wall clock for running the engine as a 1x speed production driver.
*   **Pluggable Executor (`Executor` Trait):**
    *   **`SimulatedExecutor`:** When a `work` event occurs, this executor does not perform real work. It will draw durations from statistical distributions (e.g., for Average Handle Time) and schedule a future `work_completed` event. It will also be responsible for stochastic work generation using **Poisson or Erlang distributions** to schedule new task arrivals.
    *   **`ProductionExecutor`:** When a `work` event occurs, this executor will make an API call to the Hive Control Plane to dispatch the task to a real agent (LLM, human).
*   **Real-Time Event Emitter:** The engine will accept a callback function or use a channel to emit events *as they are processed*. This allows external systems (like a UI) to receive a real-time feed of the simulation's or production run's progress.
*   **API Control:** The engine will expose a clear API for its lifecycle (`new`, `run`, `pause`, `step`, `get_state`) to both Python and JavaScript.

### 2. `simdecisions-frontend` (Next.js) - Role

*   **Loads WASM:** Loads the compiled `simdecisions-engine.wasm`.
*   **Client-Side Simulation:** The user can configure and run simulations entirely in their browser, leveraging their local CPU.
*   **Real-time Visualization:** Subscribes to the WASM engine's event emitter to render real-time charts, logs, and visualizations.
*   **Bulk Data Submission:** After a simulation, sends the complete in-memory event ledger to the backend for persistence.

### 3. `simdecisions-backend` (FastAPI) - Role

*   **Mission Control:** Configures, launches, and ingests results from the engine.
*   **Server-Side Execution:** Imports the engine as a Python module to run simulations or to operate as the production driver. When running server-side, it will use the real-time event emitter to push events to a WebSocket for consumption by the dashboard.
*   **Result Ingestion Endpoint (`/api/v1/simulation/ingest`):** A new endpoint for receiving and bulk-inserting simulation results.

---

## Implications

*   **Unified Engine:** We will have a single, high-performance Rust core that can serve as both a `1,000,000x` speed simulation engine AND the real-time production driver for our hive.
*   **New Technology Stack:** Introduces **Rust** as a core development language.
*   **Increased (but Justified) Complexity:** The "Pluggable Reality" design is more complex upfront but provides immense flexibility and power, cleanly separating the engine's core logic from its execution context.
*   **Decoupled Architecture:** The simulation engine is cleanly separated from the transactional web application.
*   **Superior User Experience:** Offloading simulations to the client provides a highly interactive and responsive experience at zero server cost for computation.

---
