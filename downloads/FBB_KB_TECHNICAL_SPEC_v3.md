# FBB Knowledge Base Technical Specification v3

**Purpose:** Complete implementation spec for Claude Code  
**Companion docs:** FBB_CONTENT_v3_PART1.md, FBB_CONTENT_v3_PART2.md

---

## 1. Database Schema

### Table: `kb_content_entities`

```sql
CREATE TABLE kb_content_entities (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR(100) NOT NULL UNIQUE,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('PERSONA', 'GUARDRAIL', 'HANDLER', 'KNOWLEDGE', 'SCRIPT', 'RULE')),
    subtype VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    
    -- Content Fields (all TEXT, all available for all entity types)
    concept_summary TEXT,
    recognition TEXT,
    keywords TEXT,
    guidance_do TEXT,
    guidance_dont TEXT,
    examples TEXT,
    red_flags TEXT,
    
    -- Configuration
    load_mode VARCHAR(20) NOT NULL DEFAULT 'SITUATION' CHECK (load_mode IN ('ALWAYS', 'STATE', 'SITUATION')),
    priority INTEGER NOT NULL DEFAULT 50 CHECK (priority BETWEEN 0 AND 100),
    state_conditions JSONB,
    audience_types TEXT[] DEFAULT ARRAY['PARENT'],
    
    -- Vector (Voyage AI, 1024 dimensions)
    embedding vector(1024),
    
    -- Attribution
    source_author VARCHAR(255),
    source_title VARCHAR(255),
    source_year INTEGER,
    
    -- Admin
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    editable_by VARCHAR(20) DEFAULT 'ADMIN' CHECK (editable_by IN ('ADMIN', 'TRAINER', 'HIDDEN')),
    retrieval_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    previous_version_id UUID REFERENCES kb_content_entities(id)
);

-- Indexes
CREATE INDEX idx_kb_entity_type ON kb_content_entities(entity_type);
CREATE INDEX idx_kb_load_mode ON kb_content_entities(load_mode);
CREATE INDEX idx_kb_is_active ON kb_content_entities(is_active);
CREATE INDEX idx_kb_priority ON kb_content_entities(priority DESC);
CREATE INDEX idx_kb_audience ON kb_content_entities USING GIN(audience_types);
```

### Versioning Strategy

```sql
-- When updating an entity:
-- 1. Copy current row with new UUID
-- 2. Set previous_version_id to old row's ID
-- 3. Increment version
-- 4. Mark old row is_active = FALSE

CREATE OR REPLACE FUNCTION version_kb_entity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.id = NEW.id THEN
        -- Insert old version as history
        INSERT INTO kb_content_entities 
        SELECT OLD.* WITH id = gen_random_uuid(), is_active = FALSE;
        
        -- Update new version
        NEW.version = OLD.version + 1;
        NEW.previous_version_id = OLD.id;
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER kb_entity_version_trigger
BEFORE UPDATE ON kb_content_entities
FOR EACH ROW EXECUTE FUNCTION version_kb_entity();
```

---

## 2. Vector Storage

### Provider: pgvector (PostgreSQL extension)

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Vector index for similarity search
CREATE INDEX idx_kb_embedding ON kb_content_entities 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Note: For <1000 rows, ivfflat with lists=100 is fine
-- For larger scale, consider HNSW index:
-- CREATE INDEX idx_kb_embedding_hnsw ON kb_content_entities 
-- USING hnsw (embedding vector_cosine_ops);
```

### Voyage AI Configuration

```python
# config/embedding.py

VOYAGE_CONFIG = {
    "model": "voyage-2",  # or voyage-large-2 for higher quality
    "dimensions": 1024,
    "max_tokens": 4000,  # per embedding request
    "batch_size": 128,   # max items per API call
}
```

### Embedding Generation

```python
# services/embedding_service.py

import voyageai
from typing import List

class EmbeddingService:
    def __init__(self):
        self.client = voyageai.Client()
        self.model = "voyage-2"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate single embedding."""
        result = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="document"
        )
        return result.embeddings[0]
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch."""
        result = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="document"
        )
        return result.embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        result = self.client.embed(
            texts=[query],
            model=self.model,
            input_type="query"  # Different from document!
        )
        return result.embeddings[0]
