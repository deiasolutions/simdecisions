# V3.0 Service Migration Spec: Column → JSONB

**Date:** 2025-12-30
**Purpose:** Fix Python files to read from new JSONB `content` field
**Implementer:** Claude Code

---

## OVERVIEW

Four files still reference old column-based schema. They need updates to read from the new JSONB `content` field.

| File | Priority | Issue |
|------|----------|-------|
| `src/api/content_entities.py` | HIGH | Admin API broken - wrong columns, wrong types |
| `src/services/content_retrieval_service.py` | HIGH | Retrieval may fail or return empty |
| `src/services/reranker_service.py` | HIGH | Candidate formatting broken |
| `src/services/prompt_cache_service.py` | MEDIUM | Prompt building may fail |

---

## NEW SCHEMA REFERENCE

### Table: `content_entities`

```sql
content JSONB NOT NULL DEFAULT '{}'
```

### JSONB Structure by Type

**PERSONA:**
```json
{
  "identity": "string",
  "voice": "string", 
  "approach": "string",
  "anti_patterns": "string",
  "signature_elements": {}  // optional
}
```

**GUARDRAIL:**
```json
{
  "constraint": "string",
  "rules": {
    "do": ["array"],
    "dont": ["array"]
  },
  "scope": "string or object",  // optional
  "escalation_trigger": "string"  // optional
}
```

**HANDLER:**
```json
{
  "purpose": "string",
  "protocol": {},
  "rules": {
    "do": ["array"],
    "dont": ["array"]
  },
  "escalation_trigger": "string"  // optional
}
```

**KNOWLEDGE:**
```json
{
  "concept": "string",
  "guidance": {
    "do": ["array"],  // optional
    "dont": ["array"]  // optional
  },
  "examples": {},  // optional
  "frank_voice": "string"  // optional
}
```

**RERANKER:**
```json
{
  "purpose": "string",
  "scoring_criteria": {},
  "detection_patterns": {},
  "output_format": {}
}
```

**CHAT_CONTEXT:**
```json
{
  "purpose": "string",
  "focus_areas": ["array"],
  "retrieval_hints": ["array"],
  "onboarding_prompt": "string",
  "rules": {}  // optional
}
```

---

## FILE 1: `src/api/content_entities.py`

### Issues

1. `entity_to_response()` reads non-existent columns
2. `create_entity()` / `update_entity()` write to wrong columns
3. Entity type validation uses old types (SCRIPT, RULE)
4. Search/filter may break on missing columns

### Fix: `entity_to_response()`

**BEFORE:**
```python
def entity_to_response(entity: ContentEntity) -> dict:
    return {
        "id": str(entity.id),
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type,
        "title": entity.title,
        "concept_summary": entity.concept_summary,      # OLD
        "content_summary": entity.content_summary,      # OLD
        "guidance_do": entity.guidance_do,              # OLD
        "guidance_dont": entity.guidance_dont,          # OLD
        "examples": entity.examples,                    # OLD
        "red_flags": entity.red_flags,                  # OLD
        "keywords": entity.keywords,
        "recognition": entity.recognition,
        # ...
    }
```

**AFTER:**
```python
def entity_to_response(entity: ContentEntity) -> dict:
    content = entity.content or {}
    
    return {
        "id": str(entity.id),
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type,
        "subtype": entity.subtype,
        "title": entity.title,
        "content": content,  # Return full JSONB blob
        "keywords": entity.keywords,
        "recognition": entity.recognition,
        "load_mode": entity.load_mode,
        "state_conditions": entity.state_conditions,
        "priority": entity.priority,
        "audience_types": entity.audience_types,
        "chat_types": entity.chat_types,
        "attribution": entity.attribution,
        "editable_by": entity.editable_by,
        "is_active": entity.is_active,
        "created_at": entity.created_at.isoformat() if entity.created_at else None,
        "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
    }
```

### Fix: Entity Type Validation

**BEFORE:**
```python
VALID_TYPES = ["KNOWLEDGE", "SCRIPT", "RULE", "GUARDRAIL", "HANDLER", "PERSONA"]
```

**AFTER:**
```python
VALID_TYPES = ["PERSONA", "GUARDRAIL", "HANDLER", "KNOWLEDGE", "RERANKER", "CHAT_CONTEXT"]
```

### Fix: `create_entity()` / `update_entity()`

