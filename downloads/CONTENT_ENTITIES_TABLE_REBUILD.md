# Content Entities Table Rebuild

## Overview

Drop the existing `content_entities` table and create a new one with a cleaner schema. Then import 76 entity records from CSV.

## Step 1: Drop Existing Table

```sql
DROP TABLE IF EXISTS content_entities CASCADE;
```

Also drop any related tables that reference it (check for foreign keys first).

## Step 2: Create Enums (if not exists)

```sql
CREATE TYPE entity_type_enum AS ENUM (
  'TOPIC',
  'RULE', 
  'HANDLER',
  'PERSONA',
  'CHAT_CONTEXT',
  'RERANKER'
);

CREATE TYPE editable_by_enum AS ENUM (
  'ADMIN',
  'TRAINER'
);

CREATE TYPE load_mode_enum AS ENUM (
  'ALWAYS',
  'STATE',
  'SITUATION'
);

CREATE TYPE severity_enum AS ENUM (
  'critical',
  'high',
  'medium',
  'low'
);
```

If enums already exist, skip or use `DROP TYPE IF EXISTS ... CASCADE` first.

## Step 3: Create New Table

```sql
CREATE TABLE content_entities (
  -- Section 1: What Is This
  title               VARCHAR(200) NOT NULL,
  entity_type         entity_type_enum NOT NULL,
  subtype             VARCHAR(50),
  what_this_is        TEXT NOT NULL,
  
  -- Section 2: Recognition (for matching)
  user_says           TEXT,                          -- semicolon-separated phrases
  keywords            TEXT,                          -- comma-separated words
  
  -- Section 3: Frank's Response
  frank_says          TEXT,
  do_this             TEXT,                          -- semicolon-separated list
  never_do            TEXT,                          -- semicolon-separated list
  sample_dialog       TEXT,
  
  -- Section 4: Warning/Routing
  watch_for           TEXT,                          -- semicolon-separated list
  escalate_if         TEXT,
  handler             VARCHAR(50),                   -- e.g., 'crisis' or NULL
  severity            severity_enum,
  
  -- Section 5: Targeting
  audience_types      JSONB NOT NULL DEFAULT '["PARENT"]',
  chat_types          JSONB NOT NULL DEFAULT '[]',
  load_mode           load_mode_enum NOT NULL DEFAULT 'SITUATION',
  state_conditions    JSONB,                         -- only used when load_mode = 'STATE'
  
  -- Section 6: Admin
  priority            INT NOT NULL DEFAULT 50,
  attribution         VARCHAR(500),
  editable_by         editable_by_enum NOT NULL DEFAULT 'TRAINER',
  is_active           BOOLEAN NOT NULL DEFAULT true,
  
  -- Section 7: System (auto-generated)
  entity_id           VARCHAR(100) PRIMARY KEY,
  slug                VARCHAR(100) UNIQUE NOT NULL,
  embedding           VECTOR(1024),                  -- generated after insert
  token_count         INT,
  created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Step 4: Create Indexes

```sql
-- Primary lookups
CREATE INDEX idx_content_entities_type ON content_entities(entity_type);
CREATE INDEX idx_content_entities_subtype ON content_entities(subtype);
CREATE INDEX idx_content_entities_load_mode ON content_entities(load_mode);
CREATE INDEX idx_content_entities_active ON content_entities(is_active);

-- Audience/chat filtering (JSONB)
CREATE INDEX idx_content_entities_audience ON content_entities USING GIN(audience_types);
CREATE INDEX idx_content_entities_chat ON content_entities USING GIN(chat_types);

-- Vector similarity search
CREATE INDEX idx_content_entities_embedding ON content_entities USING ivfflat(embedding vector_cosine_ops);
```

## Step 5: Import CSV Data

The CSV file is located in the user's **Downloads folder**:
- Filename: `content_entities_insert_ready.csv`
- Records: 76
- Columns: 25 (matches table, excludes embedding, created_at, updated_at)

### Column Mapping

CSV columns are in this order:
1. title
2. entity_type
3. subtype
4. what_this_is
5. user_says
6. keywords
7. frank_says
8. do_this
9. never_do
10. sample_dialog
11. watch_for
12. escalate_if
13. handler
14. severity
15. audience_types
16. chat_types
17. load_mode
18. state_conditions
19. priority
20. attribution
21. editable_by
22. is_active
23. entity_id
24. slug
25. token_count

### Import Options

**Option A: Python script**
```python
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('~/Downloads/content_entities_insert_ready.csv')
engine = create_engine('postgresql://...')
df.to_sql('content_entities', engine, if_exists='append', index=False)
```

**Option B: psql COPY**
```sql
\COPY content_entities (
  title, entity_type, subtype, what_this_is,
  user_says, keywords,
  frank_says, do_this, never_do, sample_dialog,
  watch_for, escalate_if, handler, severity,
  audience_types, chat_types, load_mode, state_conditions,
  priority, attribution, editable_by, is_active,
  entity_id, slug, token_count
)
FROM '~/Downloads/content_entities_insert_ready.csv'
WITH (FORMAT csv, HEADER true, QUOTE '"');
```

## Step 6: Generate Embeddings

After import, generate embeddings for each entity using Voyage:

```python
# For each entity where embedding IS NULL:
# 1. Concatenate: user_says + " " + what_this_is
# 2. Call Voyage API to get embedding
# 3. UPDATE content_entities SET embedding = ... WHERE entity_id = ...
```

## Step 7: Verify

```sql
-- Check counts by type
SELECT entity_type, COUNT(*) 
FROM content_entities 
GROUP BY entity_type 
ORDER BY COUNT(*) DESC;

-- Expected:
-- TOPIC: 33
-- RULE: 20
-- CHAT_CONTEXT: 9
-- HANDLER: 7
-- PERSONA: 5
-- RERANKER: 2

-- Check for missing required fields
SELECT entity_id, entity_type 
FROM content_entities 
WHERE what_this_is IS NULL OR LENGTH(what_this_is) < 150;
-- Should return 0 rows
```

## Important Notes

1. **audience_types is always a filter** - even ALWAYS load_mode requires audience match
2. **load_mode logic:**
   - ALWAYS = load when audience matches
   - STATE = load when audience matches AND state_conditions met
   - SITUATION = load when audience matches AND user message matches (via embedding/keywords)
3. **Embeddings** must be generated after import - the CSV doesn't include them
4. **List fields** (do_this, never_do, watch_for) are semicolon-separated in the CSV - convert to arrays if needed for your application