```

---

## 3. Retrieval Logic

### Retrieval Service

```python
# services/retrieval_service.py

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RetrievalConfig:
    top_k: int = 5
    score_threshold: float = 0.65
    priority_weight: float = 0.15  # How much priority affects final score
    max_tokens_budget: int = 3000  # Max tokens for retrieved content

@dataclass
class RetrievedEntity:
    entity_id: str
    entity_type: str
    title: str
    similarity_score: float
    priority: int
    final_score: float
    content: Dict  # All fields for prompt injection

class RetrievalService:
    def __init__(self, db, embedding_service, config: RetrievalConfig = None):
        self.db = db
        self.embedding_service = embedding_service
        self.config = config or RetrievalConfig()
    
    def retrieve(
        self,
        user_message: str,
        user_state: Dict,
        audience_type: str = "PARENT"
    ) -> List[RetrievedEntity]:
        """
        Full retrieval pipeline:
        1. Load ALWAYS entities
        2. Evaluate STATE conditions
        3. Semantic search for SITUATION entities
        4. Blend and rank results
        5. Apply token budget
        """
        results = []
        
        # 1. ALWAYS entities (no matching needed)
        always_entities = self._load_always_entities(audience_type)
        results.extend(always_entities)
        
        # 2. STATE entities (condition matching)
        state_entities = self._evaluate_state_conditions(user_state, audience_type)
        results.extend(state_entities)
        
        # 3. SITUATION entities (semantic search)
        situation_entities = self._semantic_search(user_message, audience_type)
        results.extend(situation_entities)
        
        # 4. Deduplicate and rank
        results = self._deduplicate_and_rank(results)
        
        # 5. Apply token budget
        results = self._apply_token_budget(results)
        
        return results
    
    def _load_always_entities(self, audience_type: str) -> List[RetrievedEntity]:
        """Load all ALWAYS entities."""
        query = """
            SELECT * FROM kb_content_entities
            WHERE load_mode = 'ALWAYS'
            AND is_active = TRUE
            AND %s = ANY(audience_types)
            ORDER BY priority DESC
        """
        rows = self.db.execute(query, [audience_type])
        return [self._row_to_entity(row, similarity=1.0) for row in rows]
    
    def _evaluate_state_conditions(
        self, 
        user_state: Dict, 
        audience_type: str
    ) -> List[RetrievedEntity]:
        """Evaluate STATE entity conditions against current user state."""
        query = """
            SELECT * FROM kb_content_entities
            WHERE load_mode = 'STATE'
            AND is_active = TRUE
            AND %s = ANY(audience_types)
            AND state_conditions IS NOT NULL
        """
        rows = self.db.execute(query, [audience_type])
        
        results = []
        for row in rows:
            if self._matches_state(row['state_conditions'], user_state):
                results.append(self._row_to_entity(row, similarity=1.0))
        
        return results
    
    def _matches_state(self, conditions: Dict, user_state: Dict) -> bool:
        """
        Evaluate state conditions.
        
        Supports:
        - Exact match: {"user_type": "clinician"}
        - List membership: {"interaction_rating": [1, 2]}
        - Comparison: {"days_since_last": {"$gte": 7}}
        - Zero check: {"conversation_count": 0}
        """
        for key, expected in conditions.items():
            actual = user_state.get(key)
            
            if isinstance(expected, dict):
                # Comparison operators
                for op, val in expected.items():
                    if op == "$gte" and not (actual >= val):
                        return False
                    elif op == "$lte" and not (actual <= val):
                        return False
                    elif op == "$gt" and not (actual > val):
                        return False
                    elif op == "$lt" and not (actual < val):
                        return False
                    elif op == "$eq" and not (actual == val):
                        return False
            elif isinstance(expected, list):
                # List membership
                if actual not in expected:
                    return False
            else:
                # Exact match
                if actual != expected:
                    return False
        
        return True
    
    def _semantic_search(
        self, 
        user_message: str, 
        audience_type: str
    ) -> List[RetrievedEntity]:
        """Semantic similarity search for SITUATION entities."""
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_query_embedding(user_message)
        
        # Vector similarity search
        query = """
            SELECT 
                *,
                1 - (embedding <=> %s::vector) as similarity
            FROM kb_content_entities
            WHERE load_mode = 'SITUATION'
            AND is_active = TRUE
            AND %s = ANY(audience_types)
            AND embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        rows = self.db.execute(query, [
            query_embedding, 
            audience_type, 
            query_embedding,
            self.config.top_k * 2  # Fetch extra for threshold filtering
        ])
        
        results = []
        for row in rows:
            if row['similarity'] >= self.config.score_threshold:
                results.append(self._row_to_entity(row, row['similarity']))
        
        return results[:self.config.top_k]
    
    def _row_to_entity(self, row: Dict, similarity: float) -> RetrievedEntity:
        """Convert DB row to RetrievedEntity."""
        # Calculate final score: similarity + priority bonus
        priority_bonus = (row['priority'] / 100) * self.config.priority_weight
        final_score = similarity + priority_bonus
        
        return RetrievedEntity(
            entity_id=row['entity_id'],
            entity_type=row['entity_type'],
            title=row['title'],
            similarity_score=similarity,
            priority=row['priority'],
            final_score=final_score,
            content={
                'concept_summary': row['concept_summary'],
                'guidance_do': row['guidance_do'],
                'guidance_dont': row['guidance_dont'],
                'examples': row['examples'],
                'red_flags': row['red_flags'],
            }
        )
    
    def _deduplicate_and_rank(
        self, 
        entities: List[RetrievedEntity]
    ) -> List[RetrievedEntity]:
        """Remove duplicates and sort by final score."""
        seen = set()
        unique = []
        for e in entities:
            if e.entity_id not in seen:
                seen.add(e.entity_id)
                unique.append(e)
        
        return sorted(unique, key=lambda x: x.final_score, reverse=True)
    
    def _apply_token_budget(
        self, 
        entities: List[RetrievedEntity]
    ) -> List[RetrievedEntity]:
        """Trim results to fit token budget."""
        # Rough estimate: 1 token ≈ 4 characters
        total_tokens = 0
        result = []
        
        for entity in entities:
            content_text = " ".join(
                str(v) for v in entity.content.values() if v
            )
            entity_tokens = len(content_text) // 4
            
            if total_tokens + entity_tokens <= self.config.max_tokens_budget:
                result.append(entity)
                total_tokens += entity_tokens
            else:
                break
        
        return result
```

---

## 4. Admin UI

### API Endpoints

```python
# api/admin/kb_routes.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

router = APIRouter(prefix="/admin/kb", tags=["Knowledge Base Admin"])

@router.get("/entities")
async def list_entities(
    entity_type: Optional[str] = None,
    load_mode: Optional[str] = None,
    is_active: bool = True,
    page: int = 1,
    page_size: int = 20
):
    """List all KB entities with filtering."""
    pass

@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get single entity by entity_id."""
    pass

