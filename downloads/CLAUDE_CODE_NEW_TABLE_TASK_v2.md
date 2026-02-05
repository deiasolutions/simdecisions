# Claude Code Task: New Content Table Schema

**Date:** 2025-12-15  
**Assigned To:** Claude Code  
**Priority:** HIGH  
**Replaces:** Previous schema task, CLAUDE_CODE_NEW_TABLE_TASK.md

---

## Overview

Create a NEW `content_entities` table with a clean schema. Rename the existing table to `content_entities_deprecated`. Do NOT migrate data - content will be loaded via a separate script after schema is ready.

---

## STEP 1: Pre-flight Checks

Before making changes, verify:

```python
# Check if deprecated table already exists (indicates script already ran)
# Check if new table already exists
# Check for foreign key references to content_entities
```

---

## STEP 2: Rename Existing Table

```sql
ALTER TABLE content_entities RENAME TO content_entities_deprecated;
```

---

## STEP 3: Create New Table

```sql
CREATE TABLE content_entities (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(100) UNIQUE NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- PERSONA, GUARDRAIL, HANDLER, KNOWLEDGE, SCRIPT, RULE
    subtype VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    
    -- Retrieval (what goes into embedding)
    concept_summary TEXT,              -- Clean 2-3 sentence summary for LLM context
    recognition TEXT,                  -- Parent + clinician phrases for semantic matching
    keywords VARCHAR(500),             -- Comma-separated single words for exact match
    
    -- Response Guidance (what Frank DOES - injected into prompt, NOT in embedding)
    -- Primarily used by KNOWLEDGE type, optional for others
    guidance_do TEXT,                  -- Templated: [Do say...] [Do ask...] [Do do...]
    guidance_dont TEXT,                -- Templated: [Don't say...] [Don't do...]
    examples TEXT,                     -- Sample parent/Frank exchanges
    red_flags TEXT,                    -- Escalation triggers
    
    -- Load Configuration
    load_mode VARCHAR(20) NOT NULL DEFAULT 'SITUATION',  -- ALWAYS, STATE, SITUATION
    priority INTEGER NOT NULL DEFAULT 50,                 -- 0-100
    state_conditions JSONB,                               -- For STATE load mode
    
    -- Audience
    audience_types VARCHAR(100) DEFAULT 'PARENT,CLINICIAN',
    
    -- Embedding
    embedding JSONB,                   -- Voyage AI 1024-dim vector stored as JSON array
    
    -- Attribution
    source_author VARCHAR(255),
    source_title VARCHAR(255),
    source_year INTEGER,
    
    -- Admin
    editable_by VARCHAR(50) DEFAULT 'TRAINER',  -- ADMIN, TRAINER, HIDDEN
    is_active INTEGER DEFAULT 1,
    retrieval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- Indexes
CREATE INDEX idx_ce_entity_type ON content_entities(entity_type);
CREATE INDEX idx_ce_load_mode ON content_entities(load_mode);
CREATE INDEX idx_ce_priority ON content_entities(priority);
CREATE INDEX idx_ce_is_active ON content_entities(is_active);
```

**Note:** `entity_id` already has a unique constraint which creates an implicit index.

**Note on embedding column:** Check if pgvector extension is installed. If yes, use `VECTOR(1024)`. If no, fall back to `JSONB`.

---

## STEP 4: Update SQLAlchemy Model

Replace `src/models/content_entity.py`:

