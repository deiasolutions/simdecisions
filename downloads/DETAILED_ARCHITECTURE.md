# Simulation Contact-Center App — Detailed Architecture & Behavior

This document summarizes how `simapp_075_001.pde` works after it was split into `simapp_exploded/` and annotated in `exploded_analysis/`. Each section references the exploded chunk where the logic lives and the compact notes that describe its intent. Imagine this as a 3–4 page overview to bring a reviewer up to speed before they dive into the original 6,500-line sketch.

## 1. Foundations & Global State (`02_main_stuff.pde`, `03_number_stuff.pde`, `04_agent_group_stuff.pde`)

`02_main_stuff.pde` initializes the simulation’s timeline variables (`simTick`, `repInterval`, `runTick`, `runMode`) plus the UI/control flags (`displayMode`, `modView`, `modStats`, `setupMode`). The exploded analysis entry `exploded_analysis/02_main_stuff.analysis.md` highlights that it also defines the Play/Pause/Fast-forward constants (`STOP`, `PAUSE`, `PLAY`, `FORWARD`) and the toggleable features (volseek, stfseek, callroute, multitask). Those globals orchestrate whether the main loop runs, when it pauses for staffing adjustments, and how user inputs affect time progression.

`03_number_stuff.pde` and `04_agent_group_stuff.pde` populate the data models that fuel the simulation. Each “number” (phone queue) receives service-level indicators (`numSLGoal`, `numAHTVar`, `numShortTime`, `numEscNum`) while agent groups store salary, occupancy, staffing schedules, and HashMaps for quick lookup. The `exploded_analysis/03_number_stuff.analysis.md` and `exploded_analysis/04_agent_group_stuff.analysis.md` notes remind us that the simulator combines these parameters to determine routing priorities, escalation paths, and multi-tasking allowances as contacts flow through the system.

`05_queue_stuff.pde` keeps the queue-specific lists (`CnctQsList`, `contactPool`, `qCount`) and mid-point waiting data; `exploded_analysis/05_queue_stuff.analysis.md` highlights it as the anchor between call data and slot assignment. These foundational files store everything that subsequent routines read when balancing staffing, routing, and timing.

## 2. Staffing Automation & Agent Lifecycle (Files 20–35, 45, 33)

The simulator continuously adjusts agent staffing to meet occupancy goals. `21_set_up_staffing_levels_for_the_interval.pde` and `23_increase_staffing_levels_if_necessary.pde` set the baseline numbers for each interval based on planned staffing tables from `04_agent_group_stuff`. `exploded_analysis/21_set_up_staffing_levels_for_the_interval.analysis.md` describes how interval targets are computed, while `exploded_analysis/23_increase_staffing_levels_if_necessary.analysis.md` explains the reactive increase when demand spikes.

Agent status transitions occur through several files:

- `25_log_out_if_so_switch_them_to_active_state_so_they_stay_on.pde` keeps on-call agents available so that the queue always has resources (`exploded_analysis/25…`).
- `32_are_currently_on_a_call_set_them_inactive_so_they_ll.pde` captures agents mid-call needing to be marked unavailable temporarily (`exploded_analysis/32…`).
- `33_log_out_after_this_call.pde` finalizes contacts, releasing agents back to the pool.
- `34_i_am_the_best_call.pde` and `38_set_a_random_aht_between_aht_1_aht_variance_aht_1.pde` introduce randomness in assignment and handle per-contact AHT variation (`exploded_analysis/34…`, `exploded_analysis/38…`).

By splitting staffing logic into these files, the sketch emulates real-world contact-center behavior: evaluate demand, adjust staffing, handle mid-call transitions, and randomize call durations. The exploded analysis entries record this choreography, so reviewers can read two paragraphs before diving into the actual code.

## 3. Contact Routing & Queue Management (`37_queue_call.pde`, `27_available_queue...`, `38_set_a_random...`)

