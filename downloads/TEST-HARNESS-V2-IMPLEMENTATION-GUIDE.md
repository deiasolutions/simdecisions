# Test Harness V2 - Complete Implementation Guide

**Date:** 2025-12-18
**Status:** APPROVED - Ready for implementation
**Priority:** HIGH

---

## Executive Summary

Build a unified test harness that validates RAG retrieval across four mechanisms, uses 100-point scoring, supports Opus-calibrated expectations with versioning, and produces actionable reports. This replaces the current ad-hoc testing with a production-grade validation system.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [File Structure](#2-file-structure)
3. [100-Point Scoring System](#3-100-point-scoring-system)
4. [Expectation Versioning](#4-expectation-versioning)
5. [Test Bank Schemas](#5-test-bank-schemas)
6. [Module Specifications](#6-module-specifications)
7. [API Endpoints](#7-api-endpoints)
8. [Implementation Order](#8-implementation-order)
9. [Critical Requirements](#9-critical-requirements)
10. [Success Criteria](#10-success-criteria)

---

## 1. Architecture Overview

### 1.1 Four Test Mechanisms

The KB contains different entity types that are retrieved/loaded via different mechanisms. Each needs its own test approach:

| Mechanism | Entity Types | How It Works | Test Bank |
|-----------|--------------|--------------|-----------|
| **Semantic** | KNOWLEDGE, SCRIPT | Voyage embedding → Haiku ranking | parent_test_bank.json |
| **State** | HANDLER (state-based) | User state condition evaluation | state_handler_tests.json |
| **Pattern** | Crisis, keywords | Regex/keyword matching | pattern_tests.json |
| **Always** | PERSONA, core GUARDRAIL | Always loaded, no retrieval | always_load_tests.json |

### 1.2 Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED TEST RUNNER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│   │   SEMANTIC   │  │    STATE     │  │   PATTERN    │          │
│   │    TESTS     │  │    TESTS     │  │    TESTS     │          │
│   │   (94 tests) │  │  (18 tests)  │  │  (28 tests)  │          │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│          │                 │                 │                   │
│          │    ┌────────────┴────────────┐    │                   │
│          │    │        ALWAYS           │    │                   │
│          │    │        TESTS            │    │                   │
│          │    │       (7 tests)         │    │                   │
│          │    └────────────┬────────────┘    │                   │
│          │                 │                 │                   │
│          └─────────────────┼─────────────────┘                   │
│                            │                                     │
│                            ▼                                     │
│                  ┌─────────────────┐                            │
│                  │    SCORING      │                            │
│                  │   (100-point)   │                            │
│                  └────────┬────────┘                            │
│                           │                                      │
│                           ▼                                      │
│                  ┌─────────────────┐                            │
│                  │   AGGREGATION   │                            │
│                  │ Combined Score  │                            │
│                  │ Health Status   │                            │
│                  └────────┬────────┘                            │
│                           │                                      │
│                           ▼                                      │
│                  ┌─────────────────┐                            │
│                  │    REPORTING    │                            │
│                  │  Markdown + JSON│                            │
│                  └─────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Design Principles

1. **Separation of concerns** - Each test type has its own module
2. **Versioned expectations** - Opus calibration results stored in history, most recent wins
3. **100-point granularity** - Per-item penalties, not letter grades
4. **Critical failure tracking** - Crisis false positives/negatives flagged separately
5. **Reuse existing services** - Adapt VoyageEmbeddingService, RerankerService, etc.

---

## 2. File Structure

```
fbb/backend-v2/src/testing/
├── __init__.py
├── scoring.py                  # 100-point scoring system
├── expectation_loader.py       # Load versioned expectations
├── unified_runner.py           # Main orchestrator
├── semantic_tests.py           # Voyage → Haiku pipeline tests
├── state_tests.py              # State condition evaluation tests
├── pattern_tests.py            # Crisis/keyword pattern tests
├── always_tests.py             # Always-load verification tests
├── reporting.py                # Markdown report generation
├── calibrate.py                # Opus calibration tool
│
├── test_banks/
│   ├── semantic/
│   │   ├── parent_test_bank.json       # 94 semantic tests
│   │   └── history/
│   │       └── expectations_YYYY-MM-DD.json
│   ├── state/
│   │   └── state_handler_tests.json    # 18 state tests
│   ├── pattern/
│   │   ├── pattern_tests.json          # 28 pattern tests
│   │   └── pattern_rules.json          # Crisis patterns + keyword boosts
│   └── always/
│       └── always_load_tests.json      # 7 always tests
│
├── results/
│   └── results_YYYY-MM-DD-HHMM.json    # Saved test runs
│
└── calibration/
    ├── calibration_log.json            # Record of calibration runs
    └── opus_responses/
        └── calibration_YYYY-MM-DD.json
```

---

## 3. 100-Point Scoring System

### 3.1 Core Rules

```python
"""
100-POINT SCORING SYSTEM

Start: 100 points (if primary passes)
Hard Fail: 0 points (if primary fails)

Penalties (stack, per item):
  - Missing expected_secondary:    -10 per item
  - False positive (not_expected): -20 per item
  - Rank check violation:          -10 per violation
  - Wrong handler loaded:          -20 per item

Floor: 0 (cannot go negative)
"""
```

### 3.2 Implementation

```python
# scoring.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ScoreResult:
    score: int
    breakdown: Dict[str, Any]
    is_hard_fail: bool


def calculate_score(results: Dict[str, Any]) -> ScoreResult:
    """
    Calculate 100-point score with per-item penalties.
    
    Args:
        results: Dict containing:
            - primary_pass: bool - Did all primary expected entities appear?
            - secondary_missing: List[str] - Entity IDs that should have appeared but didn't
            - false_positives: List[str] - Entity IDs that appeared but shouldn't have
            - rank_violations: List[Dict] - Rank order violations
            - wrong_handlers: List[str] - (State tests only) Wrong handlers that loaded
    
    Returns:
        ScoreResult with score (0-100), breakdown, and hard_fail flag
    """
    
    # Hard fail check - primary is non-negotiable
    if not results.get("primary_pass", False):
        return ScoreResult(
            score=0,
            breakdown={"primary_fail": True, "reason": "Primary expected entity not found"},
            is_hard_fail=True
        )
    
    score = 100
    breakdown = {}
    
    # Secondary misses: -10 each
    secondary_missing = results.get("secondary_missing", [])
    if secondary_missing:
        penalty = len(secondary_missing) * 10
        score -= penalty
        breakdown["secondary_missing"] = {
            "items": secondary_missing,
            "count": len(secondary_missing),
            "penalty": -penalty
        }
    
    # False positives: -20 each
    false_positives = results.get("false_positives", [])
    if false_positives:
        penalty = len(false_positives) * 20
        score -= penalty
        breakdown["false_positives"] = {
            "items": false_positives,
            "count": len(false_positives),
            "penalty": -penalty
        }
    
    # Rank violations: -10 each
    rank_violations = results.get("rank_violations", [])
    if rank_violations:
        penalty = len(rank_violations) * 10
        score -= penalty
        breakdown["rank_violations"] = {
            "items": rank_violations,
            "count": len(rank_violations),
            "penalty": -penalty
        }
    
    # Wrong handlers (state tests): -20 each
    wrong_handlers = results.get("wrong_handlers", [])
    if wrong_handlers:
        penalty = len(wrong_handlers) * 20
        score -= penalty
        breakdown["wrong_handlers"] = {
            "items": wrong_handlers,
            "count": len(wrong_handlers),
            "penalty": -penalty
        }
    
    # Floor at 0
    score = max(0, score)
    
    return ScoreResult(
        score=score,
        breakdown=breakdown,
        is_hard_fail=False
    )


def interpret_score(score: int) -> str:
    """Map score to human-readable interpretation."""
    if score == 100:
        return "Perfect"
    elif score >= 90:
        return "Minor issue"
    elif score >= 80:
        return "Notable issues"
    elif score >= 70:
        return "Concerning"
    elif score >= 60:
        return "Barely acceptable"
    elif score > 0:
        return "Failing"
    else:
        return "Hard fail"


def get_score_distribution(scores: List[int]) -> Dict[str, int]:
    """Calculate distribution of scores across ranges."""
    distribution = {
        "100": 0,
        "90-99": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "1-59": 0,
        "0": 0
    }
    
    for score in scores:
        if score == 100:
            distribution["100"] += 1
        elif score >= 90:
            distribution["90-99"] += 1
        elif score >= 80:
            distribution["80-89"] += 1
        elif score >= 70:
            distribution["70-79"] += 1
        elif score >= 60:
            distribution["60-69"] += 1
        elif score > 0:
            distribution["1-59"] += 1
        else:
            distribution["0"] += 1
    
    return distribution
```

### 3.3 Score Examples

| Scenario | Calculation | Final Score |
|----------|-------------|-------------|
| Perfect | 100 | 100 |
| 1 secondary miss | 100 - 10 | 90 |
| 1 false positive | 100 - 20 | 80 |
| 2 secondary + 1 rank violation | 100 - 20 - 10 | 70 |
| 1 secondary + 2 false positives | 100 - 10 - 40 | 50 |
| Primary not found | HARD FAIL | 0 |

---

## 4. Expectation Versioning

### 4.1 Purpose

Test expectations are calibrated using Opus 4.5 with full KB content. When expectations change (after recalibration), the history is preserved. Test runner always uses the most recent expectation for each test.

### 4.2 Priority Order

```
1. Human override (clinical judgment trumps Opus)
2. Most recent Opus calibration
3. Original test bank value
```

### 4.3 Implementation

```python
# expectation_loader.py

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ExpectationLoader:
    """
    Load versioned expectations for semantic tests.
    Handles history files, human overrides, and fallback to originals.
    """
    
    def __init__(self, test_bank_path: Path, history_dir: Path):
        self.test_bank_path = test_bank_path
        self.history_dir = history_dir
        self._original_bank = None
        self._history_cache = None
    
    @property
    def original_bank(self) -> Dict:
        """Lazy load original test bank."""
        if self._original_bank is None:
            with open(self.test_bank_path) as f:
                self._original_bank = json.load(f)
        return self._original_bank
    
    @property
    def history_files(self) -> list:
        """Get history files sorted newest first."""
        if not self.history_dir.exists():
            return []
        return sorted(
            self.history_dir.glob("expectations_*.json"),
            reverse=True  # Newest first
        )
    
    def get_expectations(self, test_id: str) -> Dict[str, Any]:
        """
        Get current expectations for a test.
        
        Returns dict with:
            - expected_primary: List[str]
            - expected_secondary: List[str]
            - not_expected: List[str]
            - rank_check: List[Dict]
            - _source: str - Where expectations came from
        """
        
        # Check history files (newest first)
        for history_file in self.history_files:
            with open(history_file) as f:
                history = json.load(f)
            
            for change in history.get("changes", []):
                if change["test_id"] == test_id:
                    # Human override takes precedence
                    if change.get("human_override"):
                        override = change["human_override"]
                        return {
                            "expected_primary": override.get("expected_primary", []),
                            "expected_secondary": override.get("expected_secondary", []),
                            "not_expected": override.get("not_expected", []),
                            "rank_check": override.get("rank_check", []),
                            "_source": f"human_override_{change['human_override'].get('override_date', 'unknown')}"
                        }
                    
                    # Opus calibration
                    updated = change["updated"]
                    return {
                        "expected_primary": updated.get("expected_primary", []),
                        "expected_secondary": updated.get("expected_secondary", []),
                        "not_expected": updated.get("not_expected", []),
                        "rank_check": updated.get("rank_check", []),
                        "_source": f"opus_{history_file.stem.replace('expectations_', '')}"
                    }
        
        # Fallback to original test bank
        for test in self.original_bank.get("tests", []):
            if test["test_id"] == test_id:
                return {
                    "expected_primary": test.get("expected_primary", []),
                    "expected_secondary": test.get("expected_secondary", []),
                    "not_expected": test.get("not_expected", []),
                    "rank_check": test.get("rank_check", []),
                    "_source": "original"
                }
        
        raise ValueError(f"Test {test_id} not found in test bank or history")
    
    def get_test_with_expectations(self, test_id: str) -> Dict[str, Any]:
        """Get full test definition merged with current expectations."""
        
        # Get original test
        original_test = None
        for test in self.original_bank.get("tests", []):
            if test["test_id"] == test_id:
                original_test = test.copy()
                break
        
        if not original_test:
            raise ValueError(f"Test {test_id} not found")
        
        # Merge with current expectations
        expectations = self.get_expectations(test_id)
        original_test.update({
            "expected_primary": expectations["expected_primary"],
            "expected_secondary": expectations["expected_secondary"],
            "not_expected": expectations["not_expected"],
            "rank_check": expectations["rank_check"],
            "_expectation_source": expectations["_source"]
        })
        
        return original_test
    
    def get_expectation_summary(self) -> Dict[str, int]:
        """Summarize where expectations come from."""
        summary = {"original": 0, "opus": 0, "human_override": 0}
        
        for test in self.original_bank.get("tests", []):
            expectations = self.get_expectations(test["test_id"])
            source = expectations["_source"]
            
            if source == "original":
                summary["original"] += 1
            elif source.startswith("human_override"):
                summary["human_override"] += 1
            elif source.startswith("opus"):
                summary["opus"] += 1
        
        return summary
```

### 4.4 History File Schema

```json
{
  "version": "2025-12-18T14:30:00Z",
  "calibration_trigger": "kb_entity_added",
  "kb_version": "v2.1",
  "changes": [
    {
      "test_id": "V2-LOY-001",
      "previous": {
        "expected_primary": ["loyalty_binds"],
        "expected_secondary": ["parental_alienation"],
        "not_expected": ["handler_crisis"],
        "rank_check": []
      },
      "updated": {
        "expected_primary": ["loyalty_binds"],
        "expected_secondary": ["psychological_splitting", "transition_bridge"],
        "not_expected": ["handler_crisis", "biff_response"],
        "rank_check": [{"higher": "loyalty_binds", "lower": "transition_bridge"}]
      },
      "opus_reasoning": "User describes child feeling guilty...",
      "human_override": null
    }
  ],
  "unchanged_count": 87,
  "changed_count": 13
}
```

---

## 5. Test Bank Schemas

### 5.1 Semantic Test Bank

```json
{
  "bank_type": "SEMANTIC",
  "version": "2.0",
  "created": "2025-12-17",
  "description": "Tests for Voyage → Haiku semantic retrieval pipeline",
  "tests": [
    {
      "test_id": "V2-GR-001",
      "name": "Gray rock - provocation bait",
      "category": "one_liner",
      "topics": ["gray_rock"],
      "prompt": "she texts me nonstop just trying to get a reaction",
      "expected_primary": ["gray_rock"],
      "expected_secondary": ["medium_response_time", "biff_response"],
      "not_expected": ["handler_crisis", "domestic_violence"],
      "rank_check": [{"higher": "gray_rock", "lower": "boundary_setting"}],
      "user_state": {}
    }
  ]
}
```

### 5.2 State Handler Test Bank

```json
{
  "bank_type": "STATE",
  "version": "1.0",
  "tests": [
    {
      "test_id": "STATE-001",
      "name": "First conversation triggers welcome handler",
      "user_state": {
        "is_first_conversation": true,
        "days_since_last": null,
        "last_rating": null,
        "user_type": "PARENT"
      },
      "expected_handlers": ["handler_first_conversation"],
      "not_expected_handlers": ["handler_returning_user", "handler_clinician_mode"]
    }
  ]
}
```

### 5.3 Pattern Test Bank

```json
{
  "bank_type": "PATTERN",
  "version": "1.0",
  "tests": [
    {
      "test_id": "PAT-CRISIS-001",
      "name": "Crisis - suicidal ideation explicit",
      "prompt": "i want to end it all",
      "expected_matches": ["handler_crisis"],
      "expected_secondary": ["rule_crisis_detection"],
      "not_expected_matches": [],
      "pattern_type": "crisis",
      "is_critical": true
    }
  ]
}
```

### 5.4 Always Load Test Bank

```json
{
  "bank_type": "ALWAYS",
  "version": "1.0",
  "tests": [
    {
      "test_id": "ALWAYS-001",
      "name": "Parent user has core entities",
      "user_type": "PARENT",
      "user_state": {},
      "expected_always": ["frank_parent_persona", "core_behavioral_guardrails", "user_context"]
    }
  ]
}
```

### 5.5 Pattern Rules File

```json
{
  "crisis_patterns": [
    {
      "pattern": "want(s)? to (die|end it|hurt myself|kill myself)",
      "entities": ["handler_crisis", "rule_crisis_detection"],
      "is_critical": true
    },
    {
      "pattern": "better off (dead|without me)",
      "entities": ["handler_crisis"],
      "is_critical": true
    },
    {
      "pattern": "(not|don't|dont) feel safe",
      "entities": ["handler_crisis"],
      "is_critical": true
    },
    {
      "pattern": "can'?t (go on|take it|do this) anymore",
      "entities": ["handler_crisis"],
      "is_critical": true
    },
    {
      "pattern": "being (hit|abused|hurt)",
      "entities": ["handler_crisis", "domestic_violence"],
      "is_critical": true
    }
  ],
  "keyword_boosts": [
    {"keywords": ["gray rock", "grey rock", "gray-rock"], "entity": "gray_rock"},
    {"keywords": ["biff", "biff response"], "entity": "biff_response"},
    {"keywords": ["parental alienation", "alienation"], "entity": "parental_alienation"},
    {"keywords": ["documentation", "document everything", "keep records"], "entity": "documentation_practices"},
    {"keywords": ["boundaries", "boundary", "set boundaries"], "entity": "boundary_setting"},
    {"keywords": ["loyalty bind", "loyalty conflict", "caught in the middle"], "entity": "loyalty_binds"},
    {"keywords": ["gatekeeping", "gatekeeper"], "entity": "gatekeeping"},
    {"keywords": ["coercive control"], "entity": "coercive_control_detailed"}
  ]
}
```

---

## 6. Module Specifications

### 6.1 semantic_tests.py

```python
"""
Semantic test runner - Tests Voyage → Haiku retrieval pipeline.

Uses existing services:
- VoyageEmbeddingService for candidate retrieval
- RerankerService for Haiku ranking

Integrates with ExpectationLoader for versioned expectations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

from .scoring import calculate_score, ScoreResult
from .expectation_loader import ExpectationLoader


@dataclass
class SemanticTestResult:
    test_id: str
    name: str
    category: str
    topics: List[str]
    prompt: str
    
    # Pipeline results
    voyage_candidates: List[Dict]  # Top 15 from Voyage
    haiku_selections: List[str]    # Final 6 entity_ids from Haiku
    
    # Expectations
    expectations: Dict[str, Any]
    expectation_source: str
    
    # Evaluation
    primary_pass: bool
    secondary_missing: List[str]
    false_positives: List[str]
    rank_violations: List[Dict]
    
    # Score
    score: int
    breakdown: Dict
    is_hard_fail: bool


class SemanticTestRunner:
    """Runs semantic retrieval tests."""
    
    def __init__(
        self,
        voyage_service,      # VoyageEmbeddingService
        reranker_service,    # RerankerService
        expectation_loader: ExpectationLoader,
        test_bank_path: str,
        rate_limit_delay: float = 1.25  # Seconds between Haiku calls
    ):
        self.voyage = voyage_service
        self.reranker = reranker_service
        self.expectations = expectation_loader
        self.rate_limit_delay = rate_limit_delay
        
        with open(test_bank_path) as f:
            self.test_bank = json.load(f)
    
    async def run_test(self, test: Dict) -> SemanticTestResult:
        """Run single semantic test."""
        
        # Get current expectations (may be from history)
        expectations = self.expectations.get_expectations(test["test_id"])
        
        # Run Voyage retrieval
        voyage_candidates = await self.voyage.search_entities(
            query=test["prompt"],
            top_k=15
        )
        
        # Run Haiku ranking
        haiku_results = await self.reranker.rerank(
            query=test["prompt"],
            candidates=voyage_candidates,
            top_k=6
        )
        
        # Extract entity_ids from selections
        haiku_selections = [r["entity_id"] for r in haiku_results]
        
        # Evaluate primary
        primary_pass = all(
            eid in haiku_selections 
            for eid in expectations["expected_primary"]
        )
        
        # Evaluate secondary
        secondary_missing = [
            eid for eid in expectations.get("expected_secondary", [])
            if eid not in haiku_selections
        ]
        
        # Evaluate false positives
        false_positives = [
            eid for eid in expectations.get("not_expected", [])
            if eid in haiku_selections
        ]
        
        # Evaluate rank order
        rank_violations = self._check_rank_order(
            haiku_selections, 
            expectations.get("rank_check", [])
        )
        
        # Calculate score
        score_result = calculate_score({
            "primary_pass": primary_pass,
            "secondary_missing": secondary_missing,
            "false_positives": false_positives,
            "rank_violations": rank_violations
        })
        
        return SemanticTestResult(
            test_id=test["test_id"],
            name=test.get("name", ""),
            category=test.get("category", ""),
            topics=test.get("topics", []),
            prompt=test["prompt"],
            voyage_candidates=voyage_candidates,
            haiku_selections=haiku_selections,
            expectations=expectations,
            expectation_source=expectations["_source"],
            primary_pass=primary_pass,
            secondary_missing=secondary_missing,
            false_positives=false_positives,
            rank_violations=rank_violations,
            score=score_result.score,
            breakdown=score_result.breakdown,
            is_hard_fail=score_result.is_hard_fail
        )
    
    async def run_all(self, verbose: bool = False) -> List[SemanticTestResult]:
        """Run all semantic tests with rate limiting."""
        results = []
        total = len(self.test_bank["tests"])
        
        for i, test in enumerate(self.test_bank["tests"], 1):
            if verbose:
                print(f"[{i}/{total}] {test['test_id']}: {test.get('name', '')[:50]}")
            
            result = await self.run_test(test)
            results.append(result)
            
            if verbose:
                status = "✓" if result.score == 100 else f"Score: {result.score}"
                print(f"         {status}")
            
            # Rate limiting
            if i < total:
                await asyncio.sleep(self.rate_limit_delay)
        
        return results
    
    async def run_by_topic(self, topic: str) -> List[SemanticTestResult]:
        """Run tests for specific topic."""
        tests = [
            t for t in self.test_bank["tests"]
            if topic in t.get("topics", [])
        ]
        
        results = []
        for test in tests:
            result = await self.run_test(test)
            results.append(result)
            await asyncio.sleep(self.rate_limit_delay)
        
        return results
    
    def _check_rank_order(
        self, 
        selections: List[str], 
        rank_checks: List[Dict]
    ) -> List[Dict]:
        """Check if rank order constraints are satisfied."""
        violations = []
        
        for check in rank_checks:
            higher = check["higher"]
            lower = check["lower"]
            
            # Both must be in selections to check
            if higher not in selections or lower not in selections:
                continue
            
            higher_idx = selections.index(higher)
            lower_idx = selections.index(lower)
            
            if higher_idx > lower_idx:  # Higher should have lower index (ranked higher)
                violations.append({
                    "expected_higher": higher,
                    "expected_lower": lower,
                    "actual_higher_rank": higher_idx + 1,
                    "actual_lower_rank": lower_idx + 1
                })
        
        return violations
```

### 6.2 state_tests.py

```python
"""
State handler test runner - Tests user state condition matching.

Handlers are triggered by user_state conditions, not semantic similarity.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from .scoring import calculate_score, ScoreResult


# State conditions for each handler
# TODO: Later move to DB in state_conditions JSONB field
STATE_CONDITIONS = {
    "handler_first_conversation": {
        "is_first_conversation": {"eq": True}
    },
    "handler_returning_user": {
        "is_first_conversation": {"eq": False},
        "days_since_last": {"gte": 7}
    },
    "handler_post_escalation": {
        "is_first_conversation": {"eq": False},
        "last_rating": {"lte": 2}
    },
    "handler_celebrating_wins": {
        "is_first_conversation": {"eq": False},
        "last_rating": {"gte": 4}
    },
    "handler_clinician_mode": {
        "user_type": {"in": ["CLINICIAN", "PROFESSIONAL"]}
    },
    "handler_interaction_debrief": {
        "is_first_conversation": {"eq": False},
        "has_pending_debrief": {"eq": True}
    }
}


@dataclass
class StateTestResult:
    test_id: str
    name: str
    user_state: Dict
    
    triggered_handlers: List[str]
    expected_handlers: List[str]
    not_expected_handlers: List[str]
    
    primary_pass: bool
    wrong_handlers: List[str]
    
    score: int
    breakdown: Dict
    is_hard_fail: bool


class StateMatcher:
    """Evaluates user state against handler conditions."""
    
    def __init__(self, conditions: Dict = None):
        self.conditions = conditions or STATE_CONDITIONS
    
    def evaluate(self, user_state: Dict) -> List[str]:
        """Return list of handler entity_ids that should trigger."""
        triggered = []
        
        for handler_id, conditions in self.conditions.items():
            if self._matches(user_state, conditions):
                triggered.append(handler_id)
        
        return triggered
    
    def _matches(self, user_state: Dict, conditions: Dict) -> bool:
        """Check if user_state matches all conditions."""
        for field, constraint in conditions.items():
            value = user_state.get(field)
            
            if not self._check_constraint(value, constraint):
                return False
        
        return True
    
    def _check_constraint(self, value: Any, constraint: Dict) -> bool:
        """Check single constraint."""
        for op, expected in constraint.items():
            if op == "eq":
                if value != expected:
                    return False
            elif op == "gte":
                if value is None or value < expected:
                    return False
            elif op == "lte":
                if value is None or value > expected:
                    return False
            elif op == "in":
                if value not in expected:
                    return False
        
        return True


class StateTestRunner:
    """Runs state handler tests."""
    
    def __init__(self, test_bank_path: str, matcher: StateMatcher = None):
        self.matcher = matcher or StateMatcher()
        
        with open(test_bank_path) as f:
            self.test_bank = json.load(f)
    
    def run_test(self, test: Dict) -> StateTestResult:
        """Run single state test."""
        
        user_state = test["user_state"]
        triggered = self.matcher.evaluate(user_state)
        
        expected = test["expected_handlers"]
        not_expected = test.get("not_expected_handlers", [])
        
        # Evaluate
        primary_pass = all(h in triggered for h in expected)
        wrong_handlers = [h for h in not_expected if h in triggered]
        
        # Calculate score
        score_result = calculate_score({
            "primary_pass": primary_pass,
            "secondary_missing": [],
            "false_positives": [],
            "wrong_handlers": wrong_handlers
        })
        
        return StateTestResult(
            test_id=test["test_id"],
            name=test.get("name", ""),
            user_state=user_state,
            triggered_handlers=triggered,
            expected_handlers=expected,
            not_expected_handlers=not_expected,
            primary_pass=primary_pass,
            wrong_handlers=wrong_handlers,
            score=score_result.score,
            breakdown=score_result.breakdown,
            is_hard_fail=score_result.is_hard_fail
        )
    
    def run_all(self, verbose: bool = False) -> List[StateTestResult]:
        """Run all state tests."""
        results = []
        
        for test in self.test_bank["tests"]:
            result = self.run_test(test)
            results.append(result)
            
            if verbose:
                status = "✓" if result.score == 100 else f"Score: {result.score}"
                print(f"{test['test_id']}: {status}")
        
        return results
```

### 6.3 pattern_tests.py

```python
"""
Pattern test runner - Tests regex/keyword pattern matching.

Handles:
- Crisis phrase detection (CRITICAL - false pos/neg are serious)
- Keyword boost matching (explicit entity mentions)
"""

import re
import json
from typing import List, Dict, Any
from dataclasses import dataclass

from .scoring import calculate_score, ScoreResult


@dataclass
class PatternTestResult:
    test_id: str
    name: str
    prompt: str
    pattern_type: str
    
    matched_entities: List[str]
    expected_matches: List[str]
    expected_secondary: List[str]
    not_expected_matches: List[str]
    
    primary_pass: bool
    secondary_missing: List[str]
    false_positives: List[str]
    
    score: int
    breakdown: Dict
    is_hard_fail: bool
    is_critical: bool
    is_critical_failure: bool  # Crisis false pos/neg


class PatternMatcher:
    """Matches messages against crisis patterns and keyword boosts."""
    
    def __init__(self, rules_path: str):
        with open(rules_path) as f:
            self.rules = json.load(f)
        
        # Compile regex patterns
        self._compiled_crisis = [
            {
                "pattern": re.compile(p["pattern"], re.IGNORECASE),
                "entities": p["entities"],
                "is_critical": p.get("is_critical", False)
            }
            for p in self.rules.get("crisis_patterns", [])
        ]
        
        # Normalize keyword boosts
        self._keyword_boosts = [
            {
                "keywords": [k.lower() for k in b["keywords"]],
                "entity": b["entity"]
            }
            for b in self.rules.get("keyword_boosts", [])
        ]
    
    def match(self, message: str) -> List[str]:
        """Return list of entity_ids that match the message."""
        matched = set()
        
        # Crisis patterns
        for rule in self._compiled_crisis:
            if rule["pattern"].search(message):
                matched.update(rule["entities"])
        
        # Keyword boosts
        message_lower = message.lower()
        for boost in self._keyword_boosts:
            if any(kw in message_lower for kw in boost["keywords"]):
                matched.add(boost["entity"])
        
        return list(matched)
    
    def match_with_details(self, message: str) -> Dict[str, Any]:
        """Return matches with details about what triggered them."""
        results = {
            "entities": set(),
            "crisis_matches": [],
            "keyword_matches": []
        }
        
        # Crisis patterns
        for rule in self._compiled_crisis:
            match = rule["pattern"].search(message)
            if match:
                results["entities"].update(rule["entities"])
                results["crisis_matches"].append({
                    "pattern": rule["pattern"].pattern,
                    "matched_text": match.group(),
                    "entities": rule["entities"]
                })
        
        # Keyword boosts
        message_lower = message.lower()
        for boost in self._keyword_boosts:
            for kw in boost["keywords"]:
                if kw in message_lower:
                    results["entities"].add(boost["entity"])
                    results["keyword_matches"].append({
                        "keyword": kw,
                        "entity": boost["entity"]
                    })
                    break
        
        results["entities"] = list(results["entities"])
        return results


class PatternTestRunner:
    """Runs pattern matching tests."""
    
    def __init__(self, test_bank_path: str, rules_path: str):
        self.matcher = PatternMatcher(rules_path)
        
        with open(test_bank_path) as f:
            self.test_bank = json.load(f)
    
    def run_test(self, test: Dict) -> PatternTestResult:
        """Run single pattern test."""
        
        matched = self.matcher.match(test["prompt"])
        
        expected = test["expected_matches"]
        expected_secondary = test.get("expected_secondary", [])
        not_expected = test.get("not_expected_matches", [])
        is_critical = test.get("is_critical", False)
        
        # Evaluate
        primary_pass = all(e in matched for e in expected)
        secondary_missing = [e for e in expected_secondary if e not in matched]
        false_positives = [e for e in not_expected if e in matched]
        
        # Calculate score
        score_result = calculate_score({
            "primary_pass": primary_pass,
            "secondary_missing": secondary_missing,
            "false_positives": false_positives,
            "rank_violations": []
        })
        
        # Critical failure check (crisis tests only)
        is_critical_failure = False
        if is_critical:
            # False negative: missed crisis
            if test["pattern_type"] == "crisis" and not primary_pass:
                is_critical_failure = True
            # False positive: triggered crisis on non-crisis (negative test)
            if test["pattern_type"] == "negative" and false_positives:
                is_critical_failure = True
        
        return PatternTestResult(
            test_id=test["test_id"],
            name=test.get("name", ""),
            prompt=test["prompt"],
            pattern_type=test.get("pattern_type", "unknown"),
            matched_entities=matched,
            expected_matches=expected,
            expected_secondary=expected_secondary,
            not_expected_matches=not_expected,
            primary_pass=primary_pass,
            secondary_missing=secondary_missing,
            false_positives=false_positives,
            score=score_result.score,
            breakdown=score_result.breakdown,
            is_hard_fail=score_result.is_hard_fail,
            is_critical=is_critical,
            is_critical_failure=is_critical_failure
        )
    
    def run_all(self, verbose: bool = False) -> List[PatternTestResult]:
        """Run all pattern tests."""
        results = []
        
        for test in self.test_bank["tests"]:
            result = self.run_test(test)
            results.append(result)
            
            if verbose:
                status = "✓" if result.score == 100 else f"Score: {result.score}"
                if result.is_critical_failure:
                    status = "🚨 CRITICAL"
                print(f"{test['test_id']}: {status}")
        
        return results
    
    def run_by_type(self, pattern_type: str) -> List[PatternTestResult]:
        """Run tests of specific pattern type."""
        tests = [
            t for t in self.test_bank["tests"]
            if t.get("pattern_type") == pattern_type
        ]
        return [self.run_test(t) for t in tests]
```

### 6.4 always_tests.py

```python
"""
Always-load test runner - Verifies core entities are always present.

These tests check that ALWAYS load_mode entities are present in context.
Failure here means the system is broken.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class AlwaysTestResult:
    test_id: str
    name: str
    user_type: str
    
    loaded_entities: List[str]
    expected_always: List[str]
    missing: List[str]
    
    score: int
    is_hard_fail: bool


class AlwaysTestRunner:
    """Runs always-load verification tests."""
    
    def __init__(self, test_bank_path: str, context_builder):
        """
        Args:
            test_bank_path: Path to always_load_tests.json
            context_builder: Service that builds Frank's context (has get_always_entities method)
        """
        self.context_builder = context_builder
        
        with open(test_bank_path) as f:
            self.test_bank = json.load(f)
    
    def run_test(self, test: Dict) -> AlwaysTestResult:
        """Run single always-load test."""
        
        user_type = test["user_type"]
        user_state = test.get("user_state", {})
        
        # Get entities that would be loaded
        loaded = self.context_builder.get_always_entities(user_type, user_state)
        loaded_ids = [e["entity_id"] for e in loaded]
        
        expected = test["expected_always"]
        missing = [e for e in expected if e not in loaded_ids]
        
        # Score: 100 if all present, 0 if any missing
        score = 100 if not missing else 0
        
        return AlwaysTestResult(
            test_id=test["test_id"],
            name=test.get("name", ""),
            user_type=user_type,
            loaded_entities=loaded_ids,
            expected_always=expected,
            missing=missing,
            score=score,
            is_hard_fail=bool(missing)
        )
    
    def run_all(self, verbose: bool = False) -> List[AlwaysTestResult]:
        """Run all always-load tests."""
        results = []
        
        for test in self.test_bank["tests"]:
            result = self.run_test(test)
            results.append(result)
            
            if verbose:
                status = "✓" if result.score == 100 else f"MISSING: {result.missing}"
                print(f"{test['test_id']}: {status}")
        
        return results
```

### 6.5 unified_runner.py

```python
"""
Unified test runner - Orchestrates all test types and aggregates results.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .scoring import get_score_distribution
from .semantic_tests import SemanticTestRunner
from .state_tests import StateTestRunner
from .pattern_tests import PatternTestRunner
from .always_tests import AlwaysTestRunner
from .expectation_loader import ExpectationLoader


@dataclass
class SemanticResults:
    tests_run: int
    average_score: float
    hard_fails: int
    score_distribution: Dict[str, int]
    topic_scores: Dict[str, Dict]
    results: List


@dataclass
class StateResults:
    tests_run: int
    average_score: float
    hard_fails: int
    handler_scores: Dict[str, Dict]
    results: List


@dataclass
class PatternResults:
    tests_run: int
    average_score: float
    hard_fails: int
    pattern_type_scores: Dict[str, Dict]
    critical_failures: List[str]
    results: List


@dataclass
class AlwaysResults:
    tests_run: int
    average_score: float
    all_passed: bool
    results: List


@dataclass
class UnifiedResults:
    timestamp: str
    semantic: SemanticResults
    state: StateResults
    pattern: PatternResults
    always: AlwaysResults
    summary: Dict[str, Any]


class UnifiedTestRunner:
    """Runs all test banks and produces unified results."""
    
    # Weights for combined score
    WEIGHTS = {
        "semantic": 0.60,
        "state": 0.15,
        "pattern": 0.15,
        "always": 0.10
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Dict with paths and services:
                - test_banks_dir: Path to test_banks/
                - voyage_service: VoyageEmbeddingService instance
                - reranker_service: RerankerService instance
                - context_builder: Context builder with get_always_entities
                - rate_limit_delay: Seconds between Haiku calls
        """
        self.config = config
        base_dir = Path(config["test_banks_dir"])
        
        # Initialize expectation loader
        self.expectation_loader = ExpectationLoader(
            test_bank_path=base_dir / "semantic" / "parent_test_bank.json",
            history_dir=base_dir / "semantic" / "history"
        )
        
        # Initialize runners
        self.semantic_runner = SemanticTestRunner(
            voyage_service=config["voyage_service"],
            reranker_service=config["reranker_service"],
            expectation_loader=self.expectation_loader,
            test_bank_path=str(base_dir / "semantic" / "parent_test_bank.json"),
            rate_limit_delay=config.get("rate_limit_delay", 1.25)
        )
        
        self.state_runner = StateTestRunner(
            test_bank_path=str(base_dir / "state" / "state_handler_tests.json")
        )
        
        self.pattern_runner = PatternTestRunner(
            test_bank_path=str(base_dir / "pattern" / "pattern_tests.json"),
            rules_path=str(base_dir / "pattern" / "pattern_rules.json")
        )
        
        self.always_runner = AlwaysTestRunner(
            test_bank_path=str(base_dir / "always" / "always_load_tests.json"),
            context_builder=config["context_builder"]
        )
    
    async def run_all(self, verbose: bool = False) -> UnifiedResults:
        """Run all test banks and aggregate results."""
        
        print("=" * 60)
        print("UNIFIED TEST HARNESS V2")
        print("=" * 60)
        
        # Run each bank
        print("\n[1/4] Running semantic tests...")
        semantic = await self._run_semantic(verbose)
        
        print("\n[2/4] Running state tests...")
        state = self._run_state(verbose)
        
        print("\n[3/4] Running pattern tests...")
        pattern = self._run_pattern(verbose)
        
        print("\n[4/4] Running always tests...")
        always = self._run_always(verbose)
        
        # Calculate summary
        summary = self._calculate_summary(semantic, state, pattern, always)
        
        results = UnifiedResults(
            timestamp=datetime.now().isoformat(),
            semantic=semantic,
            state=state,
            pattern=pattern,
            always=always,
            summary=summary
        )
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    async def _run_semantic(self, verbose: bool) -> SemanticResults:
        """Run semantic tests and aggregate."""
        results = await self.semantic_runner.run_all(verbose)
        scores = [r.score for r in results]
        
        # Calculate topic scores
        topic_scores = {}
        for result in results:
            for topic in result.topics:
                if topic not in topic_scores:
                    topic_scores[topic] = {"scores": [], "hard_fails": 0}
                topic_scores[topic]["scores"].append(result.score)
                if result.is_hard_fail:
                    topic_scores[topic]["hard_fails"] += 1
        
        for topic, data in topic_scores.items():
            data["avg"] = round(sum(data["scores"]) / len(data["scores"]), 1)
            data["tests"] = len(data["scores"])
            del data["scores"]
        
        return SemanticResults(
            tests_run=len(results),
            average_score=round(sum(scores) / len(scores), 1) if scores else 0,
            hard_fails=sum(1 for r in results if r.is_hard_fail),
            score_distribution=get_score_distribution(scores),
            topic_scores=topic_scores,
            results=results
        )
    
    def _run_state(self, verbose: bool) -> StateResults:
        """Run state tests and aggregate."""
        results = self.state_runner.run_all(verbose)
        scores = [r.score for r in results]
        
        # Calculate handler scores
        handler_scores = {}
        for result in results:
            for handler in result.expected_handlers:
                if handler not in handler_scores:
                    handler_scores[handler] = {"scores": [], "tests": 0}
                handler_scores[handler]["tests"] += 1
            # Use test_id to attribute score (simplified)
            # In practice, you might want more granular tracking
        
        return StateResults(
            tests_run=len(results),
            average_score=round(sum(scores) / len(scores), 1) if scores else 0,
            hard_fails=sum(1 for r in results if r.is_hard_fail),
            handler_scores=handler_scores,
            results=results
        )
    
    def _run_pattern(self, verbose: bool) -> PatternResults:
        """Run pattern tests and aggregate."""
        results = self.pattern_runner.run_all(verbose)
        scores = [r.score for r in results]
        
        # Calculate pattern type scores
        type_scores = {}
        for result in results:
            ptype = result.pattern_type
            if ptype not in type_scores:
                type_scores[ptype] = {"scores": [], "hard_fails": 0}
            type_scores[ptype]["scores"].append(result.score)
            if result.is_hard_fail:
                type_scores[ptype]["hard_fails"] += 1
        
        for ptype, data in type_scores.items():
            data["avg"] = round(sum(data["scores"]) / len(data["scores"]), 1)
            data["tests"] = len(data["scores"])
            del data["scores"]
        
        # Collect critical failures
        critical_failures = [
            r.test_id for r in results if r.is_critical_failure
        ]
        
        return PatternResults(
            tests_run=len(results),
            average_score=round(sum(scores) / len(scores), 1) if scores else 0,
            hard_fails=sum(1 for r in results if r.is_hard_fail),
            pattern_type_scores=type_scores,
            critical_failures=critical_failures,
            results=results
        )
    
    def _run_always(self, verbose: bool) -> AlwaysResults:
        """Run always tests and aggregate."""
        results = self.always_runner.run_all(verbose)
        scores = [r.score for r in results]
        
        return AlwaysResults(
            tests_run=len(results),
            average_score=round(sum(scores) / len(scores), 1) if scores else 0,
            all_passed=all(r.score == 100 for r in results),
            results=results
        )
    
    def _calculate_summary(
        self,
        semantic: SemanticResults,
        state: StateResults,
        pattern: PatternResults,
        always: AlwaysResults
    ) -> Dict[str, Any]:
        """Calculate combined summary with health status."""
        
        total_tests = (
            semantic.tests_run +
            state.tests_run +
            pattern.tests_run +
            always.tests_run
        )
        
        # Weighted combined score
        combined_score = (
            semantic.average_score * self.WEIGHTS["semantic"] +
            state.average_score * self.WEIGHTS["state"] +
            pattern.average_score * self.WEIGHTS["pattern"] +
            always.average_score * self.WEIGHTS["always"]
        )
        
        total_hard_fails = (
            semantic.hard_fails +
            state.hard_fails +
            pattern.hard_fails +
            (0 if always.all_passed else always.tests_run)
        )
        
        # Determine health status
        if pattern.critical_failures:
            health = "CRITICAL"
        elif combined_score >= 90 and total_hard_fails == 0:
            health = "EXCELLENT"
        elif combined_score >= 80:
            health = "GOOD"
        elif combined_score >= 70:
            health = "FAIR"
        else:
            health = "POOR"
        
        # Expectation source summary
        expectation_sources = self.expectation_loader.get_expectation_summary()
        
        return {
            "total_tests": total_tests,
            "combined_score": round(combined_score, 1),
            "hard_fail_count": total_hard_fails,
            "critical_failures": pattern.critical_failures,
            "health_status": health,
            "component_scores": {
                "semantic": semantic.average_score,
                "state": state.average_score,
                "pattern": pattern.average_score,
                "always": always.average_score
            },
            "expectation_sources": expectation_sources
        }
    
    def _print_summary(self, results: UnifiedResults):
        """Print summary to console."""
        s = results.summary
        
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        print(f"\nHealth Status: {s['health_status']}")
        print(f"Combined Score: {s['combined_score']}")
        print(f"Total Tests: {s['total_tests']}")
        print(f"Hard Fails: {s['hard_fail_count']}")
        
        if s['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES: {s['critical_failures']}")
        
        print("\nComponent Scores:")
        for component, score in s['component_scores'].items():
            print(f"  {component}: {score}")
        
        print("\nExpectation Sources:")
        for source, count in s['expectation_sources'].items():
            print(f"  {source}: {count}")
```

### 6.6 reporting.py

```python
"""
Report generation for test harness results.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import json


def generate_markdown_report(results, output_path: Path = None) -> str:
    """Generate markdown report from UnifiedResults."""
    
    s = results.summary
    
    lines = [
        "# Test Harness V2 Results",
        f"**Date:** {results.timestamp}",
        f"**Health Status:** {s['health_status']}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Component | Score | Tests | Hard Fails |",
        "|-----------|-------|-------|------------|",
        f"| Semantic | {results.semantic.average_score} | {results.semantic.tests_run} | {results.semantic.hard_fails} |",
        f"| State | {results.state.average_score} | {results.state.tests_run} | {results.state.hard_fails} |",
        f"| Pattern | {results.pattern.average_score} | {results.pattern.tests_run} | {results.pattern.hard_fails} |",
        f"| Always | {results.always.average_score} | {results.always.tests_run} | {0 if results.always.all_passed else results.always.tests_run} |",
        f"| **Combined** | **{s['combined_score']}** | **{s['total_tests']}** | **{s['hard_fail_count']}** |",
        "",
    ]
    
    # Critical failures
    if s['critical_failures']:
        lines.extend([
            "## 🚨 Critical Failures",
            "",
            "These crisis detection failures require immediate attention:",
            ""
        ])
        for cf in s['critical_failures']:
            lines.append(f"- {cf}")
        lines.append("")
    
    # Score distribution (semantic)
    lines.extend([
        "## Score Distribution (Semantic)",
        "",
        "| Range | Count |",
        "|-------|-------|",
    ])
    for range_name, count in results.semantic.score_distribution.items():
        lines.append(f"| {range_name} | {count} |")
    lines.append("")
    
    # Topic scores
    lines.extend([
        "## Topic Scores (Semantic)",
        "",
        "| Topic | Avg Score | Tests | Hard Fails |",
        "|-------|-----------|-------|------------|",
    ])
    
    # Sort by avg score descending
    sorted_topics = sorted(
        results.semantic.topic_scores.items(),
        key=lambda x: x[1]["avg"],
        reverse=True
    )
    for topic, data in sorted_topics:
        lines.append(f"| {topic} | {data['avg']} | {data['tests']} | {data['hard_fails']} |")
    lines.append("")
    
    # Expectation sources
    lines.extend([
        "## Expectation Sources",
        "",
        "| Source | Tests |",
        "|--------|-------|",
    ])
    for source, count in s['expectation_sources'].items():
        lines.append(f"| {source} | {count} |")
    lines.append("")
    
    # Failures detail (semantic)
    failures = [r for r in results.semantic.results if r.is_hard_fail]
    if failures:
        lines.extend([
            "## Semantic Test Failures",
            ""
        ])
        for f in failures[:20]:  # Limit to 20
            lines.extend([
                f"### {f.test_id}: {f.name}",
                f"**Prompt:** {f.prompt[:100]}...",
                f"**Expected Primary:** {f.expectations['expected_primary']}",
                f"**Haiku Selected:** {f.haiku_selections}",
                f"**Expectation Source:** {f.expectation_source}",
                ""
            ])
    
    report = "\n".join(lines)
    
    # Save if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
    
    return report


def save_json_results(results, output_path: Path):
    """Save full results as JSON."""
    
    # Convert dataclasses to dicts (simplified - may need custom serialization)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # For now, save summary + scores only (full results may be large)
    summary_data = {
        "timestamp": results.timestamp,
        "summary": results.summary,
        "semantic": {
            "tests_run": results.semantic.tests_run,
            "average_score": results.semantic.average_score,
            "hard_fails": results.semantic.hard_fails,
            "score_distribution": results.semantic.score_distribution,
            "topic_scores": results.semantic.topic_scores
        },
        "state": {
            "tests_run": results.state.tests_run,
            "average_score": results.state.average_score,
            "hard_fails": results.state.hard_fails
        },
        "pattern": {
            "tests_run": results.pattern.tests_run,
            "average_score": results.pattern.average_score,
            "hard_fails": results.pattern.hard_fails,
            "pattern_type_scores": results.pattern.pattern_type_scores,
            "critical_failures": results.pattern.critical_failures
        },
        "always": {
            "tests_run": results.always.tests_run,
            "average_score": results.always.average_score,
            "all_passed": results.always.all_passed
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
```

---

## 7. API Endpoints

Add to existing `testing.py` router:

```python
from fastapi import APIRouter, Query
from typing import Optional, List

router = APIRouter(prefix="/cli", tags=["testing"])


@router.get("/test-harness")
async def run_test_harness(
    banks: str = Query("all", description="Which banks to run: all, semantic, state, pattern, always"),
    verbose: bool = Query(False, description="Show detailed output"),
    failures_only: bool = Query(False, description="Only show failures"),
    save_results: bool = Query(True, description="Save results to file")
):
    """Run unified test harness."""
    
    runner = UnifiedTestRunner(get_test_config())
    
    if banks == "all":
        results = await runner.run_all(verbose)
    elif banks == "semantic":
        results = await runner.run_semantic_only(verbose)
    # ... etc
    
    if save_results:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        save_json_results(results, Path(f"results/results_{timestamp}.json"))
        generate_markdown_report(results, Path(f"results/report_{timestamp}.md"))
    
    return {
        "health_status": results.summary["health_status"],
        "combined_score": results.summary["combined_score"],
        "total_tests": results.summary["total_tests"],
        "hard_fails": results.summary["hard_fail_count"],
        "critical_failures": results.summary["critical_failures"]
    }


@router.get("/test-harness/test/{test_id}")
async def run_single_test(
    test_id: str,
    debug: bool = Query(False, description="Show debug info")
):
    """Run single test by ID."""
    # Determine which bank based on test_id prefix
    # V2-* = semantic, STATE-* = state, PAT-* = pattern, ALWAYS-* = always
    pass


@router.get("/test-harness/topic/{topic}")
async def run_by_topic(topic: str):
    """Run semantic tests for specific topic."""
    pass


@router.post("/calibrate")
async def calibrate_tests(
    scope: str = Query("full", description="full, affected, or single"),
    test_ids: Optional[List[str]] = Query(None),
    added_entities: Optional[List[str]] = Query(None),
    kb_version: str = Query("v2.0"),
    dry_run: bool = Query(True, description="Don't save results")
):
    """Run Opus calibration on test expectations."""
    pass
```

---

## 8. Implementation Order

| Phase | Component | Depends On | Effort |
|-------|-----------|------------|--------|
| 1 | scoring.py | None | Small |
| 2 | expectation_loader.py | None | Small |
| 3 | Copy test bank JSON files | None | Trivial |
| 4 | always_tests.py | scoring | Small |
| 5 | state_tests.py | scoring | Medium |
| 6 | pattern_tests.py + pattern_rules.json | scoring | Medium |
| 7 | semantic_tests.py | scoring, expectation_loader, existing services | Medium |
| 8 | unified_runner.py | All test runners | Medium |
| 9 | reporting.py | unified_runner | Small |
| 10 | API endpoints | unified_runner | Small |
| 11 | calibrate.py | AI service, expectation_loader | Deferred |

**Estimated total: ~1300 lines of code**

---

## 9. Critical Requirements

### 9.1 MUST HAVE

1. **100-point scoring exactly as specified** - Per-item penalties, hard fail on primary miss
2. **Expectation versioning** - History files, source tracking, human override support
3. **Critical failure flagging** - Crisis false pos/neg flagged separately, affects health status
4. **Rate limiting** - 1.25s between Haiku calls
5. **Weighted combined score** - 60% semantic, 15% state, 15% pattern, 10% always

### 9.2 MUST NOT

1. **Don't break existing semantic tests** - Keep backward compatibility
2. **Don't skip rate limiting** - API will throttle
3. **Don't lose expectation history** - Append to history, never overwrite
4. **Don't ignore critical failures** - They must surface prominently

### 9.3 State Conditions (Hardcode These)

```python
STATE_CONDITIONS = {
    "handler_first_conversation": {
        "is_first_conversation": {"eq": True}
    },
    "handler_returning_user": {
        "is_first_conversation": {"eq": False},
        "days_since_last": {"gte": 7}
    },
    "handler_post_escalation": {
        "is_first_conversation": {"eq": False},
        "last_rating": {"lte": 2}
    },
    "handler_celebrating_wins": {
        "is_first_conversation": {"eq": False},
        "last_rating": {"gte": 4}
    },
    "handler_clinician_mode": {
        "user_type": {"in": ["CLINICIAN", "PROFESSIONAL"]}
    }
}
```

### 9.4 Health Status Logic

```python
if pattern.critical_failures:
    health = "CRITICAL"
elif combined_score >= 90 and total_hard_fails == 0:
    health = "EXCELLENT"
elif combined_score >= 80:
    health = "GOOD"
elif combined_score >= 70:
    health = "FAIR"
else:
    health = "POOR"
```

---

## 10. Success Criteria

### 10.1 Functional

- [ ] All 4 test banks runnable independently
- [ ] Unified runner aggregates results correctly
- [ ] 100-point scoring matches spec exactly (verify with examples)
- [ ] Critical failures flagged for crisis tests
- [ ] Expectation loader resolves history → original correctly
- [ ] Markdown report saved to results/
- [ ] Health status calculated correctly

### 10.2 Quality

- [ ] Existing semantic tests still work (no regression)
- [ ] Rate limiting respected (1.25s delay)
- [ ] Results JSON is valid and complete
- [ ] Code is documented and type-hinted

### 10.3 Validation Tests

Run these to verify implementation:

```bash
# Run all banks
GET /cli/test-harness?banks=all

# Verify scoring
# - Create test with 1 secondary miss → should score 90
# - Create test with 1 false positive → should score 80
# - Create test with primary miss → should score 0

# Verify critical failures
# - PAT-NEG-001 with handler_crisis in matched → should flag critical
# - Health status should be CRITICAL when any critical failures exist

# Verify expectation loading
# - Add entry to history file → should use history over original
# - Add human_override → should use override over history
```

---

## Appendix: Test Bank Files Location

The three new test bank files are provided separately:

1. `state_handler_tests.json` - 18 tests
2. `pattern_tests.json` - 28 tests  
3. `always_load_tests.json` - 7 tests

Plus create `pattern_rules.json` from the schema in section 5.5.

Migrate existing `parent_test_bank.json` by adding:
```json
{
  "bank_type": "SEMANTIC",
  "version": "2.0",
  "tests": [... existing tests ...]
}
```

---

**END OF SPECIFICATION**