```python
"""Content Entity model for FBB knowledge base."""

from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from database import Base


class ContentEntity(Base):
    """
    Content entity for RAG retrieval and response guidance.
    
    RETRIEVAL FIELDS (used for embedding):
        - title
        - concept_summary
        - recognition
        - keywords (exact match, not embedded)
    
    RESPONSE FIELDS (injected into prompt AFTER retrieval, NOT in embedding):
        - guidance_do
        - guidance_dont
        - examples
        - red_flags
    
    ENTITY TYPE USAGE:
        - PERSONA: concept_summary only (guidance fields not used)
        - GUARDRAIL: concept_summary, guidance_dont, red_flags
        - HANDLER: concept_summary, guidance_do, state_conditions
        - KNOWLEDGE: ALL fields
        - SCRIPT: concept_summary, guidance_do, examples
        - RULE: concept_summary, red_flags
    """
    
    __tablename__ = "content_entities"
    
    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String(100), unique=True, nullable=False)
    entity_type = Column(String(50), nullable=False)
    subtype = Column(String(50))
    title = Column(String(255), nullable=False)
    
    # Retrieval (for embedding)
    concept_summary = Column(Text)
    recognition = Column(Text)
    keywords = Column(String(500))
    
    # Response Guidance (for prompt, NOT embedding)
    guidance_do = Column(Text)
    guidance_dont = Column(Text)
    examples = Column(Text)
    red_flags = Column(Text)
    
    # Load Configuration
    load_mode = Column(String(20), nullable=False, default='SITUATION')
    priority = Column(Integer, nullable=False, default=50)
    state_conditions = Column(JSONB)
    
    # Audience
    audience_types = Column(String(100), default='PARENT,CLINICIAN')
    
    # Embedding
    embedding = Column(JSONB)  # Or pgvector if available
    
    # Attribution
    source_author = Column(String(255))
    source_title = Column(String(255))
    source_year = Column(Integer)
    
    # Admin
    editable_by = Column(String(50), default='TRAINER')
    is_active = Column(Integer, default=1)
    retrieval_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    
    def __repr__(self):
        return f"<ContentEntity {self.entity_id} ({self.entity_type})>"
    
    @property
    def has_embedding(self):
        """Check if embedding exists."""
        return self.embedding is not None and len(self.embedding) > 0
    
    def matches_keyword(self, message_lower: str) -> bool:
        """Check if any keyword matches the message."""
        if not self.keywords:
            return False
        keyword_list = [k.strip().lower() for k in self.keywords.split(',')]
        return any(kw in message_lower for kw in keyword_list if kw)
    
    def to_embedding_text(self) -> str:
        """
        Generate text for embedding - retrieval fields only.
        
        INCLUDES: title, concept_summary, recognition
        EXCLUDES: guidance_do, guidance_dont, examples, red_flags, keywords
        """
        parts = [self.title]
        if self.concept_summary:
            parts.append(self.concept_summary)
        if self.recognition:
            parts.append(f"Recognition phrases: {self.recognition}")
        return ". ".join(parts)
    
    def to_prompt_text(self) -> str:
        """
        Generate text for prompt injection - includes response guidance.
        Called AFTER entity is retrieved.
        """
        sections = [f"## {self.title}"]
        
        if self.concept_summary:
            sections.append(self.concept_summary)
        
        if self.guidance_do:
            sections.append(f"\n**Guidance:**\n{self.guidance_do}")
        
        if self.guidance_dont:
            sections.append(f"\n**Avoid:**\n{self.guidance_dont}")
        
        if self.examples:
            sections.append(f"\n**Example:**\n{self.examples}")
        
        if self.red_flags:
            sections.append(f"\n**Red Flags - Escalate if:**\n{self.red_flags}")
        
        return "\n".join(sections)
```

---

## STEP 5: Update Content Retrieval Service

In `src/services/content_retrieval_service.py`, update field references:

**OLD → NEW field mapping:**
```python
# OLD                      → NEW
situation_keywords         → keywords
situation_phrases          → recognition
content_summary            → concept_summary
content_detailed           → (removed - use to_prompt_text())
```

Update the keyword matching:
```python
# OLD
if entity.situation_keywords:
    keywords = [k.strip().lower() for k in entity.situation_keywords.split(',')]

# NEW
if entity.keywords:
    keywords = [k.strip().lower() for k in entity.keywords.split(',')]
```

Update embedding text generation to call `entity.to_embedding_text()`.

---

## STEP 6: Update Embedding Service

In `src/services/embedding_service.py`:

```python
async def generate_embedding_for_entity(self, entity: ContentEntity) -> list[float]:
    """
    Generate embedding for a content entity.
    Uses only retrieval fields (title, concept_summary, recognition).
    """
    text = entity.to_embedding_text()
    return await self.generate_embedding(text)


async def regenerate_all_embeddings(self, db: Session) -> dict:
    """
    Regenerate embeddings for all active entities.
    Call this after content is loaded into new table.
    """
    entities = db.query(ContentEntity).filter(ContentEntity.is_active == 1).all()
    
    results = {"success": 0, "failed": 0, "errors": []}
    
    for entity in entities:
        try:
            embedding = await self.generate_embedding_for_entity(entity)
            entity.embedding = embedding
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"entity_id": entity.entity_id, "error": str(e)})
    
    db.commit()
    return results
```

---

## STEP 7: Update Prompt Prep Service

In `src/services/prompt_prep_service.py`:

```python
def format_knowledge_for_prompt(entity: ContentEntity) -> str:
    """
    Format KNOWLEDGE entity for prompt injection.
    Uses to_prompt_text() which includes response guidance.
    """
    return entity.to_prompt_text()
```

---

## STEP 8: Update API Router

Update `src/routers/content_entities.py`:

### Add Embedding Regeneration Endpoint

```python
@router.post("/{entity_id}/regenerate-embedding")
async def regenerate_entity_embedding(
    entity_id: str,
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends()
):
    """Regenerate embedding for a single entity."""
    entity = db.query(ContentEntity).filter(
        ContentEntity.entity_id == entity_id
    ).first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    text = entity.to_embedding_text()
    embedding = await embedding_service.generate_embedding(text)
    entity.embedding = embedding
    db.commit()
    
    return {"status": "ok", "entity_id": entity_id, "dimensions": len(embedding)}


@router.post("/regenerate-all-embeddings")
async def regenerate_all_embeddings(
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends()
):
    """Regenerate embeddings for all active entities. Admin only."""
    entities = db.query(ContentEntity).filter(ContentEntity.is_active == 1).all()
    
    results = {"success": 0, "failed": 0, "errors": []}
    
    for entity in entities:
        try:
            text = entity.to_embedding_text()
            embedding = await embedding_service.generate_embedding(text)
            entity.embedding = embedding
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"entity_id": entity.entity_id, "error": str(e)})
    
    db.commit()
    return results
```

### Pydantic Models

```python
from pydantic import BaseModel
from typing import Optional


class ContentEntityCreate(BaseModel):
    entity_id: str
    entity_type: str
    title: str
    subtype: Optional[str] = None
    
    # Retrieval
    concept_summary: Optional[str] = None
    recognition: Optional[str] = None
    keywords: Optional[str] = None
    
    # Response guidance
    guidance_do: Optional[str] = None
    guidance_dont: Optional[str] = None
    examples: Optional[str] = None
    red_flags: Optional[str] = None
    
    # Config
    load_mode: str = "SITUATION"
    priority: int = 50
    state_conditions: Optional[dict] = None
    audience_types: str = "PARENT,CLINICIAN"
    
    # Attribution
    source_author: Optional[str] = None
    source_title: Optional[str] = None
    source_year: Optional[int] = None
    
    # Admin
    editable_by: str = "TRAINER"
    is_active: int = 1


class ContentEntityUpdate(BaseModel):
    title: Optional[str] = None
    subtype: Optional[str] = None
    concept_summary: Optional[str] = None
    recognition: Optional[str] = None
    keywords: Optional[str] = None
    guidance_do: Optional[str] = None
    guidance_dont: Optional[str] = None
    examples: Optional[str] = None
    red_flags: Optional[str] = None
    load_mode: Optional[str] = None
    priority: Optional[int] = None
    state_conditions: Optional[dict] = None
    audience_types: Optional[str] = None
    source_author: Optional[str] = None
    source_title: Optional[str] = None
    source_year: Optional[int] = None
    editable_by: Optional[str] = None
    is_active: Optional[int] = None


class ContentEntityResponse(BaseModel):
    """Response model - includes computed fields."""
    id: str  # UUID as string
    entity_id: str
    entity_type: str
    title: str
    subtype: Optional[str]
    concept_summary: Optional[str]
    recognition: Optional[str]
    keywords: Optional[str]
    guidance_do: Optional[str]
    guidance_dont: Optional[str]
    examples: Optional[str]
    red_flags: Optional[str]
    load_mode: str
    priority: int
    state_conditions: Optional[dict]
    audience_types: str
    has_embedding: bool  # Computed from embedding field
    source_author: Optional[str]
    source_title: Optional[str]
    source_year: Optional[int]
    editable_by: str
    is_active: int
    retrieval_count: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
```