@router.post("/entities")
async def create_entity(entity: KBEntityCreate):
    """Create new entity."""
    pass

@router.put("/entities/{entity_id}")
async def update_entity(entity_id: str, entity: KBEntityUpdate):
    """Update entity (creates new version)."""
    pass

@router.delete("/entities/{entity_id}")
async def deactivate_entity(entity_id: str):
    """Soft delete (set is_active=FALSE)."""
    pass

@router.get("/entities/{entity_id}/versions")
async def get_entity_versions(entity_id: str):
    """Get version history for entity."""
    pass

@router.post("/entities/{entity_id}/regenerate-embedding")
async def regenerate_embedding(entity_id: str):
    """Regenerate embedding for single entity."""
    pass

@router.post("/regenerate-all-embeddings")
async def regenerate_all_embeddings():
    """Regenerate embeddings for all active entities."""
    pass

@router.get("/retrieval-test")
async def test_retrieval(
    query: str,
    audience_type: str = "PARENT",
    top_k: int = 5
):
    """Test retrieval with a sample query."""
    pass

@router.get("/stats")
async def get_stats():
    """Get KB statistics (counts by type, retrieval stats, etc.)."""
    pass
```

### Admin UI Pages (React)

```
/admin/kb/
├── EntityList.tsx        # Table view with filters
├── EntityDetail.tsx      # View/edit single entity
├── EntityCreate.tsx      # Create new entity
├── VersionHistory.tsx    # View version history
├── RetrievalTest.tsx     # Test queries against KB
├── BulkOperations.tsx    # Import/export, bulk regenerate
└── Stats.tsx             # Dashboard with metrics
```

### Pydantic Models

```python
# models/kb_admin.py

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class EntityType(str, Enum):
    PERSONA = "PERSONA"
    GUARDRAIL = "GUARDRAIL"
    HANDLER = "HANDLER"
    KNOWLEDGE = "KNOWLEDGE"
    SCRIPT = "SCRIPT"
    RULE = "RULE"

