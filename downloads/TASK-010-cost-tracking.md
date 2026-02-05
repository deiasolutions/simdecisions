# TASK-010: Cost Tracking

## Status: PENDING
## Assignee: BEE-001
## Effort: 3-4 hours
## Priority: P0
## Depends: TASK-009

---

## Objective

Track token usage and estimated cost per task and in aggregate.

---

## Create `runtime/costing.py`

```python
from datetime import datetime

# Provider rates (per 1M tokens) - Jan 2026
RATES = {
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "local": {"input": 0.00, "output": 0.00},
    "cli": {"input": 0.00, "output": 0.00},
    "default": {"input": 1.00, "output": 5.00}
}

def estimate_cost(provider: str, input_tokens: int = 0, output_tokens: int = 0) -> float:
    """Estimate cost in USD."""
    rates = RATES.get(provider, RATES["default"])
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return round(input_cost + output_cost, 6)

def get_provider_rates() -> dict:
    """Return all provider rates."""
    return RATES.copy()

def create_metrics(provider: str = "default") -> dict:
    """Create initial metrics object for a task."""
    return {
        "provider": provider,
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": None,
        "duration_seconds": None
    }

def update_metrics(metrics: dict, input_tokens: int = 0, output_tokens: int = 0) -> dict:
    """Update metrics with new token counts."""
    metrics["input_tokens"] += input_tokens
    metrics["output_tokens"] += output_tokens
    metrics["estimated_cost_usd"] = estimate_cost(
        metrics["provider"],
        metrics["input_tokens"],
        metrics["output_tokens"]
    )
    return metrics

def complete_metrics(metrics: dict) -> dict:
    """Mark metrics as complete with duration."""
    metrics["completed_at"] = datetime.utcnow().isoformat() + "Z"
    if metrics.get("created_at"):
        start = datetime.fromisoformat(metrics["created_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(metrics["completed_at"].replace("Z", "+00:00"))
        metrics["duration_seconds"] = (end - start).total_seconds()
    return metrics
```

---

## Wire into `server.py`

```python
from runtime.costing import create_metrics, update_metrics, complete_metrics, estimate_cost

# In create_task() - add metrics to payload:
payload["metrics"] = create_metrics(routing.provider)

# In complete_task_endpoint() - finalize metrics:
# (load task, update metrics, save)
task_data["metrics"] = complete_metrics(task_data.get("metrics", {}))
```

---

## Update `/api/summary`

```python
@app.get("/api/summary")
def get_summary() -> Dict:
    summary = _message_store.get_summary()
    
    # Aggregate costs from messages
    total_tokens = 0
    total_cost = 0.0
    by_provider = {}
    
    for msg in _message_store.get_messages(limit=1000):
        tokens = msg.get("token_count", 0)
        provider = msg.get("provider", "default")
        cost = estimate_cost(provider, output_tokens=tokens)
        
        total_tokens += tokens
        total_cost += cost
        
        if provider not in by_provider:
            by_provider[provider] = {"tokens": 0, "cost": 0.0}
        by_provider[provider]["tokens"] += tokens
        by_provider[provider]["cost"] += cost
    
    summary["cost"] = {
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(total_cost, 6),
        "by_provider": by_provider
    }
    
    return summary
```

---

## Done When

- [ ] `runtime/costing.py` exists
- [ ] Task files include `metrics` object
- [ ] `/api/summary` returns cost totals
- [ ] Cost breakdown by provider