Contacts travel through a queue `CnctQ` structure that is iterated by `47_queue_iterator.pde` (see `exploded_analysis/47_queue_iterator.analysis.md`). The queue iterator advances contacts and triggers call events, consulting `37_queue_call.pde` to match each caller with an available agent when they reach the head of their assigned queue. The random AHT generator (`38_set_a_random_aht_between_aht_1_aht_variance_aht_1.pde`) influences when agents finish and release, affecting occupancy via scheduler loops described earlier.

Macros like `27_available_queue_add_agents.pde` and `31_if_there_weren't_enough_available_agents_find_agents_that.pde` adjust how many agents re-enter the queue, ensuring that newly freed agents are reused before new staffing adjustments (`exploded_analysis/27…`, `exploded_analysis/31…`). The queue logic also enforces priorities: `29_dump_as_many_available_agents_as_possible.pde` and `28_if_true_then_we_need_to_get_rid_of_some_agents.pde` show how the sketch caps overstaffing when demand drops.

## 4. Timing, Repetitions, and Intervals (`40`–`44`, `41`, `42`, `43`, `17_end...`)

Time advances in discrete ticks via `simTick` and `intSecond`. Files `41_check_to_see_if_the_interval_is_beginning_ending.pde` through `43_check_to_see_if_the_simulation_is_beginning_ending.pde` orchestrate interval and repetition boundaries, invoking `21_set_up_staffing_levels…` every interval start and signaling `17_end_no_scroll…` to finalize a run. Their analyses highlight that these routines coordinate logic with the UI state: the simulator only makes staffing decisions at those boundaries, allowing players to observe the results between intervals.

`18_apparently_this_doesn_t_do_a_darn_thing.pde` and the repeated `dumpstats` sections (53–60) appear to serve as placeholders or telemetry emitters; each has an analysis file (`exploded_analysis/18...`, `exploded_analysis/53...` etc.) noting this vagueness, which suggests they may have been scaffolding for future reporting or debugging.

## 5. UI, Controls, and Reporting (`02_main_stuff`, `12_no_scroll…`, `07_reporting…`)

`TabBox[] TabBoxes`, `Slider speedSlider`, and `radioButton[] goalButtons` declared early let the user toggle views, control playback speed, and set goal-seeking behavior. Files `12_no_scroll_no_scroll_no_scroll_no_scroll.pde` and `17_end_no_scroll` through `18` handle the display logic when no scrollable UI is active (see `exploded_analysis/12…` and `exploded_analysis/17…`). The reporting pipeline lives in `07_reporting_stuff_reporting_stuff…` plus the dumpstats derivatives; `exploded_analysis/07…analysis.md` records that these sections emit console or file reports for debugging, while the `exploded_analysis/53…` notes imply multiple redundant dumps, probably to log different partitions of the agent queue.

## 6. Using the Exploded & Analysis Assets

`simapp_exploded/README.md` lists each chunk and its length, enabling you to open the exact portion of the sketch you care about (e.g., `simapp_exploded/23_increase_staffing_levels_if_necessary.pde` for staffing). `exploded_analysis/index.md` provides 1–2 sentence summaries so you understand each file’s focus without reading the code first. This two-tier structure lets you approach detailed review in manageable steps.

## 7. Suggested Next Actions

1. **Isolate policy logic** – rewrite the staffing adjustments (files 21, 23, 25, 31, 33) as pure functions or Python modules. The analysis notes mark them as cohesive pieces; extracting them reduces complexity and enables unit tests.
2. **Consolidate reporting** – replace the `dumpstats` multitude (53–60) with a single exporter that writes structured JSON/CSV, referencing `exploded_analysis/53…` to capture each previous channel’s intent.
3. **Document control flow** – use the exploded files to create flow diagrams: start at `02_main_stuff`, follow `41/42/43` for timing, branch into staffing (`21–33`), and finish with `47_queue_iterator`.

Pick any chunk numbered in `simapp_exploded/README.md` and I can expand this document with pseudocode or detailed interpreter notes for that specific slice.