---

## STEP 9: Update Admin UI - Content Entity Editor

Update `frontend/src/components/admin/ContentEntityEditor.tsx`:

### Form Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ CONTENT ENTITY EDITOR                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ IDENTITY ─────────────────────────────────────────────────┐ │
│ │ Entity ID: [____________]  Type: [KNOWLEDGE ▼]             │ │
│ │ Title: [______________________________________________]    │ │
│ │ Subtype: [____________]                                    │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ RETRIEVAL (used for matching) ────────────────────────────┐ │
│ │                                                             │ │
│ │ Concept Summary: (2-3 sentences - what is this?)           │ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 3 rows]                                    │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ │ Recognition: (what parents + clinicians say - for matching)│ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 6 rows, pre-populated with template]       │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ │ Keywords: (exact match, comma-separated)                   │ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [single-line input]                                    │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ RESPONSE GUIDANCE (what Frank does) ──────────────────────┐ │
│ │                                                             │ │
│ │ DO:                                                        │ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 8 rows, pre-populated with template]       │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ │ DON'T:                                                     │ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 6 rows, pre-populated with template]       │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ EXAMPLES ─────────────────────────────────────────────────┐ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 8 rows, pre-populated with template]       │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ RED FLAGS ────────────────────────────────────────────────┐ │
│ │ ┌────────────────────────────────────────────────────────┐ │ │
│ │ │ [textarea - 3 rows]                                    │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ CONFIGURATION ────────────────────────────────────────────┐ │
│ │ Load Mode: [SITUATION ▼]  Priority: [60]                   │ │
│ │ Audience: [PARENT,CLINICIAN_________]                      │ │
│ │ Editable By: [TRAINER ▼]  Active: [x]                      │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ ATTRIBUTION ──────────────────────────────────────────────┐ │
│ │ Author: [________________]  Title: [____________________]  │ │
│ │ Year: [____]                                               │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ STATUS ───────────────────────────────────────────────────┐ │
│ │ Has Embedding: ✓ Yes | Retrieval Count: 47                 │ │
│ │ Created: 2025-12-15 | Updated: 2025-12-15                  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                              [Cancel]  [Save]  [Save & Embed]  │
└─────────────────────────────────────────────────────────────────┘
```

### New Entry Pre-population (KNOWLEDGE type only)

When creating a NEW entity with type = KNOWLEDGE, pre-populate:

**recognition:**
```
[What parents say...]


[What clinicians report...]

```

**guidance_do:**
```
[Do say...]


[Do ask...]


[Do do...]

