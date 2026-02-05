# SPEC-Tribunal-SDK: Python SDK for Tribunal Operations

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Q33N (Dave) + BEE-001
**Version:** 0.1.0

---

## Purpose

A lightweight Python SDK that any bee can use to interact with the Tribunal API. Designed to be simple enough that bees can write and execute it inline, or import as a module.

---

## Installation

```bash
# From repo (recommended)
pip install -e ./tribunal_sdk

# Or just copy the single file
cp tribunal_sdk/client.py ./
```

---

## Quick Start

```python
from tribunal_sdk import TribunalClient

# Initialize with API key
client = TribunalClient(
    api_key="your-api-key",
    base_url="https://hive.deiasolutions.com/api/v1"  # or local
)

# Test connection
client.ping()  # Returns {"status": "ok", "judge_id": "Q33N-ANTHROPIC"}

# Get PR for review
pr = client.get_pr(42)

# Submit verdict
verdict = client.submit_verdict(
    pr_number=42,
    scores={"I": 1, "N": 1, "V": 0, "E": 1, "S": 1, "T": 1},
    vote="APPROVE",
    summary="Clean implementation of export feature.",
    notes="Consider edge case for empty data."
)
```

---

## API Reference

### TribunalClient

```python
class TribunalClient:
    """
    Client for Tribunal API operations.

    Args:
        api_key: Your tribunal API key (or set TRIBUNAL_API_KEY env var)
        base_url: Hive Control Plane URL (default: from HIVE_API_URL env var)
        timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        timeout: int = 30
    ):
        self.api_key = api_key or os.environ.get("TRIBUNAL_API_KEY")
        self.base_url = base_url or os.environ.get("HIVE_API_URL", "http://localhost:8000/api/v1")
        self.timeout = timeout
```

---

### ping()

Test API connection and verify credentials.

```python
def ping(self) -> dict:
    """
    Test connection and verify API key.

    Returns:
        {
            "status": "ok",
            "judge_id": "Q33N-ANTHROPIC",
            "permissions": ["tribunal:read", "tribunal:write"]
        }

    Raises:
        TribunalAuthError: Invalid API key
        TribunalConnectionError: Cannot reach server
    """
```

**Example:**
```python
result = client.ping()
print(f"Connected as {result['judge_id']}")
```

---

### get_pr()

Fetch PR details for review.

```python
def get_pr(
    self,
    pr_number: int,
    repo: str = "deiasolutions/simdecisions"
) -> PRDetails:
    """
    Get PR details for tribunal review.

    Args:
        pr_number: GitHub PR number
        repo: Repository in "owner/repo" format

    Returns:
        PRDetails object with:
            - number: int
            - title: str
            - author: str
            - created_at: datetime
            - url: str
            - diff: str (full diff text)
            - files_changed: List[str]
            - additions: int
            - deletions: int
            - linked_task: Optional[str]  # e.g., "TASK-009"
            - linked_spec: Optional[str]  # e.g., "ADR-001"
            - labels: List[str]
            - existing_reviews: List[dict]  # Other judges' verdicts

    Raises:
        TribunalNotFoundError: PR doesn't exist
    """
```

**Example:**
```python
pr = client.get_pr(42)
print(f"Reviewing: {pr.title}")
print(f"Author: {pr.author}")
print(f"Files changed: {len(pr.files_changed)}")
print(f"Linked to: {pr.linked_task}")
```

---

### submit_verdict()

Submit your tribunal verdict.

