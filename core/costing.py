"""
Costing module - Token usage and cost estimation.

Migrated from deiasolutions (original) during metamorphosis gap remediation.
Original: simdecisions/runtime/costing.py
Migration Date: 2026-02-03
"""

from datetime import datetime, timezone
from typing import Dict, Optional

# Provider rates (per 1M tokens)
# Updated 2026-02-03 with current pricing
RATES = {
    # Claude models (Anthropic)
    "claude-opus-4-5": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},

    # OpenAI models
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},

    # Google models
    "gemini-pro": {"input": 0.50, "output": 1.50},
    "gemini-ultra": {"input": 7.00, "output": 21.00},

    # Local/free models
    "local": {"input": 0.00, "output": 0.00},
    "ollama": {"input": 0.00, "output": 0.00},
    "cli": {"input": 0.00, "output": 0.00},

    # Fallback
    "default": {"input": 1.00, "output": 5.00}
}


def estimate_cost(provider: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate cost in USD for a given provider and token counts.

    Args:
        provider: Model/provider name (e.g., "claude-sonnet-4")
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens

    Returns:
        Estimated cost in USD (rounded to 6 decimal places)
    """
    rates = RATES.get(provider, RATES["default"])
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return round(input_cost + output_cost, 6)


def calculate_duration(start_time: str, end_time: str) -> float:
    """
    Calculate duration in seconds between two ISO timestamps.

    Args:
        start_time: ISO format timestamp (e.g., "2026-02-01T10:00:00Z")
        end_time: ISO format timestamp

    Returns:
        Duration in seconds
    """
    start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    return (end - start).total_seconds()


def get_rate(provider: str) -> Dict[str, float]:
    """Get the rate table for a provider."""
    return RATES.get(provider, RATES["default"])


def list_providers() -> list:
    """List all known providers."""
    return [k for k in RATES.keys() if k != "default"]


class TaskMetrics:
    """
    Metrics collector for a single task.

    Tracks token usage, timing, and calculates costs.
    """

    def __init__(self, task_id: str, provider: str = "default"):
        self.task_id = task_id
        self.provider = provider
        self.input_tokens = 0
        self.output_tokens = 0
        self.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.completed_at: Optional[str] = None

    def add_tokens(self, input_tokens: int, output_tokens: int):
        """Add token counts from an API call."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def complete(self):
        """Mark the task as complete with current timestamp."""
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost(self) -> float:
        """Estimated cost in USD."""
        return estimate_cost(self.provider, self.input_tokens, self.output_tokens)

    @property
    def duration(self) -> Optional[float]:
        """Duration in seconds, or None if not complete."""
        if self.completed_at:
            return calculate_duration(self.created_at, self.completed_at)
        return None

    def to_dict(self) -> dict:
        """Export metrics as dictionary."""
        return {
            "task_id": self.task_id,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration
        }


class SessionMetrics:
    """
    Aggregate metrics across multiple tasks in a session.

    Added in Method B migration for better session-level tracking.
    """

    def __init__(self, session_id: str, provider: str = "default"):
        self.session_id = session_id
        self.provider = provider
        self.tasks: Dict[str, TaskMetrics] = {}
        self.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def start_task(self, task_id: str) -> TaskMetrics:
        """Start tracking a new task."""
        task = TaskMetrics(task_id, self.provider)
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[TaskMetrics]:
        """Get metrics for a specific task."""
        return self.tasks.get(task_id)

    @property
    def total_input_tokens(self) -> int:
        return sum(t.input_tokens for t in self.tasks.values())

    @property
    def total_output_tokens(self) -> int:
        return sum(t.output_tokens for t in self.tasks.values())

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_cost(self) -> float:
        return sum(t.estimated_cost for t in self.tasks.values())

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "provider": self.provider,
            "task_count": len(self.tasks),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost,
            "created_at": self.created_at,
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()}
        }


# For testing
if __name__ == "__main__":
    print("=== Costing Module Test ===
")

    # Test RATES
    print("1. RATES dict:")
    print(f"   claude-sonnet-4 rates: {RATES['claude-sonnet-4']}")
    print(f"   claude-opus-4-5 rates: {RATES['claude-opus-4-5']}")

    # Test estimate_cost
    print("
2. estimate_cost:")
    cost = estimate_cost("claude-sonnet-4", 1000, 500)
    print(f"   1000 in + 500 out = ${cost:.6f}")

    # Test calculate_duration
    print("
3. calculate_duration:")
    dur = calculate_duration("2026-02-01T10:00:00Z", "2026-02-01T10:05:00Z")
    print(f"   5 min = {dur}s")

    # Test TaskMetrics
    print("
4. TaskMetrics:")
    tm = TaskMetrics("TASK-001", "claude-sonnet-4")
    tm.add_tokens(1000, 500)
    tm.complete()
    print(f"   {tm.to_dict()}")

    # Test SessionMetrics
    print("
5. SessionMetrics:")
    sm = SessionMetrics("SESSION-001", "claude-sonnet-4")
    t1 = sm.start_task("TASK-001")
    t1.add_tokens(1000, 500)
    t1.complete()
    t2 = sm.start_task("TASK-002")
    t2.add_tokens(2000, 1000)
    t2.complete()
    print(f"   Total cost: ${sm.total_cost:.6f}")
    print(f"   Total tokens: {sm.total_tokens}")

    print("
[OK] All tests passed")