```

**guidance_dont:**
```
[Don't say...]


[Don't do...]

```

**examples:**
```
Parent: ""

Frank: ""
```

### Conditional Field Display

Show/hide sections based on entity_type:

| Field | PERSONA | GUARDRAIL | HANDLER | KNOWLEDGE | SCRIPT | RULE |
|-------|---------|-----------|---------|-----------|--------|------|
| concept_summary | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| recognition | - | - | - | ✓ | ✓ | ✓ |
| keywords | - | - | - | ✓ | ✓ | ✓ |
| guidance_do | - | - | ✓ | ✓ | ✓ | - |
| guidance_dont | - | ✓ | - | ✓ | - | - |
| examples | - | - | - | ✓ | ✓ | - |
| red_flags | - | ✓ | - | ✓ | - | ✓ |
| state_conditions | - | - | ✓ | - | - | - |

---

## STEP 10: Create Schema Script

Create `scripts/create_new_content_table.py`:

```python
#!/usr/bin/env python3
"""
Create new content_entities table and rename old one.

Usage:
    python scripts/create_new_content_table.py --dry-run
    python scripts/create_new_content_table.py --execute
    python scripts/create_new_content_table.py --rollback  # Undo changes
"""

import argparse
import os
import sys
from sqlalchemy import create_engine, text, inspect


def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    return url


def table_exists(engine, table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_foreign_keys(engine) -> list:
    """Check for foreign keys referencing content_entities."""
    sql = """
    SELECT 
        tc.table_name, 
        kcu.column_name,
        ccu.table_name AS foreign_table_name
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND ccu.table_name = 'content_entities';
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return list(result.fetchall())


def run_migration(dry_run: bool = True):
    engine = create_engine(get_database_url())
    
    # Pre-flight checks
    print("=== PRE-FLIGHT CHECKS ===")
    
    if table_exists(engine, 'content_entities_deprecated'):
        print("WARNING: content_entities_deprecated already exists.")
        print("  This may indicate the script already ran.")
        if not dry_run:
            response = input("  Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
    
    if not table_exists(engine, 'content_entities'):
        print("ERROR: content_entities table does not exist. Nothing to migrate.")
        return
    
    fk_refs = check_foreign_keys(engine)
    if fk_refs:
        print(f"WARNING: Found {len(fk_refs)} foreign key references to content_entities:")
        for ref in fk_refs:
            print(f"  - {ref[0]}.{ref[1]} -> content_entities")
        print("  These may need to be updated after migration.")
    
    print("\n=== MIGRATION ===")
    
    statements = [
        ("Rename old table", 
         "ALTER TABLE content_entities RENAME TO content_entities_deprecated"),
        
        ("Create new table", """
CREATE TABLE content_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(100) UNIQUE NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    
    concept_summary TEXT,
    recognition TEXT,
    keywords VARCHAR(500),
    
    guidance_do TEXT,
    guidance_dont TEXT,
    examples TEXT,
    red_flags TEXT,
    
    load_mode VARCHAR(20) NOT NULL DEFAULT 'SITUATION',
    priority INTEGER NOT NULL DEFAULT 50,
    state_conditions JSONB,
    
    audience_types VARCHAR(100) DEFAULT 'PARENT,CLINICIAN',
    
    embedding JSONB,
    
    source_author VARCHAR(255),
    source_title VARCHAR(255),
    source_year INTEGER,
    
    editable_by VARCHAR(50) DEFAULT 'TRAINER',
    is_active INTEGER DEFAULT 1,
    retrieval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100)
)"""),
        
        ("Create entity_type index", 
         "CREATE INDEX idx_ce_entity_type ON content_entities(entity_type)"),
        ("Create load_mode index", 
         "CREATE INDEX idx_ce_load_mode ON content_entities(load_mode)"),
        ("Create priority index", 
         "CREATE INDEX idx_ce_priority ON content_entities(priority)"),
        ("Create is_active index", 
         "CREATE INDEX idx_ce_is_active ON content_entities(is_active)"),
    ]
    
    with engine.connect() as conn:
        for desc, sql in statements:
            if dry_run:
                print(f"[DRY RUN] {desc}")
            else:
                try:
                    conn.execute(text(sql))
                    print(f"[OK] {desc}")
                except Exception as e:
                    print(f"[ERROR] {desc}: {e}")
                    conn.rollback()
                    raise
        
        if not dry_run:
            conn.commit()
            print("\n=== MIGRATION COMPLETE ===")
            print("Next steps:")
            print("  1. Load content into new table")
            print("  2. Run embedding generation script")
            print("  3. Test retrieval")


def run_rollback(dry_run: bool = True):
    """Rollback: drop new table, rename deprecated back."""
    engine = create_engine(get_database_url())
    
    print("=== ROLLBACK ===")
    
    if not table_exists(engine, 'content_entities_deprecated'):
        print("ERROR: content_entities_deprecated does not exist. Cannot rollback.")
        return
    
    statements = [
        ("Drop new table (if exists)", 
         "DROP TABLE IF EXISTS content_entities"),
        ("Rename deprecated back to original", 
         "ALTER TABLE content_entities_deprecated RENAME TO content_entities"),
    ]
    
    with engine.connect() as conn:
        for desc, sql in statements:
            if dry_run:
                print(f"[DRY RUN] {desc}")
            else:
                try:
                    conn.execute(text(sql))
                    print(f"[OK] {desc}")
                except Exception as e:
                    print(f"[ERROR] {desc}: {e}")
                    raise
        
        if not dry_run:
            conn.commit()
            print("\n=== ROLLBACK COMPLETE ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create new content_entities table")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes (default)")
    parser.add_argument("--execute", action="store_true", help="Actually run the operation")
    parser.add_argument("--rollback", action="store_true", help="Rollback: drop new table, restore old")
    args = parser.parse_args()
    
    if not args.execute and not args.dry_run:
        args.dry_run = True  # Default to dry-run
    
    if args.rollback:
        if args.execute:
            run_rollback(dry_run=False)
        else:
            print("Rollback DRY RUN (add --execute to actually rollback):")
            run_rollback(dry_run=True)
    elif args.execute:
        run_migration(dry_run=False)
    else:
        run_migration(dry_run=True)
```

---

## STEP 11: Create Embedding Generation Script

Create `scripts/generate_embeddings.py`:

```python
#!/usr/bin/env python3
"""
Generate embeddings for all active content entities.

Run AFTER content is loaded into the new table.

Usage:
    python scripts/generate_embeddings.py --dry-run
    python scripts/generate_embeddings.py --execute
    python scripts/generate_embeddings.py --execute --entity-id parental_alienation
"""

import argparse
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.content_entity import ContentEntity
from services.embedding_service import EmbeddingService


def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    return url


async def generate_embeddings(dry_run: bool = True, entity_id: str = None):
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    db = Session()
    
    embedding_service = EmbeddingService()
    
    # Query entities
    query = db.query(ContentEntity).filter(ContentEntity.is_active == 1)
    if entity_id:
        query = query.filter(ContentEntity.entity_id == entity_id)
    
    entities = query.all()
    print(f"Found {len(entities)} entities to process")
    
    results = {"success": 0, "failed": 0, "skipped": 0, "errors": []}
    
    for entity in entities:
        text = entity.to_embedding_text()
        
        if not text or len(text.strip()) < 10:
            print(f"[SKIP] {entity.entity_id} - insufficient text")
            results["skipped"] += 1
            continue
        
        if dry_run:
            print(f"[DRY RUN] {entity.entity_id}")
            print(f"  Text: {text[:100]}...")
            results["success"] += 1
        else:
            try:
                embedding = await embedding_service.generate_embedding(text)
                entity.embedding = embedding
                print(f"[OK] {entity.entity_id} - {len(embedding)} dimensions")
                results["success"] += 1
            except Exception as e:
                print(f"[ERROR] {entity.entity_id}: {e}")
                results["failed"] += 1
                results["errors"].append({"entity_id": entity.entity_id, "error": str(e)})
    
    if not dry_run:
        db.commit()
    
    db.close()
    
    print(f"\n=== RESULTS ===")
    print(f"Success: {results['success']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped: {results['skipped']}")
    
    if results["errors"]:
        print(f"\nErrors:")
        for err in results["errors"]:
            print(f"  - {err['entity_id']}: {err['error']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for content entities")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--execute", action="store_true", help="Actually generate embeddings")
    parser.add_argument("--entity-id", type=str, help="Process single entity")
    args = parser.parse_args()
    
    asyncio.run(generate_embeddings(
        dry_run=not args.execute,
        entity_id=args.entity_id
    ))
```

---

## STEP 12: Create Content Loading Script

Create `scripts/load_content.py`:

```python
#!/usr/bin/env python3
"""
Load content entities from JSON file into database.

Usage:
    python scripts/load_content.py content_entities.json --dry-run
    python scripts/load_content.py content_entities.json --execute
"""

import argparse
import json
import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from models.content_entity import ContentEntity


def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    return url


def load_content(json_file: str, dry_run: bool = True):
    # Load JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    entities = data if isinstance(data, list) else data.get('entities', [])
    print(f"Loaded {len(entities)} entities from {json_file}")
    
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    db = Session()
    
    results = {"created": 0, "updated": 0, "errors": []}
    
    for item in entities:
        entity_id = item.get('entity_id')
        if not entity_id:
            print(f"[SKIP] Missing entity_id: {item}")
            continue
        
        # Check if exists
        existing = db.query(ContentEntity).filter(
            ContentEntity.entity_id == entity_id
        ).first()
        
        if dry_run:
            action = "UPDATE" if existing else "CREATE"
            print(f"[DRY RUN] {action} {entity_id}")
        else:
            try:
                if existing:
                    # Update
                    for key, value in item.items():
                        # Skip fields that shouldn't be overwritten
                        if key in ['id', 'created_at', 'embedding', 'retrieval_count']:
                            continue
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    results["updated"] += 1
                    print(f"[UPDATE] {entity_id}")
                else:
                    # Create
                    entity = ContentEntity(**item)
                    db.add(entity)
                    results["created"] += 1
                    print(f"[CREATE] {entity_id}")
            except Exception as e:
                print(f"[ERROR] {entity_id}: {e}")
                results["errors"].append({"entity_id": entity_id, "error": str(e)})
    
    if not dry_run:
        db.commit()
    
    db.close()
    
    print(f"\n=== RESULTS ===")
    print(f"Created: {results['created']}")
    print(f"Updated: {results['updated']}")
    print(f"Errors: {len(results['errors'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load content entities from JSON")
    parser.add_argument("json_file", help="Path to JSON file")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    
    load_content(args.json_file, dry_run=not args.execute)
```

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `scripts/create_new_content_table.py` | CREATE |
| `scripts/generate_embeddings.py` | CREATE |
| `scripts/load_content.py` | CREATE |
| `src/models/content_entity.py` | REPLACE |
| `src/routers/content_entities.py` | UPDATE |
| `src/services/content_retrieval_service.py` | UPDATE field names |
| `src/services/embedding_service.py` | UPDATE |
| `src/services/prompt_prep_service.py` | UPDATE |
| `frontend/src/components/admin/ContentEntityEditor.tsx` | UPDATE |

---

## Execution Order

1. `python scripts/create_new_content_table.py --execute`
2. Update Python code (model, services, router)
3. `python scripts/load_content.py content.json --execute`
4. `python scripts/generate_embeddings.py --execute`
5. Test retrieval
6. Update frontend

---

## DO NOT

- Do NOT use Alembic migrations
- Do NOT delete the deprecated table (keep for reference/rollback)
- Do NOT migrate data automatically from old table
- Do NOT change test_bank table yet

---

## ALSO CHECK

These files/services may reference old field names and need updates:

- `src/services/testing_service.py` - may use old field names
- `src/services/prompt_assembly_service.py` - if exists
- Any other service that imports `ContentEntity`
- Frontend components that display content fields

Search codebase for: `situation_keywords`, `situation_phrases`, `content_summary`, `content_detailed`

---

## ROLLBACK PLAN

If something goes wrong:

```bash
python scripts/create_new_content_table.py --rollback --execute
```

This drops the new table and renames deprecated back to original.

---

## Testing Checklist

- [ ] Pre-flight checks pass
- [ ] Old table renamed to content_entities_deprecated
- [ ] New table created with all columns
- [ ] Indexes created
- [ ] Rollback script works
- [ ] SQLAlchemy model works
- [ ] API accepts new fields
- [ ] Content loads from JSON
- [ ] Embeddings generate successfully
- [ ] Retrieval uses new field names
- [ ] UI displays new form layout
- [ ] New entries pre-populate templates

---

*Ready for Claude Code implementation. Content JSON will be provided separately.*
