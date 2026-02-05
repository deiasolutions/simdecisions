# Content Entities Table Rebuild

## Summary of Changes

| Current | New |
|---------|-----|
| JSONB content blob | Flat columns |
| KNOWLEDGE type | TOPIC |
| GUARDRAIL type | RULE with subtype=guardrail |
| 53 entities | 76 entities (deduplicated + enriched) |

## Answers to Your Questions

**Q2: GUARDRAIL → RULE?**
Yes. GUARDRAIL is now `entity_type=RULE` with `subtype` field:
- RULE/guardrail - behavioral guardrails
- RULE/safety - crisis detection  
- RULE/threat - harassment, legal threats
- RULE/routing - complexity routing
- RULE/system - PII detection

**Q3: List field storage?**
JSONB arrays, not semicolons. The `do_this`, `never_do`, `watch_for` columns are JSONB arrays like `["item1", "item2"]`. 

Text fields that stay as plain text:
- `user_says` - semicolon-separated (for embedding generation)
- `keywords` - comma-separated (for keyword boost)

**Q4: Frontend form editor?**
Yes, rebuild. Flat schema is easier. Show/hide fields based on entity_type using the visibility rules below.

**Q5: Migration or clean break?**
Clean break. Drop old table, create new, import 76 pre-curated entities from CSV.

**Q6: Backend services?**
Yes, refactor needed. Simpler than before - flat column access instead of JSONB parsing.

**Q7: Timeline?**
Before parent beta. Do it now.

---

## Step 1: Drop Existing Table

```sql
DROP TABLE IF EXISTS content_entities CASCADE;
```

## Step 2: Create Enums (if not exist)

```sql
DO $$ BEGIN
  CREATE TYPE entity_type_enum AS ENUM ('TOPIC', 'RULE', 'HANDLER', 'PERSONA', 'CHAT_CONTEXT', 'RERANKER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE editable_by_enum AS ENUM ('ADMIN', 'TRAINER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE load_mode_enum AS ENUM ('ALWAYS', 'STATE', 'SITUATION');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE severity_enum AS ENUM ('critical', 'high', 'medium', 'low');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
```

## Step 3: Create New Table

```sql
CREATE TABLE content_entities (
  -- What Is This
  title               VARCHAR(200) NOT NULL,
  entity_type         entity_type_enum NOT NULL,
  subtype             VARCHAR(50),
  what_this_is        TEXT NOT NULL,
  
  -- Recognition (for matching)
  user_says           TEXT,                          -- semicolon-separated, used for embedding
  keywords            TEXT,                          -- comma-separated, used for keyword boost
  
  -- Frank's Response
  frank_says          TEXT,
  do_this             JSONB DEFAULT '[]',            -- array of strings
  never_do            JSONB DEFAULT '[]',            -- array of strings
  sample_dialog       TEXT,
  
  -- Warning/Routing
  watch_for           JSONB DEFAULT '[]',            -- array of strings
  escalate_if         TEXT,
  handler             VARCHAR(50),
  severity            severity_enum,
  
  -- Targeting
  audience_types      JSONB NOT NULL DEFAULT '["PARENT"]',
  chat_types          JSONB NOT NULL DEFAULT '[]',
  load_mode           load_mode_enum NOT NULL DEFAULT 'SITUATION',
  state_conditions    JSONB,
  
  -- Admin
  priority            INT NOT NULL DEFAULT 50,
  attribution         VARCHAR(500),
  editable_by         editable_by_enum NOT NULL DEFAULT 'TRAINER',
  is_active           BOOLEAN NOT NULL DEFAULT true,
  
  -- System
  entity_id           VARCHAR(100) PRIMARY KEY,
  slug                VARCHAR(100) UNIQUE NOT NULL,
  embedding           VECTOR(1024),
  token_count         INT,
  created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Step 4: Create Indexes

```sql
CREATE INDEX idx_ce_type ON content_entities(entity_type);
CREATE INDEX idx_ce_subtype ON content_entities(subtype);
CREATE INDEX idx_ce_load_mode ON content_entities(load_mode);
CREATE INDEX idx_ce_active ON content_entities(is_active);
CREATE INDEX idx_ce_audience ON content_entities USING GIN(audience_types);
CREATE INDEX idx_ce_chat ON content_entities USING GIN(chat_types);
CREATE INDEX idx_ce_embedding ON content_entities USING ivfflat(embedding vector_cosine_ops);
```

## Step 5: Import CSV

File: `~/Downloads/content_entities_insert_ready.csv`
Records: 76

CSV columns match table columns exactly in this order:
1. title
2. entity_type
3. subtype
4. what_this_is
5. user_says
6. keywords
7. frank_says
8. do_this (JSONB array)
9. never_do (JSONB array)
10. sample_dialog
11. watch_for (JSONB array)
12. escalate_if
13. handler
14. severity
15. audience_types (JSONB array)
16. chat_types (JSONB array)
17. load_mode
18. state_conditions (JSONB)
19. priority
20. attribution
21. editable_by
22. is_active
23. entity_id
24. slug
25. token_count

## Step 6: Generate Embeddings

After import, generate embeddings for entities where `load_mode = 'SITUATION'`:
- Concatenate: `user_says + " " + what_this_is`
- Call Voyage API
- Update embedding column

## Step 7: Verify

```sql
SELECT entity_type, COUNT(*) FROM content_entities GROUP BY entity_type ORDER BY COUNT(*) DESC;
-- TOPIC: 33, RULE: 20, CHAT_CONTEXT: 9, HANDLER: 7, PERSONA: 5, RERANKER: 2
```

---

## Field Visibility by Entity Type

UI should show/hide fields based on entity_type:

| field | TOPIC | RULE | HANDLER | PERSONA | CHAT_CONTEXT | RERANKER |
|-------|-------|------|---------|---------|--------------|----------|
| what_this_is | show | show | show | show | show | show |
| frank_says | show | hide | show | hide | hide | hide |
| do_this | show | show | show | show | show | hide |
| never_do | show | show | show | show | show | hide |
| sample_dialog | show | hide | show | show | hide | hide |
| watch_for | show | show | hide | hide | hide | hide |
| escalate_if | show | show | hide | hide | hide | hide |
| handler | show | show | show | hide | hide | hide |
| severity | show | show | show | hide | hide | hide |
| load_mode | show | show | show | show | show | show |
| state_conditions | show | show | show | hide | hide | hide |

---

## Load Mode Logic

**Critical:** `audience_types` is ALWAYS the first filter. There is no "load for everyone" - if you want all audiences, you list all audience types.

- **ALWAYS** = load when audience matches (no further conditions)
- **STATE** = load when audience matches AND state_conditions met
- **SITUATION** = load when audience matches AND user message matches (via embedding similarity)
