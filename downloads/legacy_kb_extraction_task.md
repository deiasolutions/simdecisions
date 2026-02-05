# Legacy KB Extraction Task

**Purpose:** Extract all content currently in .md files and hardcoded in Python, organize into `docs/legacy_kb/` for audit and migration planning.

**For:** Claude Code
**Date:** 2025-12-29

---

## Task 1: Create Directory Structure

```
docs/
└── legacy_kb/
    ├── README.md                    # Index of all legacy content
    ├── frank_core/                  # From content/frank/core/
    ├── frank_guardrails/            # From content/frank/guardrails/
    ├── frank_handlers/              # From content/frank/handlers/
    ├── frank_techniques/            # From content/frank/techniques/
    ├── frank_dr_amy/                # From content/frank/dr_amy/
    ├── clinician/                   # From content/clinician/
    └── hardcoded/                   # Extracted from Python code
```

---

## Task 2: Move .md Files

### 2.1 Frank Core
**Source:** `content/frank/core/`
**Destination:** `docs/legacy_kb/frank_core/`

| File | Action |
|------|--------|
| frank_soul.md | COPY to destination |
| user_context.md | COPY to destination |

### 2.2 Frank Guardrails
**Source:** `content/frank/guardrails/`
**Destination:** `docs/legacy_kb/frank_guardrails/`

| File | Action |
|------|--------|
| nevers.md | COPY to destination |
| hipaa_privacy.md | COPY to destination |
| clinical_handbook_extracts.md | COPY to destination |
| situational.md | COPY to destination |

### 2.3 Frank Handlers
**Source:** `content/frank/handlers/`
**Destination:** `docs/legacy_kb/frank_handlers/`

| File | Action |
|------|--------|
| first_conversation.md | COPY to destination |
| returning_user.md | COPY to destination |
| crisis.md | COPY to destination |
| post_escalation.md | COPY to destination |
| celebrating_wins.md | COPY to destination |
| clinician_mode.md | COPY to destination |
| interaction_debrief.md | COPY to destination |

### 2.4 Frank Techniques
**Source:** `content/frank/techniques/`
**Destination:** `docs/legacy_kb/frank_techniques/`

| File | Action |
|------|--------|
| gray_rock.md | COPY to destination |
| biff_response.md | COPY to destination |
| medium_response_time.md | COPY to destination |
| boundary_setting.md | COPY to destination |
| de_escalation.md | COPY to destination |
| loyalty_binds.md | COPY to destination |
| transition_bridge.md | COPY to destination |
| psychological_splitting.md | COPY to destination |
| dialectical_thinking.md | COPY to destination |
| ambiguous_loss.md | COPY to destination |

### 2.5 Dr. Amy
**Source:** `content/frank/dr_amy/`
**Destination:** `docs/legacy_kb/frank_dr_amy/`

| File | Action |
|------|--------|
| quotes.md | COPY to destination |

### 2.6 Clinician Content
**Source:** `content/clinician/`
**Destination:** `docs/legacy_kb/clinician/`

| File | Action |
|------|--------|
| assessment_frameworks.md | COPY to destination |
| situational_guides/high_conflict.md | COPY to destination (flatten or preserve structure) |
| situational_guides/domestic_violence.md | COPY to destination |
| situational_guides/parental_alienation.md | COPY to destination |
| situational_guides/substance_abuse.md | COPY to destination |

---

## Task 3: Extract Hardcoded Content

For each hardcoded item, create an .md file in `docs/legacy_kb/hardcoded/` with this format:

```markdown
# [Name of Pattern/Logic]

## Source Location
**File:** `path/to/file.py`
**Lines:** XX-YY

## Purpose
[Explain what this code does and why it exists]

## Current Implementation
```python
[Paste the actual code]
```

## How It's Used
[Explain when/where this is called and what triggers it]

## Migration Notes
[Any notes about how this should translate to KB entities]
```

### 3.1 Crisis Patterns
**Source:** `services/frank_prompt_builder.py:60-70`
**Output:** `docs/legacy_kb/hardcoded/crisis_patterns.md`

Extract the CRISIS_PATTERNS list and document:
- Each regex pattern
- What it's trying to match
- How it triggers crisis handler

