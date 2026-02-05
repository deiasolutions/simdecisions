# Addendum 3: Business Rules Evaluation

**Created:** 2025-12-14  
**Source:** `CONTENT_PROMPT_BUSINESS_RULES.md` v2.3  
**Status:** CRITICAL - Production content has 30 issues, 34 warnings

---

## Executive Summary

| Category | Count | Impact |
|----------|-------|--------|
| ✅ Correctly Configured | 10 | Working as intended |
| ❌ Critical Issues | 30 | Content will NOT be retrieved |
| ⚠️ Warnings | 34 | Degraded retrieval (keyword-only) |

**Bottom Line:** Only 10 of 44 entities are correctly configured. The rest have issues ranging from "won't work at all" to "works partially."

---

## Critical Business Rules

### Rule 1: Priority Determines Similarity Threshold

| Priority | Threshold | Meaning |
|----------|-----------|---------|
| 90-100 | 0.0 | Always retrieved (effectively ALWAYS load) |
| 70-89 | 0.3 | Easy to match |
| 40-69 | 0.5 | **Moderate bar** - needs decent similarity |
| 0-39 | 0.7 | Hard to match |

**Issue:** 16 KNOWLEDGE entities at priority 50 with NO embeddings. They need 0.5 similarity but can't compute similarity without embeddings.

### Rule 2: SITUATION Load Requires Embeddings OR Keywords

```
For SITUATION load mode:
  IF embedding exists → use semantic similarity
  ELSE IF situation_keywords exist → use keyword matching
  ELSE → content is UNREACHABLE
```

**Issue:** All 44 entities have `has_embedding: false`. Only keyword matching works.

### Rule 3: Placeholder Phrases Are Useless

```
"help with clinical_guardrails_extracted..., struggling with this"
```

This will NEVER match a real user query like "my ex keeps manipulating me."

**Issue:** 12 entities have placeholder phrases instead of real matching phrases.

### Rule 4: Retrieval Limits Apply

| Type | Max Retrieved |
|------|---------------|
| GUARDRAIL | 10 |
| KNOWLEDGE | 5 |
| SCRIPT | 3 |
| RULE | 5 |

**Issue:** With 26 KNOWLEDGE entities but only 5 retrieved per query, having broken entities wastes retrieval slots.

---

## Entity-by-Entity Evaluation

### ✅ CORRECTLY CONFIGURED (10 entities)

These are working as intended:

| entity_id | Type | Why Correct |
|-----------|------|-------------|
| `frank_parent_persona` | PERSONA | ALWAYS load, priority 100 |
| `core_behavioral_guardrails` | GUARDRAIL | ALWAYS load, priority 100 |
| `hipaa_privacy` | GUARDRAIL | ALWAYS load, priority 95 |
| `quotes` | PERSONA | ALWAYS load, priority 70 |
| `user_context` | PERSONA | ALWAYS load, priority 70 |
| `handler_first_conversation` | HANDLER | Has state_conditions |
| `handler_returning_user` | HANDLER | Has state_conditions |
| `handler_post_escalation` | HANDLER | Has state_conditions |
| `handler_clinician_mode` | HANDLER | Has state_conditions |
| `handler_celebrating_wins` | HANDLER | Has state_conditions |

### ❌ BROKEN - Must Remove (6 entities)

These should NOT exist in content_entities:

| entity_id | Type | Problem | Action |
|-----------|------|---------|--------|
| `base_system_prompt` | KNOWLEDGE | System config, not content | DELETE |
| `general` | KNOWLEDGE | Session type prompt | DELETE |
| `co_parent` | KNOWLEDGE | Session type prompt | DELETE |
| `parent_child` | KNOWLEDGE | Session type prompt | DELETE |
| `index_master` | KNOWLEDGE | Index file, not content | DELETE |
| `handbook_full_text` | KNOWLEDGE | 500K chars raw source | DELETE |

### ❌ BROKEN - Placeholder Phrases (12 entities)

These have useless situation_phrases:

| entity_id | Current Phrase | Needed |
|-----------|---------------|--------|
| `clinical_handbook_extracts` | "help with clinical_guardrails..." | Crisis detection phrases |
| `situational` | "help with situational_guardrails..." | Context safety triggers |
| `biff_method_detailed` | "help with biff_method..." | Same as biff_response |
| `coercive_control_detailed` | "help with coercive_control..." | "controlling, isolated, monitors phone" |
| `coercive_control_summary_converted` | "help with coercive_control..." | MERGE into detailed |
| `communication_fundamentals` | "help with communication..." | "how to talk, communicate, message" |
| `sticky_notes_biff_converted` | "help with sticky_notes..." | MERGE into biff |
| `communication_guidelines` | "help with rules_of_the_game..." | "email, text, written message" |
| `conflict_resolution` | "help with rules_of_the_game..." | "argument, disagreement, conflict" |

### ⚠️ WORKING BUT DEGRADED (17 entities)

These have real situation_phrases but no embeddings - keyword-only matching:

| entity_id | Type | situation_phrases (sample) |
|-----------|------|---------------------------|
| `gray_rock` | KNOWLEDGE | "keeps baiting me, trying to get a reaction..." ✓ |
| `biff_response` | KNOWLEDGE | "need to reply to a nasty email..." ✓ |
| `loyalty_binds` | KNOWLEDGE | "child is caught in the middle..." ✓ |
| `psychological_splitting` | KNOWLEDGE | "sees everything in black and white..." ✓ |
| `boundary_setting` | KNOWLEDGE | "need to set boundaries..." ✓ |
| `de_escalation` | KNOWLEDGE | "things are getting heated..." ✓ |
| `transition_bridge` | KNOWLEDGE | "handoffs are hard, transitions rough..." ✓ |
| `dialectical_thinking` | KNOWLEDGE | "stuck in either or thinking..." ✓ |
| `ambiguous_loss` | KNOWLEDGE | "grief without closure..." ✓ |
| `medium_response_time` | KNOWLEDGE | "reacted too fast..." ✓ |
| `domestic_violence` | KNOWLEDGE | "partner is abusive, being hurt..." ✓ |
| `parental_alienation` | KNOWLEDGE | "child hates me, turned against me..." ✓ |
| `substance_abuse` | KNOWLEDGE | "ex is drinking, drug problem..." ✓ |
| `rule_crisis_detection` | RULE | "wants to hurt themselves..." ✓ |
| `rotg_de_escalation` | SCRIPT | "things are getting heated..." ✓ |
| `high_conflict` | KNOWLEDGE | "my client, professional guidance..." ✓ |
| `assessment_frameworks` | KNOWLEDGE | "my client, professional guidance..." ✓ |

**Note:** These work via keyword matching only. Once embeddings are generated, semantic matching will also work.

### ⚠️ HANDLER PRIORITY MISMATCH (1 entity)

| entity_id | Issue |
|-----------|-------|
| `handler_crisis` | Priority 95 with STATE load_mode. Priority ≥90 = ALWAYS load per business rules. This means crisis handler loads for EVERY message, not just when crisis detected. |

**Recommendation:** Either lower priority to 89 OR change to ALWAYS load intentionally.

---

## Action Plan for Claude Code

### Phase 1: Delete Bad Entities

```python
DELETE_ENTITIES = [
    'base_system_prompt',
    'general',
    'co_parent', 
    'parent_child',
    'index_master',
    'handbook_full_text',
]
```

### Phase 2: Merge Duplicates

```python
MERGE_MAP = {
    'sticky_notes_biff_converted': 'biff_method_detailed',  # Keep detailed
    'coercive_control_summary_converted': 'coercive_control_detailed',  # Keep detailed
}
```

### Phase 3: Fix Placeholder Phrases

For each placeholder entity, write real phrases:

```python
PHRASE_FIXES = {
    'clinical_handbook_extracts': 'crisis signs, red flags, safety concerns, clinical indicators, high risk behavior',
    
    'situational': 'specific situation, context matters, depends on circumstances, in this case',
    
    'biff_method_detailed': 'need to reply to a nasty email, how do I respond to this text, dont know what to say back, trying not to engage, keeping it brief',
    
    'coercive_control_detailed': 'controlling behavior, isolated from friends, monitors my phone, financial control, wont let me work, checks my messages, tracks my location, tells me what to wear',
    
    'communication_fundamentals': 'how to talk to ex, communicating with coparent, messages to send, what to say, written communication',
    
    'communication_guidelines': 'email etiquette, text communication, written messages, how to word this, professional tone',
    
    'conflict_resolution': 'fighting with ex, argument, disagreement, conflict, tension, cant agree, butting heads',
}
```