**BEFORE:**
```python
new_entity = ContentEntity(
    entity_id=data.get("entity_id"),
    entity_type=data.get("entity_type"),
    title=data.get("title"),
    concept_summary=data.get("concept_summary"),    # OLD
    content_summary=data.get("content_summary"),    # OLD
    guidance_do=data.get("guidance_do"),            # OLD
    guidance_dont=data.get("guidance_dont"),        # OLD
    # ...
)
```

**AFTER:**
```python
new_entity = ContentEntity(
    entity_id=data.get("entity_id"),
    entity_type=data.get("entity_type"),
    subtype=data.get("subtype"),
    title=data.get("title"),
    content=data.get("content", {}),  # JSONB blob
    keywords=data.get("keywords"),
    recognition=data.get("recognition"),
    load_mode=data.get("load_mode", "SITUATION"),
    state_conditions=data.get("state_conditions"),
    priority=data.get("priority", 50),
    audience_types=data.get("audience_types", ["PARENT"]),
    chat_types=data.get("chat_types", []),
    attribution=data.get("attribution"),
    editable_by=data.get("editable_by", "ADMIN"),
    is_active=data.get("is_active", True),
)
```

---

## FILE 2: `src/services/content_retrieval_service.py`

### Issues

1. May format entities using old column names
2. `get_entity_text_for_embedding()` likely broken
3. Entity filtering may reference wrong fields

### Fix: `get_entity_text_for_embedding()`

**BEFORE:**
```python
def get_entity_text_for_embedding(entity: ContentEntity) -> str:
    parts = [
        entity.title or "",
        entity.concept_summary or "",
        entity.content_summary or "",
        entity.keywords or "",
    ]
    return " ".join(filter(None, parts))
```

**AFTER:**
```python
def get_entity_text_for_embedding(entity: ContentEntity) -> str:
    content = entity.content or {}
    
    # Extract text based on entity type
    text_parts = [entity.title or ""]
    
    if entity.entity_type == "KNOWLEDGE":
        text_parts.append(content.get("concept", ""))
        text_parts.append(content.get("frank_voice", ""))
    elif entity.entity_type == "PERSONA":
        text_parts.append(content.get("identity", ""))
        text_parts.append(content.get("voice", ""))
    elif entity.entity_type == "GUARDRAIL":
        text_parts.append(content.get("constraint", ""))
    elif entity.entity_type == "HANDLER":
        text_parts.append(content.get("purpose", ""))
    elif entity.entity_type == "CHAT_CONTEXT":
        text_parts.append(content.get("purpose", ""))
        text_parts.append(" ".join(content.get("focus_areas", [])))
    elif entity.entity_type == "RERANKER":
        text_parts.append(content.get("purpose", ""))
    
    # Always include keywords and recognition
    text_parts.append(entity.keywords or "")
    text_parts.append(entity.recognition or "")
    
    return " ".join(filter(None, text_parts))
```

### Fix: Entity Formatting for Context

If there's a method that formats entity content for inclusion in prompts:

**AFTER:**
```python
def format_entity_for_prompt(entity: ContentEntity) -> str:
    """Format entity content for LLM prompt inclusion."""
    content = entity.content or {}
    lines = [f"## {entity.title}"]
    
    if entity.entity_type == "KNOWLEDGE":
        if content.get("concept"):
            lines.append(content["concept"])
        if content.get("guidance", {}).get("do"):
            lines.append("Do: " + "; ".join(content["guidance"]["do"]))
        if content.get("guidance", {}).get("dont"):
            lines.append("Don't: " + "; ".join(content["guidance"]["dont"]))
        if content.get("frank_voice"):
            lines.append(f"Frank says: {content['frank_voice']}")
            
    elif entity.entity_type == "PERSONA":
        if content.get("identity"):
            lines.append(content["identity"])
        if content.get("voice"):
            lines.append(f"Voice: {content['voice']}")
        if content.get("approach"):
            lines.append(f"Approach: {content['approach']}")
        if content.get("anti_patterns"):
            lines.append(f"Never: {content['anti_patterns']}")
            
    elif entity.entity_type == "GUARDRAIL":
        if content.get("constraint"):
            lines.append(content["constraint"])
        rules = content.get("rules", {})
        if rules.get("do"):
            lines.append("Required: " + "; ".join(rules["do"]))
        if rules.get("dont"):
            lines.append("Never: " + "; ".join(rules["dont"]))
            
    elif entity.entity_type == "HANDLER":
        if content.get("purpose"):
            lines.append(content["purpose"])
        if content.get("protocol"):
            # Format protocol based on structure
            protocol = content["protocol"]
            if isinstance(protocol, dict):
                for key, value in protocol.items():
                    if isinstance(value, str):
                        lines.append(f"{key}: {value}")
        rules = content.get("rules", {})
        if rules.get("do"):
            lines.append("Do: " + "; ".join(rules["do"]))
        if rules.get("dont"):
            lines.append("Don't: " + "; ".join(rules["dont"]))
            
    elif entity.entity_type == "CHAT_CONTEXT":
        if content.get("purpose"):
            lines.append(content["purpose"])
        if content.get("focus_areas"):
            lines.append("Focus: " + ", ".join(content["focus_areas"]))
        if content.get("onboarding_prompt"):
            lines.append(f"Opening: {content['onboarding_prompt']}")
            
    elif entity.entity_type == "RERANKER":
        # Reranker content is for internal use, not user-facing
        if content.get("purpose"):
            lines.append(content["purpose"])
    
    return "\n".join(lines)
```