### 3.2 Technique Keywords
**Source:** `services/frank_prompt_builder.py:72-87`
**Output:** `docs/legacy_kb/hardcoded/technique_keywords.md`

Extract the TECHNIQUE_KEYWORDS dict and document:
- Each technique name
- Associated keywords
- How matching works (substring, case-insensitive)
- Max 2 techniques per message rule

### 3.3 Complexity Routing
**Source:** `services/ai_service.py:210-217`
**Output:** `docs/legacy_kb/hardcoded/complexity_routing.md`

Extract the determine_complexity function and document:
- Keywords that trigger complex routing
- Length threshold (200 chars)
- Note that this is currently unused

### 3.4 Threat Detection Patterns
**Source:** `services/threat_detection.py:14-42`
**Output:** `docs/legacy_kb/hardcoded/threat_detection.md`

Extract threat detection logic and document:
- Categories (legal, regulatory, violence, harassment, self_harm)
- Severity mapping (1-4 scale)
- How this interacts with other systems

### 3.5 Tier Access Control
**Source:** `services/chat_type_service.py:83-88`
**Output:** `docs/legacy_kb/hardcoded/tier_access_control.md`

Extract the tier logic and document:
- Which tiers get which access
- How this affects content filtering

### 3.6 Rating-Based Handler Selection
**Source:** `services/frank_prompt_builder.py:281-285`
**Output:** `docs/legacy_kb/hardcoded/rating_handler_selection.md`

Extract the rating logic and document:
- Rating thresholds (<=2, >=4)
- Which handlers are selected
- Priority when multiple conditions match

### 3.7 Returning User Threshold
**Source:** `services/frank_prompt_builder.py` (find exact location)
**Output:** `docs/legacy_kb/hardcoded/returning_user_threshold.md`

Document:
- The 7-day threshold
- How days_since_last is calculated
- What triggers returning_user handler

### 3.8 Session Type Guidance (if still hardcoded)
**Source:** `services/frank_prompt_builder.py` (SESSION_TYPE_GUIDANCE dict if exists)
**Output:** `docs/legacy_kb/hardcoded/session_type_guidance.md`

Document:
- Each session type
- Associated guidance text
- Note: partially migrated to chat_types table

---

## Task 4: Create README Index

Create `docs/legacy_kb/README.md` with:

```markdown
# Legacy KB Content Index

**Created:** 2025-12-29
**Purpose:** Audit of all content that needs migration to database KB

## Status Legend
- 🔴 NOT in KB - needs migration
- 🟡 PARTIALLY in KB - needs verification
- 🟢 IN KB - verify content matches

## File-Based Content

### Frank Core
| File | Status | KB Entity ID | Notes |
|------|--------|--------------|-------|
| frank_soul.md | 🔴 | - | Needs PERSONA entity |
| user_context.md | 🟡 | user_context | Template - verify variables |

### Frank Guardrails
| File | Status | KB Entity ID | Notes |
|------|--------|--------------|-------|
| nevers.md | 🟡 | core_behavioral_guardrails | Verify complete |
| ... | | | |

[Continue for all categories]

## Hardcoded Content

| Item | Status | Target KB Type | Notes |
|------|--------|----------------|-------|
| CRISIS_PATTERNS | 🔴 | GUARDRAIL triggers | 8 regex patterns |
| TECHNIQUE_KEYWORDS | 🔴 | Entity triggers field | 10 keyword sets |
| ... | | | |

## Migration Priority

1. **HIGH:** Crisis patterns, technique keywords (actively used)
2. **MEDIUM:** Frank soul, clinician content (needed for multi-audience)
3. **LOW:** Threat detection, complexity routing (may refactor)
```

---

## Task 5: Verification

After completing the extraction:

1. List any .md files found that weren't in the inventory above
2. List any hardcoded content patterns found that weren't in the inventory above
3. Note any files that don't exist (inventory was wrong)
4. Note file sizes/line counts for planning

---

## Output

When complete, provide:

1. Confirmation that directory structure was created
2. List of all files copied with source → destination
3. List of all hardcoded extractions created
4. Any discrepancies or issues found
5. The completed README.md content

---

## Notes

- COPY files, don't MOVE - we want the system to keep working
- Preserve original formatting in .md files
- Include line numbers in code extractions for easy reference
- Flag anything that looks like it might be additional hardcoded logic not listed above