class LoadMode(str, Enum):
    ALWAYS = "ALWAYS"
    STATE = "STATE"
    SITUATION = "SITUATION"

class KBEntityCreate(BaseModel):
    entity_id: str
    entity_type: EntityType
    title: str
    subtype: Optional[str] = None
    concept_summary: Optional[str] = None
    recognition: Optional[str] = None
    keywords: Optional[str] = None
    guidance_do: Optional[str] = None
    guidance_dont: Optional[str] = None
    examples: Optional[str] = None
    red_flags: Optional[str] = None
    load_mode: LoadMode = LoadMode.SITUATION
    priority: int = 50
    state_conditions: Optional[dict] = None
    audience_types: List[str] = ["PARENT"]
    source_author: Optional[str] = None
    source_title: Optional[str] = None
    source_year: Optional[int] = None

class KBEntityUpdate(BaseModel):
    title: Optional[str] = None
    concept_summary: Optional[str] = None
    recognition: Optional[str] = None
    keywords: Optional[str] = None
    guidance_do: Optional[str] = None
    guidance_dont: Optional[str] = None
    examples: Optional[str] = None
    red_flags: Optional[str] = None
    load_mode: Optional[LoadMode] = None
    priority: Optional[int] = None
    state_conditions: Optional[dict] = None
    audience_types: Optional[List[str]] = None
    is_active: Optional[bool] = None

class KBEntityResponse(BaseModel):
    id: str
    entity_id: str
    entity_type: EntityType
    title: str
    # ... all fields
    version: int
    created_at: str
    updated_at: str
```

---

## 5. State Management

### User State Schema

```python
# models/user_state.py

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class UserState:
    # Identity
    user_id: str
    user_type: str = "PARENT"  # PARENT or CLINICIAN
    
    # Session
    conversation_count: int = 0
    days_since_last: int = 0
    session_type: Optional[str] = None  # "debrief", "general", etc.
    
    # Interaction tracking
    interaction_rating: Optional[int] = None  # 1-5
    just_logged: bool = False
    
    # History
    skills_practiced: List[str] = field(default_factory=list)
    last_topics: List[str] = field(default_factory=list)
    
    # Timestamps
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

class StateService:
    def __init__(self, db):
        self.db = db
    
    def get_user_state(self, user_id: str) -> UserState:
        """Load or create user state."""
        row = self.db.execute(
            "SELECT * FROM user_state WHERE user_id = %s",
            [user_id]
        )
        
        if row:
            return self._row_to_state(row)
        else:
            return UserState(user_id=user_id)
    
    def update_state(self, user_id: str, updates: dict) -> UserState:
        """Update user state fields."""
        pass
    
    def record_interaction(
        self, 
        user_id: str, 
        rating: Optional[int] = None,
        topics: List[str] = None,
        skills_used: List[str] = None
    ):
        """Record interaction and update state."""
        pass