---

## FILE 3: `src/services/reranker_service.py`

### Issues

1. `format_candidates_for_reranker()` uses old columns
2. Crisis pattern extraction may fail
3. Result parsing may expect wrong structure

### Fix: `format_candidates_for_reranker()`

**BEFORE:**
```python
def format_candidates_for_reranker(entities: List[ContentEntity]) -> str:
    formatted = []
    for i, entity in enumerate(entities):
        formatted.append(f"""
Candidate {i+1}: {entity.entity_id}
Type: {entity.entity_type}
Title: {entity.title}
Summary: {entity.concept_summary or entity.content_summary}
Keywords: {entity.keywords}
""")
    return "\n".join(formatted)
```

**AFTER:**
```python
def format_candidates_for_reranker(entities: List[ContentEntity]) -> str:
    formatted = []
    for i, entity in enumerate(entities):
        content = entity.content or {}
        
        # Get summary based on type
        if entity.entity_type == "KNOWLEDGE":
            summary = content.get("concept", "")[:500]
        elif entity.entity_type == "PERSONA":
            summary = content.get("identity", "")[:500]
        elif entity.entity_type == "GUARDRAIL":
            summary = content.get("constraint", "")[:500]
        elif entity.entity_type == "HANDLER":
            summary = content.get("purpose", "")[:500]
        elif entity.entity_type == "CHAT_CONTEXT":
            summary = content.get("purpose", "")[:500]
        else:
            summary = str(content)[:500]
        
        formatted.append(f"""
Candidate {i+1}: {entity.entity_id}
Type: {entity.entity_type}
Title: {entity.title}
Summary: {summary}
Keywords: {entity.keywords or ""}
""")
    return "\n".join(formatted)
```

### Fix: Crisis Pattern Loading

If crisis patterns are loaded from `reranker_core_guidance` entity:

**AFTER:**
```python
def get_crisis_patterns(self) -> dict:
    """Load crisis patterns from reranker entity."""
    entity = self.get_entity_by_id("reranker_core_guidance")
    if not entity:
        return self._default_crisis_patterns()
    
    content = entity.content or {}
    detection = content.get("detection_patterns", {})
    crisis = detection.get("crisis_detection", {})
    
    return {
        "phrase_patterns": crisis.get("phrase_patterns", {}),
        "regex_patterns": crisis.get("regex_patterns", []),
        "severity_levels": crisis.get("severity_levels", {})
    }
```

---

## FILE 4: `src/services/prompt_cache_service.py`

### Issues

1. `build_system_prompt()` may use old column access
2. ALWAYS-load entity formatting broken

### Fix: System Prompt Building