```python
def submit_verdict(
    self,
    pr_number: int,
    scores: dict,
    vote: str,
    summary: str,
    notes: str = "",
    spec_feedback: List[dict] = None,
    repo: str = "deiasolutions/simdecisions"
) -> VerdictResult:
    """
    Submit tribunal verdict for a PR.

    Args:
        pr_number: GitHub PR number
        scores: INVEST scores dict, e.g.:
            {
                "intent": 1,      # or "I": 1
                "narrow": 1,      # or "N": 1
                "verifiable": 0,  # or "V": 0
                "evident": 1,     # or "E": 1
                "safe": 1,        # or "S": 1
                "traceable": 1    # or "T": 1
            }
        vote: "APPROVE" | "REQUEST_CHANGES" | "ABSTAIN"
        summary: 2-3 sentence summary of your assessment
        notes: Detailed feedback for submitter (optional)
        spec_feedback: List of spec feedback items (optional):
            [
                {
                    "spec_ref": "ADR-001",
                    "section": "4.2",  # optional
                    "category": "gap",  # ambiguity|gap|conflict|improvement
                    "summary": "Missing pagination guidance",
                    "priority": "low"  # low|medium|high|critical
                }
            ]
        repo: Repository in "owner/repo" format

    Returns:
        VerdictResult with:
            - id: str (verdict ID)
            - submitted_at: datetime
            - total_score: int
            - consensus_status: str  # "pending" | "passed" | "failed"

    Raises:
        TribunalValidationError: Invalid scores or vote
        TribunalConflictError: Already submitted verdict for this PR
    """
```

**Example:**
```python
verdict = client.submit_verdict(
    pr_number=42,
    scores={
        "I": 1, "N": 1, "V": 0, "E": 1, "S": 1, "T": 1
    },
    vote="APPROVE",
    summary="Implements CSV export per ADR-001. Clean, focused change.",
    notes="Line 45: consider handling empty dataset edge case.",
    spec_feedback=[
        {
            "spec_ref": "ADR-001",
            "category": "gap",
            "summary": "No guidance on max export size",
            "priority": "low"
        }
    ]
)

print(f"Verdict {verdict.id} submitted")
print(f"Total score: {verdict.total_score}/6")
```

---

### get_tribunal_status()

Check current tribunal status for a PR.

```python
def get_tribunal_status(
    self,
    pr_number: int,
    repo: str = "deiasolutions/simdecisions"
) -> TribunalStatus:
    """
    Get current tribunal status for a PR.

    Returns:
        TribunalStatus with:
            - pr_number: int
            - status: "pending" | "reviewing" | "passed" | "failed"
            - judges: {
                "Q33N-GEMINI": {"voted": True, "vote": "APPROVE", "score": 5},
                "Q33N-CODEX": {"voted": True, "vote": "REQUEST_CHANGES", "score": 2},
                "Q33N-ANTHROPIC": {"voted": False}
              }
            - total_score: int (sum of all judge scores)
            - max_score: int (18)
            - consensus: Optional[str]  # "pass" | "fail" | None if pending
            - spec_feedback_count: int
    """
```

**Example:**
```python
status = client.get_tribunal_status(42)
print(f"Status: {status.status}")
print(f"Score: {status.total_score}/{status.max_score}")
for judge, info in status.judges.items():
    if info["voted"]:
        print(f"  {judge}: {info['vote']} ({info['score']}/6)")
    else:
        print(f"  {judge}: pending")
```

---

### list_pending_reviews()

Get list of PRs awaiting your review.

```python
def list_pending_reviews(
    self,
    repo: str = "deiasolutions/simdecisions"
) -> List[PendingReview]:
    """
    List PRs awaiting your review.

    Returns:
        List of PendingReview with:
            - pr_number: int
            - title: str
            - author: str
            - created_at: datetime
            - deadline: datetime
            - priority: str  # "normal" | "urgent"
    """
```

**Example:**
```python
pending = client.list_pending_reviews()
for pr in pending:
    print(f"PR #{pr.pr_number}: {pr.title} (due: {pr.deadline})")
```

---

## Data Classes

```python
@dataclass
class PRDetails:
    number: int
    title: str
    author: str
    created_at: datetime
    url: str
    diff: str
    files_changed: List[str]
    additions: int
    deletions: int
    linked_task: Optional[str]
    linked_spec: Optional[str]
    labels: List[str]
    existing_reviews: List[dict]

@dataclass
class VerdictResult:
    id: str
    submitted_at: datetime
    total_score: int
    consensus_status: str

@dataclass
class TribunalStatus:
    pr_number: int
    status: str
    judges: dict
    total_score: int
    max_score: int
    consensus: Optional[str]
    spec_feedback_count: int

@dataclass
class PendingReview:
    pr_number: int
    title: str
    author: str
    created_at: datetime
    deadline: datetime
    priority: str
```

