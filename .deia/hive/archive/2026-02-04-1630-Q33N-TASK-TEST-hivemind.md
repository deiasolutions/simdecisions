# TASK: Test HiveMind Server

**Issued by:** Q33N (Dave)
**Date:** 2026-02-04
**Assigned to:** BEE-001
**Priority:** MEDIUM
**Effort:** 30 min

---

## Objective

Verify HiveMind server runs correctly after refactoring. Run test suite and report results.

---

## Steps

### 1. Start the HiveMind Server

```bash
cd C:\Users\davee\OneDrive\Documents\GitHub\deiasolutions-2
python -m deia.hivemind.runtime.server
```

Server should start on port 8010. Watch for startup errors.

### 2. Run Test Suite

In a separate terminal:

```bash
cd C:\Users\davee\OneDrive\Documents\GitHub\simdecisions
python tests/test_hivemind_server.py
```

### 3. Report Results

Document in your response:
- Did server start cleanly?
- Any startup warnings/errors?
- Test results (passed/failed count)
- Any failing endpoints - note which ones and error messages

---

## Acceptance Criteria

- [ ] Server starts without import errors
- [ ] Health endpoint responds
- [ ] Test script runs to completion
- [ ] Results documented in hive response

---

## Notes

- Server was refactored recently - first run since changes
- Some endpoints (like /api/ledger) may 404 - that's expected until TASK-009 is done
- If server fails to start, capture the full traceback

---

**Status:** PENDING — Ready for BEE-001 to claim

*Issued under human sovereignty.*