**AFTER:**
```python
def build_system_prompt(self, user_type: str, chat_type: str) -> str:
    """Build cached system prompt from ALWAYS-load entities."""
    parts = []
    
    # Get ALWAYS entities filtered by audience
    always_entities = self.get_entities_by_load_mode(
        load_mode="ALWAYS",
        audience_type=user_type
    )
    
    # Sort by priority (highest first)
    always_entities.sort(key=lambda e: e.priority or 0, reverse=True)
    
    for entity in always_entities:
        formatted = self.format_entity_for_prompt(entity)
        if formatted:
            parts.append(formatted)
    
    return "\n\n---\n\n".join(parts)


def format_entity_for_prompt(self, entity: ContentEntity) -> str:
    """Format single entity for prompt inclusion."""
    content = entity.content or {}
    
    if entity.entity_type == "PERSONA":
        return self._format_persona(entity.title, content)
    elif entity.entity_type == "GUARDRAIL":
        return self._format_guardrail(entity.title, content)
    elif entity.entity_type == "RERANKER":
        return ""  # Reranker not included in user-facing prompt
    else:
        return self._format_generic(entity.title, content)


def _format_persona(self, title: str, content: dict) -> str:
    lines = [f"# {title}"]
    if content.get("identity"):
        lines.append(content["identity"])
    if content.get("voice"):
        lines.append(f"\n## Voice\n{content['voice']}")
    if content.get("approach"):
        lines.append(f"\n## Approach\n{content['approach']}")
    if content.get("anti_patterns"):
        lines.append(f"\n## Never\n{content['anti_patterns']}")
    return "\n".join(lines)


def _format_guardrail(self, title: str, content: dict) -> str:
    lines = [f"# {title}"]
    if content.get("constraint"):
        lines.append(content["constraint"])
    rules = content.get("rules", {})
    if rules.get("do"):
        lines.append("\nRequired:")
        for item in rules["do"]:
            lines.append(f"- {item}")
    if rules.get("dont"):
        lines.append("\nNever:")
        for item in rules["dont"]:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _format_generic(self, title: str, content: dict) -> str:
    """Generic formatting for other types."""
    lines = [f"# {title}"]
    for key, value in content.items():
        if isinstance(value, str):
            lines.append(f"\n## {key.replace('_', ' ').title()}\n{value}")
        elif isinstance(value, list):
            lines.append(f"\n## {key.replace('_', ' ').title()}")
            for item in value:
                lines.append(f"- {item}")
    return "\n".join(lines)
```

---

## ADDITIONAL: Model Update Check

### File: `src/models/content_entity.py`

Verify the model matches new schema:

```python
class ContentEntity(Base):
    __tablename__ = "content_entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String(100), unique=True, nullable=False)
    entity_type = Column(String(20), nullable=False)
    subtype = Column(String(50))
    title = Column(String(255), nullable=False)
    content = Column(JSONB, nullable=False, default=dict)  # THE KEY FIELD
    keywords = Column(String(500))
    recognition = Column(Text)
    embedding = Column(JSONB)
    load_mode = Column(String(20), nullable=False, default="SITUATION")
    state_conditions = Column(JSONB)
    priority = Column(Integer, default=50)
    audience_types = Column(JSONB, default=["PARENT"])
    chat_types = Column(JSONB, default=[])
    attribution = Column(JSONB)
    editable_by = Column(String(20), default="ADMIN")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
```

**Remove these columns if present (old schema):**
- `concept_summary`
- `content_summary`
- `guidance_do`
- `guidance_dont`
- `examples`
- `red_flags`

---

## TESTING AFTER FIXES

1. **API Test:**
```bash
curl http://localhost:8000/api/content-entities/ | jq '.[] | {entity_id, entity_type}'
```

2. **Retrieval Test:**
```python
from src.services.content_retrieval_service import ContentRetrievalService
svc = ContentRetrievalService()
entities = svc.get_entities_by_type("KNOWLEDGE")
for e in entities[:3]:
    print(e.entity_id, e.content.keys())
```

3. **Reranker Test:**
```python
from src.services.reranker_service import RerankerService
svc = RerankerService()
patterns = svc.get_crisis_patterns()
print(patterns.keys())
```

---

## IMPLEMENTATION ORDER

1. **Update Model** (`content_entity.py`) — Ensure JSONB field exists
2. **Update API** (`content_entities.py`) — Fix admin endpoint
3. **Update Retrieval** (`content_retrieval_service.py`) — Fix embedding/formatting
4. **Update Reranker** (`reranker_service.py`) — Fix candidate formatting
5. **Update Prompt Cache** (`prompt_cache_service.py`) — Fix prompt building
6. **Run Tests** — Verify all layers work

---

*Spec created: 2025-12-30*
*For implementation by Claude Code*
