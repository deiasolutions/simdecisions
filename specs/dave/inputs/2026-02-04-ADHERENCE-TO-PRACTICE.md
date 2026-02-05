# Adherence to Practice — Spec Addendum

**From:** Q33N (Dave)
**Date:** 2026-02-04
**Type:** Enforcement reminder and PyBee addendum
**Status:** OFFICIAL

---

## The Problem

Bees (LLM and PyBee) are not consistently following established DEIA processes. This causes:

- Loss of visibility (no one knows what you're doing)
- Duplicate work (multiple bees grab same task)
- Lost context (crashes lose all progress)
- Broken audit trail (no proof of work)

---

## Mandatory Processes (Already Exist)

All bees MUST read and follow these from the mothership:

| Process | Location | Summary |
|---------|----------|---------|
| **PROCESS-0001** | `deiasolutions/.deia/processes/` | Always check for existing process first |
| **PROCESS-0002** | `deiasolutions/.deia/processes/` | Task state machine: queue→claimed→buzz→archive |
| **PROCESS-0004** | `deiasolutions/.deia/processes/` | Activity logging every 30 min (YOUR responsibility) |

---

## Violations Observed This Session (BEE-001)

| Violation | Rule Broken |
|-----------|-------------|
| No activity log file created | PROCESS-0004 |
| No progress logged during 2+ hours of work | PROCESS-0004 |
| Did not `/claim` task before starting | PROCESS-0002 |
| Did not follow queue→claimed→buzz state machine | PROCESS-0002 |
| Did not check processes before starting work | PROCESS-0001 |

---

## Corrective Actions Required

### Immediate (BEE-001 this session):

1. Create `.deia/bot-logs/BEE-001-activity.jsonl`
2. Log session start and all work done retroactively
3. Log going forward every 20-30 minutes
4. Follow proper task state machine for future tasks

### Structural (for PyBee spec addendum):

PyBees MUST also adhere to these processes:

```python
# In every PyBee execution:
# 1. Log start to activity log
# 2. Log completion to activity log
# 3. Do not take work from other bees (check claimed/ first)
# 4. Output must follow response format
```

---

## PyBee Adherence Requirements (Addendum to SPEC-PyBee)

Add to Section 5.2 (Subprocess Execution):

```python
def execute_pybee(pybee_id: str, task_payload: Dict) -> Dict:
    # ADHERENCE: Log start
    log_activity(pybee_id, "task_started", task_payload.get("task_id"))

    # ... execution ...

    # ADHERENCE: Log completion
    log_activity(pybee_id, "task_completed", task_payload.get("task_id"))

    return result
```

Add to Section 10 (Security Considerations):

| Rule | Enforcement |
|------|-------------|
| Don't take other bee's work | Check `claimed/` before grabbing from `queue/` |
| Log all activity | Write to `.deia/bot-logs/{PYBEE-ID}-activity.jsonl` |
| Follow task state machine | Must `/claim` before work, `/complete` after |

---

## Enforcement

| Violation | Consequence |
|-----------|-------------|
| No logging for 30+ min | Warning |
| No logging for 60+ min | Work may be reassigned |
| Taking claimed task | Immediate escalation |
| Fabricated logs | Integrity violation, severe |
| Repeated process violations | Role reassignment |

---

## Q33N Reminder

> **"The processes exist. Read them. Follow them. No exceptions."**

---

*Issued under Q33N authority. All bees — LLM and PyBee — must comply.*