```

### State Storage Table

```sql
CREATE TABLE user_state (
    user_id VARCHAR(100) PRIMARY KEY,
    user_type VARCHAR(20) DEFAULT 'PARENT',
    conversation_count INTEGER DEFAULT 0,
    session_type VARCHAR(50),
    interaction_rating INTEGER,
    just_logged BOOLEAN DEFAULT FALSE,
    skills_practiced TEXT[],
    last_topics TEXT[],
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,
    state_data JSONB,  -- Flexible additional state
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### State Evaluation in Retrieval

```python
def evaluate_handlers_for_state(user_state: UserState) -> List[str]:
    """Determine which handlers should activate based on state."""
    
    handlers = []
    
    # First conversation
    if user_state.conversation_count == 0:
        handlers.append("handler_first_conversation")
    
    # Returning user
    if user_state.days_since_last >= 7:
        handlers.append("handler_returning_user")
    
    # Post-escalation
    if user_state.just_logged and user_state.interaction_rating in [1, 2]:
        handlers.append("handler_post_escalation")
    
    # Celebrating wins
    if user_state.interaction_rating in [4, 5]:
        handlers.append("handler_celebrating_wins")
    
    # Clinician mode
    if user_state.user_type == "CLINICIAN":
        handlers.append("handler_clinician_mode")
    
    # Debrief session
    if user_state.session_type == "debrief":
        handlers.append("handler_interaction_debrief")
    
    return handlers
```

---

## 6. Token Budget Management

### Configuration

```python
# config/token_budget.py

TOKEN_BUDGET = {
    # Total context window (Claude)
    "max_context": 100000,
    
    # Reserved allocations
    "system_prompt_base": 2000,      # Base system prompt
    "always_entities": 3000,          # ALWAYS loaded content
    "state_handlers": 1500,           # STATE triggered content
    "retrieved_knowledge": 3000,      # SITUATION retrieved content
    "conversation_history": 8000,     # Recent messages
    "user_message": 2000,             # Current message
    "response_buffer": 4000,          # Space for response
    
    # Safety margin
    "safety_margin": 1000,
}

def calculate_available_tokens(
    system_base: int,
    always_content: int,
    history_tokens: int,
    user_message_tokens: int
) -> int:
    """Calculate remaining tokens for retrieval."""
    used = (
        system_base + 
        always_content + 
        history_tokens + 
        user_message_tokens +
        TOKEN_BUDGET["response_buffer"] +
        TOKEN_BUDGET["safety_margin"]
    )
    return TOKEN_BUDGET["max_context"] - used
```

### Token Counting

```python
# utils/token_counter.py

import tiktoken

class TokenCounter:
    def __init__(self, model: str = "cl100k_base"):
        self.encoder = tiktoken.get_encoding(model)
    
    def count(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def count_entity(self, entity: RetrievedEntity) -> int:
        """Count tokens for entity's prompt content."""
        content_text = self._entity_to_prompt_text(entity)
        return self.count(content_text)
    
    def _entity_to_prompt_text(self, entity: RetrievedEntity) -> str:
        """Format entity for prompt injection."""
        sections = [f"## {entity.title}"]
        
        if entity.content.get('concept_summary'):
            sections.append(entity.content['concept_summary'])
        if entity.content.get('guidance_do'):
            sections.append(f"\n**Guidance:**\n{entity.content['guidance_do']}")
        if entity.content.get('guidance_dont'):
            sections.append(f"\n**Avoid:**\n{entity.content['guidance_dont']}")
        if entity.content.get('examples'):
            sections.append(f"\n**Examples:**\n{entity.content['examples']}")
        if entity.content.get('red_flags'):
            sections.append(f"\n**Red Flags:**\n{entity.content['red_flags']}")
        
        return "\n".join(sections)
```

### Budget-Aware Retrieval

```python
def retrieve_within_budget(
    self,
    user_message: str,
    user_state: Dict,
    available_tokens: int
) -> List[RetrievedEntity]:
    """Retrieve entities respecting token budget."""
    
    # Get all candidates
    candidates = self.retrieve(user_message, user_state)
    
    # Fit to budget
    result = []
    tokens_used = 0
    
    for entity in candidates:
        entity_tokens = self.token_counter.count_entity(entity)
        
        if tokens_used + entity_tokens <= available_tokens:
            result.append(entity)
            tokens_used += entity_tokens
        elif entity.entity_type in ['GUARDRAIL', 'HANDLER']:
            # Critical entities get priority - bump last KNOWLEDGE entity
            if result and result[-1].entity_type == 'KNOWLEDGE':
                tokens_used -= self.token_counter.count_entity(result[-1])
                result.pop()
                result.append(entity)
                tokens_used += entity_tokens
    
    return result
```

---

## 7. Migration Plan

### Phase 1: Parallel Tables (Week 1)

```sql
-- Create new table alongside old
-- Old: kb_content (deprecated)
-- New: kb_content_entities

-- No data migration yet - new table starts empty
```

### Phase 2: Content Load (Week 1)

```python
# scripts/load_content_v3.py

import json
from services.kb_service import KBService
from services.embedding_service import EmbeddingService

def load_content_from_json(filepath: str):
    """Load content from JSON export of v3 markdown docs."""
    
    with open(filepath) as f:
        entities = json.load(f)
    
    kb_service = KBService()
    embedding_service = EmbeddingService()
    
    for entity_data in entities:
        # Create entity
        entity = kb_service.create_entity(entity_data)
        
        # Generate embedding
        embedding_text = entity.to_embedding_text()
        embedding = embedding_service.generate_embedding(embedding_text)
        
        # Store embedding
        kb_service.update_embedding(entity.entity_id, embedding)
        
        print(f"Loaded: {entity.entity_id}")
```

### Phase 3: Dual-Read Testing (Week 2)

```python
# During testing, read from both systems and compare

class DualRetrievalService:
    def __init__(self, old_service, new_service):
        self.old = old_service
        self.new = new_service
    
    def retrieve_and_compare(self, query: str, user_state: Dict):
        old_results = self.old.retrieve(query, user_state)
        new_results = self.new.retrieve(query, user_state)
        
        # Log differences
        self._log_comparison(query, old_results, new_results)
        
        # Return new results (shadow mode)
        return new_results
```

### Phase 4: Cutover (Week 3)

```python
# config/feature_flags.py

FEATURE_FLAGS = {
    "use_new_kb_system": True,  # Flip when ready
    "log_retrieval_comparison": False,  # Disable after validation
}
```

### Phase 5: Cleanup (Week 4)

```sql
-- After successful cutover
-- Rename tables
ALTER TABLE kb_content RENAME TO kb_content_deprecated;
ALTER TABLE kb_content_entities RENAME TO kb_content;

-- Keep deprecated table for 30 days, then drop
```

---

## 8. Testing Strategy

### Retrieval Quality Tests

```python
# tests/test_retrieval_quality.py

import pytest

# Test cases: user message -> expected entity matches
RETRIEVAL_TEST_CASES = [
    # BIFF
    {
        "message": "she sent me another nasty email what do i say",
        "expected": ["biff_response"],
        "should_not_match": ["gray_rock"]
    },
    {
        "message": "got a 10 page text full of accusations",
        "expected": ["biff_response"],
    },
    
    # Gray rock
    {
        "message": "he keeps baiting me trying to get a reaction",
        "expected": ["gray_rock"],
    },
    {
        "message": "she wants me to blow up so she can record it",
        "expected": ["gray_rock"],
    },
    
    # Boundary setting
    {
        "message": "she shows up whenever she wants no respect for my time",
        "expected": ["boundary_setting"],
    },
    
    # De-escalation
    {
        "message": "im about to lose it things are getting heated",
        "expected": ["de_escalation"],
    },
    
    # Loyalty binds
    {
        "message": "my kid apologizes for having fun at my house",
        "expected": ["loyalty_binds"],
    },
    
    # Alienation
    {
        "message": "my daughter says im a narcissistic abuser shes 9",
        "expected": ["parental_alienation"],
        "should_not_match": ["domestic_violence"]
    },
    
    # Crisis
    {
        "message": "i dont want to be here anymore whats the point",
        "expected": ["handler_crisis", "rule_crisis_detection"],
    },
    
    # Ambiguous - should get loyalty_binds not alienation
    {
        "message": "my kid feels guilty spending time with me",
        "expected": ["loyalty_binds"],
        "should_not_match": ["parental_alienation"]
    },
]

@pytest.mark.parametrize("test_case", RETRIEVAL_TEST_CASES)
def test_retrieval_accuracy(retrieval_service, test_case):
    results = retrieval_service.retrieve(
        test_case["message"],
        user_state={},
        audience_type="PARENT"
    )
    
    result_ids = [r.entity_id for r in results]
    
    # Check expected matches are in top results
    for expected in test_case["expected"]:
        assert expected in result_ids[:3], \
            f"Expected {expected} in top 3 for: {test_case['message']}"
    
    # Check exclusions
    for excluded in test_case.get("should_not_match", []):
        assert excluded not in result_ids[:3], \
            f"Should not match {excluded} for: {test_case['message']}"
```

### State Condition Tests

```python
# tests/test_state_conditions.py

def test_first_conversation_handler():
    state = {"conversation_count": 0}
    handlers = evaluate_handlers_for_state(state)
    assert "handler_first_conversation" in handlers

def test_returning_user_handler():
    state = {"days_since_last": 10}
    handlers = evaluate_handlers_for_state(state)
    assert "handler_returning_user" in handlers

def test_post_escalation_handler():
    state = {"interaction_rating": 2, "just_logged": True}
    handlers = evaluate_handlers_for_state(state)
    assert "handler_post_escalation" in handlers

def test_clinician_mode():
    state = {"user_type": "CLINICIAN"}
    handlers = evaluate_handlers_for_state(state)
    assert "handler_clinician_mode" in handlers
```

### Embedding Quality Tests

```python
# tests/test_embedding_quality.py

def test_embedding_dimensions():
    """Verify embeddings are correct dimension."""
    entity = kb_service.get_entity("biff_response")
    assert len(entity.embedding) == 1024

def test_embedding_text_content():
    """Verify embedding text includes correct fields."""
    entity = kb_service.get_entity("biff_response")
    embedding_text = entity.to_embedding_text()
    
    # Should include
    assert entity.title in embedding_text
    assert "nasty email" in embedding_text  # from recognition
    assert "Parent:" in embedding_text  # from examples
    
    # Should NOT include
    assert "BIFF is a framework" not in embedding_text  # concept_summary excluded

def test_similar_concepts_distinguishable():
    """Verify similar concepts have distinguishable embeddings."""
    alienation = kb_service.get_entity("parental_alienation")
    loyalty = kb_service.get_entity("loyalty_binds")
    
    similarity = cosine_similarity(alienation.embedding, loyalty.embedding)
    
    # Should be related but distinguishable
    assert 0.5 < similarity < 0.85, \
        f"Alienation and loyalty_binds too similar: {similarity}"
```

### Integration Tests

```python
# tests/test_full_pipeline.py

def test_full_retrieval_pipeline():
    """Test complete retrieval flow."""
    
    # New user first message
    user_state = UserState(user_id="test", conversation_count=0)
    message = "hi im new here"
    
    results = retrieval_service.retrieve(message, user_state)
    
    # Should get: ALWAYS entities + first_conversation handler
    entity_ids = [r.entity_id for r in results]
    
    assert "frank_parent_persona" in entity_ids  # ALWAYS
    assert "core_behavioral_guardrails" in entity_ids  # ALWAYS
    assert "handler_first_conversation" in entity_ids  # STATE

def test_crisis_detection_priority():
    """Crisis content should always surface."""
    
    message = "i just cant do this anymore i want to end it"
    results = retrieval_service.retrieve(message, {})
    
    # Crisis should be top result
    assert results[0].entity_id in ["handler_crisis", "rule_crisis_detection"]
```

---

## Summary

| Area | Status |
|------|--------|
| 1. DB Schema | ✓ Table + versioning |
| 2. Vector Storage | ✓ pgvector + Voyage config |
| 3. Retrieval Logic | ✓ Full service with ALWAYS/STATE/SITUATION |
| 4. Admin UI | ✓ API routes + React pages spec |
| 5. State Management | ✓ State table + evaluation logic |
| 6. Token Budget | ✓ Config + budget-aware retrieval |
| 7. Migration | ✓ 5-phase plan |
| 8. Testing | ✓ 20+ test cases + quality validation |

---

## Files for Claude Code

1. `FBB_CONTENT_v3_PART1.md` - KNOWLEDGE entities
2. `FBB_CONTENT_v3_PART2.md` - GUARDRAIL/HANDLER/PERSONA/SCRIPT/RULE entities
3. `FBB_KB_TECHNICAL_SPEC_v3.md` - This document

Claude Code should implement in this order:
1. Database schema (Step 1)
2. Models (Step 2)
3. Embedding service (Step 3)
4. Retrieval service (Step 4)
5. State service (Step 5)
6. Admin API (Step 6)
7. Load content (Step 7)
8. Run tests (Step 8)
