# V3.0 Content Entity System Guide

**Date:** 2025-12-30
**Purpose:** Authoritative reference for KB content migration and review
**Audience:** Claude instances reviewing/migrating KB content

---

## IMPORTANT: Schema Clarification

**The canonical schema is defined in `content_entity.py` - NOT in older spec documents.**

If you see references to 4 types (concepts, scripts, guardrails, decision_rules), that is **OUTDATED**. The production system uses **6 entity types**.

---

## 1. Database Schema

### Table: `content_entities`

```sql
CREATE TABLE content_entities (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(100) UNIQUE NOT NULL,      -- Human-readable ID (e.g., "gray_rock")
    entity_type VARCHAR(20) NOT NULL,            -- One of 6 types below
    subtype VARCHAR(50),                         -- Optional sub-categorization
    title VARCHAR(255) NOT NULL,                 -- Display title

    -- Content (type-specific schema)
    content JSONB NOT NULL DEFAULT '{}',         -- THE MAIN CONTENT BLOB

    -- Retrieval fields
    keywords VARCHAR(500),                       -- Comma-separated trigger words
    recognition TEXT,                            -- Natural language patterns that match this entity
    embedding JSONB,                             -- Vector embedding for semantic search

    -- Routing
    load_mode VARCHAR(20) NOT NULL DEFAULT 'SITUATION',  -- ALWAYS, STATE, or SITUATION
    state_conditions JSONB,                      -- Conditions for STATE-loaded entities
    priority INTEGER DEFAULT 50,                 -- 0-100, higher = loaded first

    -- Targeting
    audience_types JSONB DEFAULT '["PARENT"]',   -- Who sees this: PARENT, CLINICIAN, PROFESSIONAL
    chat_types JSONB DEFAULT '[]',               -- Which chats: CO_PARENT, etc. Empty = all

    -- Administration
    editable_by VARCHAR(20) DEFAULT 'ADMIN',     -- HIDDEN, ADMIN, or TRAINER
    is_active BOOLEAN DEFAULT TRUE,              -- Soft delete flag

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);
```

### Constraints

```sql
CONSTRAINT valid_entity_type CHECK (entity_type IN (
    'PERSONA', 'RULE', 'HANDLER', 'TOPIC', 'RERANKER', 'CHAT_CONTEXT'
))

CONSTRAINT valid_load_mode CHECK (load_mode IN ('ALWAYS', 'STATE', 'SITUATION'))
```

---

## 2. Entity Types (6 Canonical Types)

### 2.1 PERSONA

**Purpose:** Defines Frank's identity, voice, and behavioral guidelines.

**When loaded:** ALWAYS (cached at session start)

**Content schema:**
```json
{
    "identity": "Who Frank is, his background, his stance",
    "voice": "How Frank speaks - tone, phrases, what he says/never says",
    "approach": "Frank's methodology - MI, practical techniques, court-awareness",
    "anti_patterns": "What Frank NEVER does - no legal advice, no diagnosis, etc."
}
```