### Phase 4: Adjust Priorities

Based on business rules:

| entity_id | Current | Target | Reason |
|-----------|---------|--------|--------|
| `handler_crisis` | 95 | 89 | Prevent unintended ALWAYS load |
| `biff_method_detailed` | 50 | 60 | Match `biff_response` |
| `coercive_control_detailed` | 50 | 55 | Important reference |
| `clinical_handbook_extracts` | 70 | 80 | Safety content deserves HIGH tier |
| `situational` | 70 | 75 | Context-dependent safety |

### Phase 5: Generate Embeddings

After content fixes, call embedding generation for ALL entities:

```bash
# Via API (triggers auto-generation)
for entity_id in $(cat entity_ids.txt); do
  curl -X PATCH "https://api.familybondbot.com/api/admin/content-entities/$entity_id" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"_trigger_embedding": true}'
done
```

Or via direct service call in migration script.

### Phase 6: Verify Fix

```bash
# Check all entities have embeddings
curl "https://api.familybondbot.com/api/admin/testing/cli/export-content?secret=xxx" | \
  python -c "import json,sys; d=json.load(sys.stdin); 
  bad=[e['entity_id'] for e in d['entities'] if not e['has_embedding']];
  print(f'Missing embeddings: {len(bad)}');
  print(bad[:10])"
```

---

## Post-Fix Target State

After all fixes:

| Type | Count | Status |
|------|-------|--------|
| PERSONA | 3 | All ALWAYS load ✓ |
| GUARDRAIL | 3-4 | All have embeddings, real phrases |
| HANDLER | 7 | All have state_conditions ✓ |
| KNOWLEDGE | ~18 | All have embeddings, real phrases |
| SCRIPT | 3 | All have embeddings, real phrases |
| RULE | 1-2 | All have embeddings |
| **TOTAL** | ~35 | All functional |

---

## Retrieval Simulation

**Example user message:** "My ex keeps sending me nasty texts and I don't know how to respond"

### Before Fixes (Current)
```
ALWAYS LOAD:
  ✓ frank_parent_persona (priority 100)
  ✓ core_behavioral_guardrails (priority 100)
  ✓ hipaa_privacy (priority 95)
  ✓ handler_crisis (priority 95 - unintended!)
  ✓ quotes (priority 70)
  ✓ user_context (priority 70)

SITUATION MATCH (keyword only):
  ✓ biff_response - matches "respond", "texts"
  ✓ gray_rock - matches "nasty"
  ? communication_guidelines - has placeholder, NO MATCH

TOTAL USEFUL RETRIEVAL: 2 KNOWLEDGE entities
```

### After Fixes
```
ALWAYS LOAD:
  ✓ frank_parent_persona (priority 100)
  ✓ core_behavioral_guardrails (priority 100)
  ✓ hipaa_privacy (priority 95)
  ✓ quotes (priority 70)
  ✓ user_context (priority 70)

HANDLERS (state match):
  (none triggered for this message)

SITUATION MATCH (semantic + keyword):
  ✓ biff_response - semantic 0.82, keyword match
  ✓ gray_rock - semantic 0.71, keyword match
  ✓ communication_guidelines - semantic 0.65
  ✓ de_escalation - semantic 0.58
  ✓ boundary_setting - semantic 0.52

TOTAL USEFUL RETRIEVAL: 5 KNOWLEDGE entities (max)
```

---

## Files for Claude Code

Give Claude Code these files:
1. `CLAUDE_CODE_KB_STAGING_TASK.md` - Original task
2. `CLAUDE_CODE_KB_STAGING_ADDENDUM.md` - Caboose patterns
3. `CLAUDE_CODE_KB_STAGING_ADDENDUM_2.md` - Critical issues
4. `CLAUDE_CODE_KB_STAGING_ADDENDUM_3.md` - **This file** (Business rules evaluation)
5. `KB_PRODUCTION_CURRENT_2025-12-14.json` - Current production state
6. `KB_CABOOSE_CONTENT_ENTITIES.json` - Full content source
7. `CONTENT_PROMPT_BUSINESS_RULES.md` - Authoritative rules

---

*Evaluation complete. 30 issues identified, action plan defined.*
