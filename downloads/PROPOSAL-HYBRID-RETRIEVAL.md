# Hybrid Retrieval Proposal - Spec Overview

**Date:** 2025-12-18
**Status:** PROPOSAL - Awaiting review
**Problem:** RAG test suite showing 18% failure rate; key entities never reach Haiku for ranking

---

## Problem Statement

Current retrieval is semantic-only:
```
User Message → Voyage Embedding → Top 15 by Similarity → Haiku Ranks → Final 3-6
```

**Failure modes identified:**

1. **Handler entities** (crisis, first_conversation, returning_user) don't surface semantically because their descriptions are clinical, not parent-voice

2. **Pattern-based content** (crisis detection) requires exact phrase matching, not semantic similarity - "want to end it" may not semantically match crisis content

3. **Keyword-explicit requests** - when user says "help me gray rock" the entity should boost, but semantic similarity treats it same as any other match

4. **State-based handlers** - returning_user, first_conversation require user context, not message content

**Evidence from test results:**
- `handler_crisis` works (4.0 GPA) only because crisis language happens to match semantically
- `rotg_de_escalation` fails (0.5 GPA) - Voyage finds it but ranks low, Haiku never sees it
- 6 state-based handlers: 0.0 GPA - never appear in Voyage top 15

---

## Proposed Solution: Hybrid Retrieval

Add three retrieval channels alongside semantic search:

```
User Message + User State
         │
         ├─────────────┬─────────────┬─────────────┐
         ▼             ▼             ▼             ▼
     Semantic      Keyword       Pattern        State
     (Voyage)      Match         Match          Match
     top 10        top 5         top 5          top 3
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                              │
                              ▼
                    Merge & Dedupe (max 15)
                              │
                              ▼
                        Haiku Ranks
                              │
                              ▼
                        Final 3-6
```

---

## Four Retrieval Channels

| Channel | Input | Matches On | Use Case |
|---------|-------|------------|----------|
| **Semantic** | message text | Voyage embedding similarity | Conceptual matches ("feels guilty having fun" → loyalty_binds) |
| **Keyword** | message tokens | Entity `keywords` field | Explicit mentions ("gray rock", "BIFF", "documentation") |
| **Pattern** | message text | Entity `trigger_patterns` (regex) | Crisis phrases, specific behavioral indicators |
| **State** | user_state dict | Entity `state_conditions` JSON | First conversation, returning user, clinician mode |

---

## Required Entity Field Additions

Each entity needs these fields populated (many are currently empty):

```json
{
  "entity_id": "handler_crisis",
  "entity_type": "HANDLER",
  
  "keywords": "suicide, crisis, self-harm, die, kill, abuse, unsafe, emergency",
  
  "trigger_patterns": [
    "want(s)? to (die|end it|hurt|kill)",
    "better off (dead|without me)", 
    "(not|don't|dont) feel safe",
    "can'?t (go on|do this|take it)"
  ],
  
  "state_conditions": null
}
```

```json
{
  "entity_id": "handler_first_conversation",
  "entity_type": "HANDLER",
  
  "keywords": null,
  "trigger_patterns": null,
  
  "state_conditions": {
    "is_first_conversation": true
  }
}
```

```json
{
  "entity_id": "rotg_de_escalation", 
  "entity_type": "SCRIPT",
  
  "keywords": "calm, breathe, pause, regulate, triggered, lose it, snap",
  
  "trigger_patterns": [
    "(about to|going to|gonna) (lose it|snap|explode)",
    "(need|help).*(calm|calming) down",
    "blood pressure (rising|up)"
  ],
  
  "state_conditions": null
}
```

---

## Merge Strategy

When combining results from all channels:

1. **Deduplicate** - same entity from multiple channels counts once
2. **Boost multi-channel hits** - entity found by semantic AND keyword ranks higher
3. **Priority override** - pattern-matched crisis always included regardless of other scores
4. **Cap at 15** - Haiku's input limit

```python
def merge_candidates(semantic, keyword, pattern, state, max_total=15):
    # Pattern matches (crisis) get priority - always include
    priority_entities = [e for e in pattern if e.priority >= 90]
    
    # Score remaining by channel hits
    scores = defaultdict(float)
    for e in semantic: scores[e.entity_id] += 1.0
    for e in keyword: scores[e.entity_id] += 0.5  # Boost for explicit mention
    for e in pattern: scores[e.entity_id] += 0.8
    for e in state: scores[e.entity_id] += 1.0    # State matches are definitive
    
    # Sort by score, take top N
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Combine priority + ranked, dedupe, cap
    result = priority_entities + [e for e, _ in ranked if e not in priority_entities]
    return result[:max_total]
```

---

## Database Schema Changes

Add columns to `content_entities` table:

```sql
ALTER TABLE content_entities ADD COLUMN keywords TEXT;
ALTER TABLE content_entities ADD COLUMN trigger_patterns JSONB DEFAULT '[]';
ALTER TABLE content_entities ADD COLUMN state_conditions JSONB DEFAULT NULL;
```

Note: `recognition` field already exists (used for Voyage embedding). New fields are for keyword/pattern/state channels.

---

## Implementation Scope

| Component | Change | Effort |
|-----------|--------|--------|
| DB Schema | Add 3 columns | Small |
| Entity Data | Populate fields for 23 SITUATION entities | Medium |
| Retrieval Service | Add keyword_match, pattern_match, state_match methods | Medium |
| Retrieval Service | Add merge logic | Small |
| Test Harness | Track which channel found each entity (diagnostic) | Small |

---

## Expected Outcomes

| Metric | Current | Projected |
|--------|---------|-----------|
| Overall GPA | 3.0 | 3.6+ |
| Handler tests (6) | 0.0 | 3.5+ |
| Crisis detection | Works by luck | Guaranteed via pattern |
| rotg_de_escalation | 0.5 | 3.0+ |

---

## Questions for Review

1. **Merge weights** - Is semantic=1.0, keyword=0.5, pattern=0.8, state=1.0 reasonable? Or should keyword matches boost higher?

2. **Pattern complexity** - Should trigger_patterns be simple keyword lists or full regex? Regex is powerful but harder to maintain.

3. **Performance** - Keyword and pattern matching on every message adds latency. Acceptable? Should we cache compiled regex?

4. **Channel diagnostics** - Should we log which channel(s) surfaced each entity for ongoing tuning?

5. **Existing code** - Does current retrieval service architecture support adding these channels cleanly, or is refactor needed?

---

## Files to Create (pending approval)

1. `SPEC-HYBRID-RETRIEVAL.md` - Full implementation spec
2. `entity_field_additions.json` - Keywords, patterns, conditions for all 23 entities
3. Updated `parent_test_bank.json` - Handler tests with state conditions

---

## Summary

Current semantic-only retrieval misses entities that should match via keywords, patterns, or user state. Hybrid approach adds three lightweight matching channels that feed into the same Haiku ranking step. This unifies all entity types into one testable pipeline.