**Examples:**
- `frank_persona_parent` - Frank for parents (warm, direct, peer who's been there)
- `frank_persona_clinician` - Frank for clinicians (collegial, clinical terminology)

**Priority:** 95 (highest - defines core behavior)

---

### 2.2 RULE

**Purpose:** Hard constraints on Frank's behavior. Non-negotiable rules.

**When loaded:** ALWAYS or SITUATION (depending on guardrail)

**Content schema:**
```json
{
    "constraint": "What must/must not happen",
    "trigger_patterns": "Situations that activate this guardrail",
    "required_action": "What Frank MUST do when triggered",
    "never_do": "What Frank must NEVER do"
}
```

**Examples:**
- `core_behavioral_guardrails` - The "nevers" (no legal advice, no diagnosis)
- `hipaa_privacy` - HIPAA compliance rules
- `pii_detection_instructions` - How to handle PII
- `loop_prevention_guardrail` - Don't repeat responses

**Priority:** 90-100 (critical safety)

---

### 2.3 HANDLER

**Purpose:** Context-specific behavioral modes that activate based on user state.

**When loaded:** STATE (when state_conditions match)

**Content schema:**
```json
{
    "mode_description": "What this mode is and when it activates",
    "behavior_override": "How Frank's behavior changes in this mode",
    "priority_logic": "What takes precedence in this mode"
}
```

**State conditions format:**
```json
{
    "conversation_count": 0,              // Direct match
    "user_type": ["CLINICIAN", "PROFESSIONAL"],  // List match (any of)
    "last_rating": {"lte": 2},            // Range: rating <= 2
    "days_since_last": {"gte": 7}         // Range: days >= 7
}
```

**Examples:**
| entity_id | Activates when |
|-----------|----------------|
| `handler_first_conversation` | conversation_count = 0 |
| `handler_returning_user` | days_since_last >= 7 |
| `handler_post_escalation` | last_rating <= 2 |
| `handler_celebrating_wins` | last_rating >= 4 |
| `handler_clinician_mode` | user_type in [CLINICIAN, PROFESSIONAL] |
| `handler_crisis` | Crisis patterns detected |
| `handler_interaction_debrief` | session_type = "debrief" |

**Priority:** 75-95 (varies by handler importance)

---

### 2.4 TOPIC

**Purpose:** Topical content - techniques, concepts, patterns that Frank can teach.

**When loaded:** SITUATION (retrieved via embedding search + keyword match)

**Content schema:**
```json
{
    "concept": "What this topic is - definition and explanation",
    "recognition": "How to recognize when user needs this (patterns, keywords)",
    "do": "What to do / how to apply this technique",
    "dont": "Common mistakes / what NOT to do",
    "examples": "Concrete examples of application",
    "red_flags": "Warning signs / when this applies especially"
}
```

**Examples:**
- `gray_rock` - The gray rock technique for dealing with difficult ex
- `biff_response` - Brief, Informative, Friendly, Firm responses
- `boundary_setting` - How to set and maintain boundaries
- `loyalty_binds` - When children are caught in the middle
- `parental_alienation` - Recognizing and responding to alienation

**Keywords field:** Comma-separated trigger words for retrieval
```
"gray rock, ignore, baiting, provoke, rise to it"
```

**Priority:** 50-70 (content relevance determined by retrieval)

---

### 2.5 RERANKER

**Purpose:** Meta-instructions for the KB ranking system.

**When loaded:** ALWAYS (used internally, not sent to user-facing LLM)

**Content schema:**
```json
{
    "ranking_instructions": "How to rank KB content by relevance",
    "signal_rules": "When to emit signals (crisis, followup)",
    "crisis_patterns": "Patterns that indicate crisis",
    "boost_rules": "When to boost certain content types"
}
```

**Example:** `reranker_core_guidance`

**Priority:** 90 (critical for retrieval quality)

---

### 2.6 CHAT_CONTEXT

**Purpose:** Chat-type-specific system prompts and retrieval hints.

**When loaded:** ALWAYS (one per chat session based on chat_type)

**Content schema:**
```json
{
    "system_prompt": "Additional system prompt for this chat type",
    "retrieval_hints": "What KB content is most relevant for this chat type",
    "onboarding_prompt": "How to start a new conversation of this type"
}
```

**Examples:** One per chat type (FAMILY_HISTORY, PARENT_CHILD, CO_PARENT, COURT_PREP, MISCELLANEOUS)

**Priority:** 85 (shapes entire conversation)

---

## 3. Chat Types (5)

| Order | Chat Type | Purpose | Audience | Typical KB Focus |
|-------|-----------|---------|----------|------------------|
| 1 | `FAMILY_HISTORY` | Family background and case intake | ALL | Initial context gathering, genogram, presenting concerns |
| 2 | `PARENT_CHILD` | Relationship with children | PARENT | Loyalty binds, reconnection, age-appropriate communication |
| 3 | `CO_PARENT` | Managing relationship with ex | PARENT | BIFF, gray rock, boundary setting, documentation |
| 4 | `COURT_PREP` | Legal proceedings | PARENT | Documentation, false allegations, court behavior |
| 5 | `MISCELLANEOUS` | Catch-all for other topics | ALL | Broad KB access |

**How targeting works:**
- `chat_types: []` (empty) = applies to ALL chat types
- `chat_types: ["CO_PARENT", "COURT_PREP"]` = only these specific types

---

## 4. Audience Types (3)

| Audience | Description | Persona Used |
|----------|-------------|--------------|
| `PARENT` | Parents going through co-parenting challenges | `frank_persona_parent` |
| `CLINICIAN` | Therapists, counselors, mental health professionals | `frank_persona_clinician` |
| `PROFESSIONAL` | Evaluators, attorneys, mediators | `frank_persona_clinician` |

**How targeting works:**
- `audience_types: ["PARENT"]` = only parents see this
- `audience_types: ["CLINICIAN", "PROFESSIONAL"]` = clinicians and professionals
- `audience_types: ["PARENT", "CLINICIAN", "PROFESSIONAL"]` = everyone

---

## 5. Load Modes (3)

| Mode | When Loaded | Cached? | Examples |
|------|-------------|---------|----------|
| `ALWAYS` | Session init | Yes (prompt cache) | PERSONA, core RULES, RERANKER |
| `STATE` | When state_conditions match | No | HANDLERs (crisis, first_conversation, etc.) |
| `SITUATION` | Embedding search + reranker | No | TOPIC (techniques, concepts) |

**Performance note:** ALWAYS content is cached using Anthropic's prompt caching, so it doesn't count against per-turn token costs after first turn.

---

## 6. Priority System

**Scale:** 0-100 (higher = more important)

| Range | Typical Use |
|-------|-------------|
| 95-100 | PERSONA, critical RULES |
| 85-94 | RERANKER, CHAT_CONTEXT, important HANDLERs |
| 75-84 | Standard HANDLERs |
| 50-74 | TOPIC (techniques, concepts) |
| 0-49 | Low-priority or supplemental content |

**How priority affects loading:**
1. ALWAYS content sorted by priority (highest first in prompt)
2. STATE content: matching handlers sorted by priority
3. SITUATION content: reranker considers priority as tiebreaker

---

## 7. Legacy Schema Mapping

The legacy `content_entities_legacy` table used separate columns. Here's how they map to JSONB:

### For TOPIC entities:

| Legacy Column | JSONB Field |
|---------------|-------------|
| `concept_summary` | `content.concept` |
| `content_summary` | `content.concept` (merge with above) |
| `guidance_do` | `content.do` |
| `guidance_dont` | `content.dont` |
| `examples` | `content.examples` |
| `red_flags` | `content.red_flags` |
| `recognition` | `recognition` column (not in JSONB) |
| `keywords` | `keywords` column (not in JSONB) |

### For RULE entities:

| Legacy Column | JSONB Field |
|---------------|-------------|
| `content_summary` | `content.constraint` |
| `guidance_do` | `content.required_action` |
| `guidance_dont` | `content.never_do` |
| `recognition` | `content.trigger_patterns` |

### For HANDLER entities:

| Legacy Column | JSONB Field |
|---------------|-------------|
| `content_summary` | `content.mode_description` |
| `guidance_do` | `content.behavior_override` |
| `state_conditions` | `state_conditions` column (already JSONB) |

### Legacy types to migrate:

| Legacy Type | New Type |
|-------------|----------|
| `RULE` | `RULE` |
| `SCRIPT` | `TOPIC` |
| `TOPIC` | `TOPIC` |
| `RULE` | `RULE` |
| `HANDLER` | `HANDLER` |
| `PERSONA` | `PERSONA` |

---

## 8. Content Deduplication Strategy

### When legacy DB (Part 1) and stripped-from-code (Part 3) conflict:

**Priority order:**
1. **Legacy DB wins** if it has richer content (do/dont/examples/red_flags populated)
2. **Stripped-from-code wins** if legacy is stub/placeholder
3. **Merge** if both have unique valuable content

### Specific known duplicates:

| Entity | Legacy DB | Stripped File | Resolution |
|--------|-----------|---------------|------------|
| `core_behavioral_guardrails` | HAS CONTENT | `nevers.md` | Compare and merge |
| `hipaa_privacy` | HAS CONTENT | `hipaa_privacy.md` | Compare and merge |
| `situational` | HAS CONTENT | `situational.md` | Compare and merge |
| All 7 handlers | HAS CONTENT | `frank_handlers/*.md` | Compare and merge |
| All 10 techniques | HAS CONTENT | `frank_techniques/*.md` | Compare and merge |

### Content that needs NEW entities (not in legacy):

| Source File | Suggested entity_id | Type |
|-------------|---------------------|------|
| `clinician/assessment_frameworks.md` | `assessment_frameworks` | TOPIC |
| `clinician/situational_guides/high_conflict.md` | `clinician_high_conflict` | TOPIC |
| `clinician/situational_guides/domestic_violence.md` | `clinician_domestic_violence` | TOPIC |
| `clinician/situational_guides/parental_alienation.md` | `clinician_parental_alienation` | TOPIC |
| `clinician/situational_guides/substance_abuse.md` | `clinician_substance_abuse` | TOPIC |

### Hardcoded patterns - where they go:

| Source | Destination |
|--------|-------------|
| `crisis_patterns.md` (8 regex patterns) | `reranker_core_guidance.content.crisis_patterns` |
| `technique_keywords.md` (10 keyword sets) | Each technique's `keywords` field |
| `rating_handler_selection.md` | Handler `state_conditions` fields |
| `returning_user_threshold.md` | `handler_returning_user.state_conditions` |

---

## 9. What the LLM Sees (to_prompt_text output)

The `to_prompt_text()` method formats entities for the LLM:

### PERSONA:
```
## Frank - Parent Coach Persona
I'm Frank, your co-parenting coach...
Voice: Conversational and warm. Use 'yeah' not 'yes'...
Approach: Motivational Interviewing at the core...
Never: Never give legal advice...
```

### RULE:
```
## Core Behavioral Guardrails
[constraint content]
Required: [required_action]
Never: [never_do]
```

### TOPIC:
```
## Gray Rock
[concept content]
Do: [do content]
Don't: [dont content]
Examples: [examples]
Red Flags: [red_flags]
```

---

## 10. Checklist for KB Content Review

When reviewing an entity for migration:

- [ ] **entity_id:** Snake_case, descriptive, unique
- [ ] **entity_type:** One of the 6 canonical types
- [ ] **title:** Human-readable, concise
- [ ] **content:** All required fields for that type populated
- [ ] **keywords:** Relevant trigger words (for TOPIC/SITUATION types)
- [ ] **recognition:** Natural language patterns (for TOPIC/SITUATION types)
- [ ] **load_mode:** Appropriate for the entity type
- [ ] **state_conditions:** Properly formatted if STATE mode
- [ ] **priority:** Reasonable for the entity type (see section 6)
- [ ] **audience_types:** Correctly targets intended audience
- [ ] **chat_types:** Correctly targets intended chat contexts (or empty for all)
- [ ] **No duplication:** Content doesn't duplicate another entity

---

## 11. Entity Counts Summary

| Type | Expected Count | Notes |
|------|----------------|-------|
| PERSONA | 4 | frank_persona_parent, frank_persona_clinician, user_context, quotes |
| RULE | 6 | Core behavioral, PII, loop prevention, clinical handbook, situational, HIPAA |
| HANDLER | 7 | Crisis, first_conversation, clinician_mode, post_escalation, returning_user, interaction_debrief, celebrating_wins |
| TOPIC | 27 | 22 from legacy + 5 new clinician |
| RERANKER | 1 | reranker_core_guidance |
| CHAT_CONTEXT | 5 | One per chat type (FAMILY_HISTORY, PARENT_CHILD, CO_PARENT, COURT_PREP, MISCELLANEOUS) |
| **TOTAL** | **~50** | After deduplication |

---

## 12. Questions to Answer During Review

For each entity being migrated:

1. **Is the content actionable?** Does it give Frank clear guidance on what to do?
2. **Is it distinct?** Does it cover something not covered elsewhere?
3. **Is the type correct?** Should this be TOPIC vs RULE vs HANDLER?
4. **Are the triggers right?** Will this entity be retrieved when needed?
5. **Is the audience appropriate?** Should clinicians see different content than parents?
6. **Is the priority reasonable?** Should this load before/after similar content?

---

*Document created: 2025-12-30*
*Updated: 2025-12-30 - Corrected chat types to canonical 5*
*For use by Claude instances reviewing KB content for V3.0 migration*