---

## Exceptions

```python
class TribunalError(Exception):
    """Base exception for tribunal SDK"""
    pass

class TribunalAuthError(TribunalError):
    """Invalid or missing API key"""
    pass

class TribunalConnectionError(TribunalError):
    """Cannot connect to Hive Control Plane"""
    pass

class TribunalNotFoundError(TribunalError):
    """Resource not found (PR, verdict, etc.)"""
    pass

class TribunalValidationError(TribunalError):
    """Invalid input (bad scores, invalid vote, etc.)"""
    pass

class TribunalConflictError(TribunalError):
    """Conflict (e.g., already submitted verdict)"""
    pass
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRIBUNAL_API_KEY` | Your judge API key | (required) |
| `HIVE_API_URL` | Hive Control Plane base URL | `http://localhost:8000/api/v1` |
| `TRIBUNAL_TIMEOUT` | Request timeout seconds | `30` |

---

## Inline Usage (No Install)

For bees that want to use the SDK without installing, here's a minimal inline version:

```python
import os
import requests

class TribunalClient:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ["TRIBUNAL_API_KEY"]
        self.base_url = base_url or os.environ.get("HIVE_API_URL", "http://localhost:8000/api/v1")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def ping(self):
        r = requests.get(f"{self.base_url}/tribunal/ping", headers=self.headers)
        r.raise_for_status()
        return r.json()

    def get_pr(self, pr_number, repo="deiasolutions/simdecisions"):
        r = requests.get(
            f"{self.base_url}/tribunal/pr/{pr_number}",
            params={"repo": repo},
            headers=self.headers
        )
        r.raise_for_status()
        return r.json()

    def submit_verdict(self, pr_number, scores, vote, summary, notes="", spec_feedback=None):
        r = requests.post(
            f"{self.base_url}/tribunal/verdict",
            json={
                "pr_number": pr_number,
                "scores": scores,
                "vote": vote,
                "summary": summary,
                "notes": notes,
                "spec_feedback": spec_feedback or []
            },
            headers=self.headers
        )
        r.raise_for_status()
        return r.json()

# Usage
client = TribunalClient()
pr = client.get_pr(42)
client.submit_verdict(42, {"I":1,"N":1,"V":0,"E":1,"S":1,"T":1}, "APPROVE", "LGTM")
```

---

## File-Based Fallback

If API is unavailable, bees can use file-based communication:

### Reading PR Review Requests

```python
import yaml
from pathlib import Path

def get_pending_reviews_from_files():
    pending_dir = Path(".deia/hive/tribunal/pending")
    reviews = []
    for f in pending_dir.glob("PR-*-review-request.yaml"):
        with open(f) as fp:
            reviews.append(yaml.safe_load(fp))
    return reviews
```

### Writing Verdict Files

```python
import yaml
from datetime import datetime

def write_verdict_file(pr_number, judge_id, scores, vote, summary, notes):
    verdict = {
        "pr_number": pr_number,
        "judge_id": judge_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "scores": scores,
        "vote": vote,
        "summary": summary,
        "notes": notes
    }

    path = f".deia/hive/tribunal/verdicts/PR-{pr_number:03d}-{judge_id}-verdict.yaml"
    with open(path, "w") as f:
        yaml.dump(verdict, f, default_flow_style=False)
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tribunal/ping` | Test connection |
| GET | `/tribunal/pr/{number}` | Get PR details |
| GET | `/tribunal/pr/{number}/status` | Get tribunal status |
| POST | `/tribunal/verdict` | Submit verdict |
| GET | `/tribunal/pending` | List pending reviews |
| GET | `/tribunal/verdicts/{id}` | Get specific verdict |

---

## References

- SPEC-Tribunal-Onboarding: Judge onboarding guide
- BOK-REVIEW-001: Full tribunal pattern
- ADR-006: Hive Control Plane API

---

*"Simple enough to inline. Powerful enough to scale."*
