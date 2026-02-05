# Job Application Tracker - Technical Specifications

## Table of Contents

1. [Database Schema](#1-database-schema)
2. [API Specification](#2-api-specification)
3. [Module Specifications](#3-module-specifications)
4. [Data Contracts](#4-data-contracts)
5. [LLM Prompt Templates](#5-llm-prompt-templates)
6. [Resume SOP Rules](#6-resume-sop-rules)
7. [Testing Requirements](#7-testing-requirements)

---

## 1. Database Schema

### 1.1 Core Tables

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(500),
    careers_url VARCHAR(500),
    research_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies(name);

-- Jobs (parsed JD data)
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    raw_posting TEXT NOT NULL,
    
    -- Extracted fields (JSONB for flexibility)
    extracted_data JSONB NOT NULL DEFAULT '{}',
    -- Structure: {
    --   title: string,
    --   location: string,
    --   remote_type: "remote" | "hybrid" | "onsite",
    --   salary_min: number | null,
    --   salary_max: number | null,
    --   salary_currency: string,
    --   required_skills: string[],
    --   preferred_skills: string[],
    --   tools_technologies: string[],
    --   soft_skills: string[],
    --   years_experience: number | null,
    --   education_requirements: string[],
    --   team_size: string | null,
    --   reports_to: string | null,
    --   benefits: string[],
    --   application_deadline: date | null
    -- }
    
    status VARCHAR(50) DEFAULT 'identified',
    -- identified, applied, interviewing, offered, rejected, withdrawn, archived
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_company ON jobs(company_id);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);

-- Resume templates (base versions)
CREATE TABLE resume_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    archetype VARCHAR(50) NOT NULL,
    -- wfm, bi, ai, cx, general
    
    description TEXT,
    base_docx_path VARCHAR(500),
    content_json JSONB NOT NULL,
    -- Structure mirrors Experiences JSON
    
    target_roles JSONB DEFAULT '[]',
    -- ["Director of WFM", "Capacity Planning Lead", ...]
    
    key_skills JSONB DEFAULT '[]',
    -- Prioritized skills for this archetype
    
    summary_template TEXT,
    -- Base professional summary
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Applications (customized for specific job)
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) NOT NULL,
    template_id INTEGER REFERENCES resume_templates(id) NOT NULL,
    
    -- Generated files
    resume_docx_path VARCHAR(500),
    resume_pdf_path VARCHAR(500),
    cover_letter_docx_path VARCHAR(500),
    cover_letter_pdf_path VARCHAR(500),
    output_directory VARCHAR(500),
    
    -- Customization metadata
    customized_content JSONB,
    -- Full resume content after LLM customization
    
    skills_matched JSONB DEFAULT '[]',
    skills_gap JSONB DEFAULT '[]',
    customization_notes TEXT,
    
    -- Tracking
    status VARCHAR(50) DEFAULT 'draft',
    -- draft, generated, reviewed, applied, responded, interviewing, offered, rejected, withdrawn
    
    applied_date DATE,
    response_date DATE,
    outcome VARCHAR(50),
    -- hired, rejected, ghosted, withdrawn
    
    salary_offered INTEGER,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_template ON applications(template_id);
CREATE INDEX idx_applications_applied ON applications(applied_date DESC);

-- Follow-ups
CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) NOT NULL,
    
    due_date DATE NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    -- email, call, linkedin, check_status
    
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_date DATE,
    response_received BOOLEAN DEFAULT FALSE,
    response_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_followups_due ON follow_ups(due_date) WHERE NOT completed;
CREATE INDEX idx_followups_app ON follow_ups(application_id);
```

### 1.2 Embedding Tables

```sql
-- Experience embeddings (Dave's inventory)
CREATE TABLE experience_embeddings (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    -- role, responsibility, achievement, skill
    
    source_reference VARCHAR(255) NOT NULL,
    -- JSON path or identifier (e.g., "meta.achievements.0")
    
    source_text TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    -- Voyage voyage-3 dimension
    
    metadata JSONB DEFAULT '{}',
    -- Additional context: role, company, dates
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exp_emb_type ON experience_embeddings(source_type);
CREATE INDEX idx_exp_emb_vector ON experience_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- JD requirement embeddings
CREATE TABLE jd_requirement_embeddings (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) NOT NULL,
    
    requirement_text TEXT NOT NULL,
    requirement_type VARCHAR(50) NOT NULL,
    -- required_skill, preferred_skill, tool, soft_skill, qualification
    
    embedding VECTOR(1024) NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jd_emb_job ON jd_requirement_embeddings(job_id);
CREATE INDEX idx_jd_emb_vector ON jd_requirement_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Cached similarity matches
CREATE TABLE experience_matches (
    id SERIAL PRIMARY KEY,
    jd_requirement_id INTEGER REFERENCES jd_requirement_embeddings(id) NOT NULL,
    experience_embedding_id INTEGER REFERENCES experience_embeddings(id) NOT NULL,
    similarity_score FLOAT NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(jd_requirement_id, experience_embedding_id)
);

CREATE INDEX idx_matches_jd ON experience_matches(jd_requirement_id);
CREATE INDEX idx_matches_score ON experience_matches(similarity_score DESC);
```

### 1.3 Analytics Tables

```sql
-- JD skill corpus (market analytics)
CREATE TABLE jd_skill_corpus (
    id SERIAL PRIMARY KEY,
    skill_term VARCHAR(255) NOT NULL UNIQUE,
    skill_category VARCHAR(100),
    -- technical, soft, tool, certification, methodology
    
    raw_variants JSONB DEFAULT '[]',
    -- ["Power BI", "PowerBI", "Power-BI"]
    
    first_seen DATE NOT NULL,
    last_seen DATE NOT NULL,
    total_occurrences INTEGER DEFAULT 1,
    jobs_containing INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_corpus_term ON jd_skill_corpus(skill_term);
CREATE INDEX idx_corpus_category ON jd_skill_corpus(skill_category);
CREATE INDEX idx_corpus_frequency ON jd_skill_corpus(jobs_containing DESC);

-- Skill occurrence tracking
CREATE TABLE jd_skill_occurrences (
    id SERIAL PRIMARY KEY,
    corpus_id INTEGER REFERENCES jd_skill_corpus(id) NOT NULL,
    job_id INTEGER REFERENCES jobs(id) NOT NULL,
    context_snippet TEXT,
    -- Surrounding text for reference
    
    requirement_type VARCHAR(50),
    -- required, preferred
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(corpus_id, job_id)
);

CREATE INDEX idx_occurrences_corpus ON jd_skill_occurrences(corpus_id);
CREATE INDEX idx_occurrences_job ON jd_skill_occurrences(job_id);

-- LLM generation logs
CREATE TABLE llm_generations (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    
    generation_type VARCHAR(50) NOT NULL,
    -- jd_extraction, resume_primary, resume_secondary, 
    -- cover_primary, cover_secondary, validation
    
    provider VARCHAR(50) NOT NULL,
    -- anthropic, openai
    
    model VARCHAR(100) NOT NULL,
    -- claude-sonnet-4-20250514, gpt-4o, etc.
    
    prompt_version VARCHAR(50),
    -- For A/B testing: "resume_v1", "resume_v2"
    
    prompt_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    generation_time_ms INTEGER,
    
    -- Quality tracking
    user_rating INTEGER,
    -- 1-5 manual rating
    
    user_feedback TEXT,
    edits_required BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_llm_gen_app ON llm_generations(application_id);
CREATE INDEX idx_llm_gen_type ON llm_generations(generation_type);
CREATE INDEX idx_llm_gen_provider ON llm_generations(provider, model);

-- Cost tracking
CREATE TABLE llm_cost_log (
    id SERIAL PRIMARY KEY,
    generation_id INTEGER REFERENCES llm_generations(id) NOT NULL,
    
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    
    cost_per_input_token DECIMAL(12, 10) NOT NULL,
    cost_per_output_token DECIMAL(12, 10) NOT NULL,
    total_cost_usd DECIMAL(10, 6) NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cost_gen ON llm_cost_log(generation_id);
CREATE INDEX idx_cost_date ON llm_cost_log(created_at);
```

### 1.4 Views

```sql
-- Application funnel view
CREATE VIEW application_funnel AS
SELECT 
    DATE_TRUNC('week', a.created_at) as week,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE a.status IN ('applied', 'responded', 'interviewing', 'offered')) as applied,
    COUNT(*) FILTER (WHERE a.status IN ('responded', 'interviewing', 'offered')) as responded,
    COUNT(*) FILTER (WHERE a.status IN ('interviewing', 'offered')) as interviewing,
    COUNT(*) FILTER (WHERE a.status = 'offered') as offered,
    COUNT(*) FILTER (WHERE a.outcome = 'hired') as hired
FROM applications a
GROUP BY DATE_TRUNC('week', a.created_at)
ORDER BY week DESC;

-- Response rate by template
CREATE VIEW template_response_rates AS
SELECT 
    rt.id as template_id,
    rt.name as template_name,
    rt.archetype,
    COUNT(a.id) as applications,
    COUNT(*) FILTER (WHERE a.status NOT IN ('draft', 'generated', 'reviewed')) as applied,
    COUNT(*) FILTER (WHERE a.response_date IS NOT NULL) as responses,
    ROUND(
        COUNT(*) FILTER (WHERE a.response_date IS NOT NULL)::DECIMAL / 
        NULLIF(COUNT(*) FILTER (WHERE a.status NOT IN ('draft', 'generated', 'reviewed')), 0) * 100, 
        1
    ) as response_rate_pct
FROM resume_templates rt
LEFT JOIN applications a ON a.template_id = rt.id
GROUP BY rt.id, rt.name, rt.archetype;

-- Cost summary
CREATE VIEW cost_summary AS
SELECT 
    DATE_TRUNC('week', cl.created_at) as week,
    cl.provider,
    COUNT(DISTINCT lg.application_id) as applications,
    SUM(cl.input_tokens) as total_input_tokens,
    SUM(cl.output_tokens) as total_output_tokens,
    SUM(cl.total_cost_usd) as total_cost
FROM llm_cost_log cl
JOIN llm_generations lg ON lg.id = cl.generation_id
GROUP BY DATE_TRUNC('week', cl.created_at), cl.provider
ORDER BY week DESC, provider;

-- Skill trends (last 30 days vs prior 30 days)
CREATE VIEW skill_trends AS
WITH recent AS (
    SELECT corpus_id, COUNT(*) as recent_count
    FROM jd_skill_occurrences
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY corpus_id
),
prior AS (
    SELECT corpus_id, COUNT(*) as prior_count
    FROM jd_skill_occurrences
    WHERE created_at >= NOW() - INTERVAL '60 days' 
      AND created_at < NOW() - INTERVAL '30 days'
    GROUP BY corpus_id
)
SELECT 
    c.skill_term,
    c.skill_category,
    c.jobs_containing as total_jobs,
    COALESCE(r.recent_count, 0) as last_30_days,
    COALESCE(p.prior_count, 0) as prior_30_days,
    ROUND(
        (COALESCE(r.recent_count, 0) - COALESCE(p.prior_count, 0))::DECIMAL / 
        NULLIF(COALESCE(p.prior_count, 0), 0) * 100,
        1
    ) as change_pct
FROM jd_skill_corpus c
LEFT JOIN recent r ON r.corpus_id = c.id
LEFT JOIN prior p ON p.corpus_id = c.id
ORDER BY c.jobs_containing DESC;
```

---

## 2. API Specification

### 2.1 Jobs Endpoints

```yaml
POST /api/v1/jobs/parse:
  description: Parse JD from URL or raw text
  request:
    body:
      url: string | null          # Job posting URL
      raw_text: string | null     # Raw JD text (if no URL)
      company_name: string | null # Override extracted company
  response:
    job_id: integer
    company: object
    extracted_data: object        # All extracted fields
    embedding_count: integer      # Requirements embedded
    corpus_updates: integer       # New/updated skill terms

GET /api/v1/jobs:
  description: List all jobs
  query:
    status: string[]              # Filter by status
    company_id: integer           # Filter by company
    limit: integer = 50
    offset: integer = 0
    sort: string = "created_at"
    order: string = "desc"
  response:
    jobs: Job[]
    total: integer

GET /api/v1/jobs/{id}:
  description: Get job details
  response:
    job: Job
    requirements_embedded: integer
    applications: Application[]

PUT /api/v1/jobs/{id}:
  description: Update job
  request:
    body:
      status: string
      extracted_data: object      # Partial update
      notes: string
  response:
    job: Job

DELETE /api/v1/jobs/{id}:
  description: Archive job (soft delete)
  response:
    success: boolean
```

### 2.2 Applications Endpoints

```yaml
POST /api/v1/applications:
  description: Start new application
  request:
    body:
      job_id: integer
      template_id: integer | null   # If null, system recommends
  response:
    application_id: integer
    recommended_templates: Template[]  # Top 2 ranked
    skills_matched: string[]
    skills_gap: string[]
    match_details: MatchDetail[]      # Semantic match breakdown

GET /api/v1/applications:
  description: List applications
  query:
    status: string[]
    job_id: integer
    template_id: integer
    date_from: date
    date_to: date
    limit: integer = 50
    offset: integer = 0
  response:
    applications: Application[]
    total: integer

GET /api/v1/applications/{id}:
  description: Get application details
  response:
    application: Application
    job: Job
    template: Template
    generations: LLMGeneration[]
    follow_ups: FollowUp[]

POST /api/v1/applications/{id}/select-template:
  description: Confirm template selection
  request:
    body:
      template_id: integer
  response:
    application: Application

POST /api/v1/applications/{id}/generate-resume:
  description: Generate customized resume via LLM
  request:
    body:
      provider: string = "anthropic"  # anthropic, openai
      model: string | null            # Default per provider
      prompt_version: string = "v1"   # For A/B testing
  response:
    application_id: integer
    customized_content: object
    generation_id: integer
    tokens_used: object
    estimated_cost: number

POST /api/v1/applications/{id}/second-opinion:
  description: Get second LLM opinion
  request:
    body:
      provider: string = "openai"
      model: string | null
      prompt_version: string = "v1"
  response:
    generation_id: integer
    suggestions: string[]
    diff_summary: string
    tokens_used: object
    estimated_cost: number

POST /api/v1/applications/{id}/generate-cover:
  description: Generate cover letter
  request:
    body:
      provider: string = "anthropic"
      prompt_version: string = "v1"
  response:
    cover_letter_content: string
    generation_id: integer
    tokens_used: object

POST /api/v1/applications/{id}/validate:
  description: Run ATS and SOP validation
  response:
    valid: boolean
    issues: ValidationIssue[]
    # Each issue: {type, severity, message, location}

POST /api/v1/applications/{id}/export:
  description: Generate final docx and PDF files
  response:
    resume_docx: string           # File path
    resume_pdf: string
    cover_letter_docx: string
    cover_letter_pdf: string
    output_directory: string

PUT /api/v1/applications/{id}:
  description: Update application
  request:
    body:
      status: string
      applied_date: date
      notes: string
      customized_content: object  # Manual edits
  response:
    application: Application

POST /api/v1/applications/{id}/mark-applied:
  description: Mark as applied and create follow-ups
  request:
    body:
      applied_date: date = today
      create_followups: boolean = true
      followup_days: integer[] = [7, 14]
  response:
    application: Application
    follow_ups_created: FollowUp[]
```

### 2.3 Templates Endpoints

```yaml
GET /api/v1/templates:
  description: List resume templates
  query:
    archetype: string
  response:
    templates: Template[]

POST /api/v1/templates:
  description: Create new template
  request:
    body:
      name: string
      archetype: string
      base_docx_path: string | null
      content_json: object
      target_roles: string[]
      key_skills: string[]
      summary_template: string
  response:
    template: Template

GET /api/v1/templates/{id}:
  response:
    template: Template

POST /api/v1/templates/{id}/suggest:
  description: Get template suggestions for a job
  request:
    body:
      job_id: integer
  response:
    recommendations: TemplateRecommendation[]
    # Each: {template_id, score, matched_skills, reasoning}

POST /api/v1/templates/import:
  description: Import template from existing docx
  request:
    body:
      docx_path: string
      name: string
      archetype: string
  response:
    template: Template
```

### 2.4 Analytics Endpoints

```yaml
GET /api/v1/analytics/funnel:
  description: Application outcome funnel
  query:
    weeks: integer = 12
  response:
    funnel: FunnelWeek[]
    # Each: {week, total, applied, responded, interviewing, offered, hired}

GET /api/v1/analytics/response-rates:
  description: Response rates by template
  response:
    by_template: TemplateRate[]
    by_company: CompanyRate[]
    by_month: MonthRate[]

GET /api/v1/analytics/salary:
  description: Salary tracking
  query:
    date_from: date
    date_to: date
  response:
    posted_ranges: SalaryRange[]
    offers: SalaryOffer[]
    avg_posted_min: number
    avg_posted_max: number

GET /api/v1/analytics/corpus:
  description: JD skill corpus analytics
  query:
    category: string | null
    limit: integer = 50
    trending: boolean = false
  response:
    skills: CorpusSkill[]
    trends: SkillTrend[]

GET /api/v1/analytics/llm-quality:
  description: LLM generation quality metrics
  query:
    provider: string | null
    generation_type: string | null
    date_from: date
    date_to: date
  response:
    by_provider: ProviderStats[]
    by_prompt_version: PromptStats[]
    avg_rating: number
    edit_rate: number

GET /api/v1/analytics/costs:
  description: LLM cost summary
  query:
    date_from: date
    date_to: date
    group_by: string = "week"   # day, week, month
  response:
    summary: CostPeriod[]
    total_cost: number
    avg_per_application: number
```

### 2.5 Follow-ups Endpoints

```yaml
GET /api/v1/follow-ups/due:
  description: Get due/overdue follow-ups
  query:
    include_completed: boolean = false
  response:
    overdue: FollowUp[]
    due_today: FollowUp[]
    upcoming: FollowUp[]

PUT /api/v1/follow-ups/{id}:
  description: Update follow-up
  request:
    body:
      completed: boolean
      response_received: boolean
      response_notes: string
  response:
    follow_up: FollowUp
```

### 2.6 Settings Endpoints

```yaml
GET /api/v1/settings/llm-config:
  description: Get LLM configuration
  response:
    primary_provider: string
    primary_model: string
    secondary_provider: string
    secondary_model: string
    prompt_versions: PromptVersion[]
    cost_rates: CostRate[]

PUT /api/v1/settings/llm-config:
  description: Update LLM configuration
  request:
    body:
      primary_provider: string
      primary_model: string
      secondary_provider: string
      secondary_model: string
  response:
    config: LLMConfig

POST /api/v1/settings/reindex-experiences:
  description: Re-embed experience inventory
  response:
    embeddings_created: integer
    time_ms: integer
```

---

## 3. Module Specifications

### 3.1 Embeddings Module (`packages/embeddings/`)

**Owner**: Bee 2

**Purpose**: Manage Voyage AI embeddings for semantic matching

**Files**:
```
embeddings/
├── __init__.py
├── voyage_client.py      # Voyage API wrapper
├── indexer.py            # Experience embedding management
├── matcher.py            # JD-to-experience matching
└── models.py             # Pydantic models
```

**voyage_client.py**:
```python
class VoyageClient:
    """Voyage AI embedding client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "voyage-3"  # 1024 dimensions
        self.base_url = "https://api.voyageai.com/v1"
    
    async def embed(
        self, 
        texts: list[str], 
        input_type: str = "document"  # or "query"
    ) -> list[list[float]]:
        """
        Embed texts using Voyage API.
        
        Args:
            texts: List of strings to embed (max 128 per call)
            input_type: "document" for indexing, "query" for search
            
        Returns:
            List of embedding vectors (1024 dimensions each)
        """
        ...
    
    async def embed_single(self, text: str, input_type: str = "query") -> list[float]:
        """Convenience method for single text"""
        ...
```

**indexer.py**:
```python
class ExperienceIndexer:
    """Index Dave's experience inventory for semantic search"""
    
    def __init__(self, voyage_client: VoyageClient, db: AsyncSession):
        self.voyage = voyage_client
        self.db = db
    
    async def index_experiences_json(self, json_path: str) -> int:
        """
        Parse experiences JSON and create embeddings.
        
        Indexes:
        - Each role's title + company
        - Each responsibility item
        - Each quantifiable achievement
        - Technical skills by category
        
        Returns:
            Number of embeddings created
        """
        ...
    
    async def index_single(
        self, 
        source_type: str,
        source_reference: str,
        source_text: str,
        metadata: dict
    ) -> int:
        """Index a single text item"""
        ...
    
    async def get_embedding_count(self) -> dict:
        """Return counts by source_type"""
        ...
```

**matcher.py**:
```python
class SemanticMatcher:
    """Match JD requirements to experience"""
    
    def __init__(self, voyage_client: VoyageClient, db: AsyncSession):
        self.voyage = voyage_client
        self.db = db
    
    async def embed_jd_requirements(
        self, 
        job_id: int, 
        requirements: list[dict]
    ) -> int:
        """
        Embed JD requirements for matching.
        
        Args:
            job_id: Job ID to associate
            requirements: List of {text, type} dicts
            
        Returns:
            Number of embeddings created
        """
        ...
    
    async def match_experience(
        self,
        job_id: int,
        top_k: int = 5
    ) -> list[dict]:
        """
        Find best experience matches for each JD requirement.
        
        Returns:
            List of {
                requirement_text: str,
                requirement_type: str,
                matches: [{
                    experience_text: str,
                    source_type: str,
                    source_reference: str,
                    similarity_score: float,
                    metadata: dict
                }]
            }
        """
        ...
    
    async def get_skills_coverage(self, job_id: int) -> dict:
        """
        Analyze skills coverage.
        
        Returns:
            {
                matched: [skills with similarity > 0.7],
                partial: [skills with similarity 0.5-0.7],
                gap: [skills with similarity < 0.5]
            }
        """
        ...
```

**Interface Contract**:
```python
# Input: Job requirements as parsed from JD
requirements = [
    {"text": "5+ years SQL experience", "type": "required_skill"},
    {"text": "Experience with Power BI", "type": "tool"},
    {"text": "Strong communication skills", "type": "soft_skill"}
]

# Output: Ranked experience matches
matches = await matcher.match_experience(job_id=123, top_k=5)
# Returns list of requirements with their best-matching experiences
```

---

### 3.2 JD Parser Module (`packages/jd-parser/`)

**Owner**: Bee 2

**Purpose**: Extract structured data from job postings

**Files**:
```
jd-parser/
├── __init__.py
├── scraper.py            # URL to text extraction
├── extractor.py          # LLM-powered field extraction
├── normalizer.py         # Skill term normalization
├── corpus.py             # Skill frequency tracking
└── models.py             # Pydantic models
```

**scraper.py**:
```python
class JDScraper:
    """Extract text from job posting URLs"""
    
    SUPPORTED_SITES = {
        "linkedin.com": LinkedInScraper,
        "indeed.com": IndeedScraper,
        "greenhouse.io": GreenhouseScraper,
        "lever.co": LeverScraper,
        # Generic fallback
    }
    
    async def scrape(self, url: str) -> dict:
        """
        Extract job posting text from URL.
        
        Returns:
            {
                raw_text: str,
                title: str | None,
                company: str | None,
                location: str | None,
                source: str,
                scraped_at: datetime
            }
        """
        ...
    
    async def detect_site(self, url: str) -> str:
        """Identify job board from URL"""
        ...
```

**extractor.py**:
```python
class JDExtractor:
    """LLM-powered field extraction from JD text"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def extract(self, raw_text: str) -> dict:
        """
        Extract structured fields from JD text.
        
        Returns:
            {
                title: str,
                company: str | None,
                location: str | None,
                remote_type: "remote" | "hybrid" | "onsite" | None,
                salary_min: int | None,
                salary_max: int | None,
                salary_currency: str,
                required_skills: list[str],
                preferred_skills: list[str],
                tools_technologies: list[str],
                soft_skills: list[str],
                years_experience: int | None,
                education_requirements: list[str],
                team_size: str | None,
                reports_to: str | None,
                benefits: list[str],
                application_deadline: date | None,
                raw_requirements: list[{text, type}]
            }
        """
        ...
```

**corpus.py**:
```python
class SkillCorpus:
    """Track skill frequency across JDs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_from_job(
        self, 
        job_id: int, 
        extracted_skills: dict
    ) -> dict:
        """
        Update corpus with skills from a job.
        
        Args:
            job_id: Job ID
            extracted_skills: {
                required_skills: [],
                preferred_skills: [],
                tools_technologies: []
            }
            
        Returns:
            {
                new_terms: int,
                updated_terms: int,
                total_occurrences: int
            }
        """
        ...
    
    async def normalize_skill(self, raw_skill: str) -> str:
        """
        Normalize skill term for deduplication.
        
        Examples:
            "Power BI" -> "power_bi"
            "PowerBI" -> "power_bi"
            "Microsoft Power BI" -> "power_bi"
        """
        ...
    
    async def get_top_skills(
        self, 
        category: str = None,
        limit: int = 50
    ) -> list[dict]:
        """Get most frequent skills"""
        ...
    
    async def get_trends(
        self, 
        days: int = 30
    ) -> list[dict]:
        """Get trending skills (increasing frequency)"""
        ...
```

---

### 3.3 Resume Engine Module (`packages/resume-engine/`)

**Owner**: Bee 3

**Purpose**: Template management, customization, and validation

**Files**:
```
resume-engine/
├── __init__.py
├── templates.py          # Template CRUD and import
├── selector.py           # Template ranking/recommendation
├── customizer.py         # LLM customization with SOP
├── validator.py          # ATS and char count validation
├── sop_rules.py          # Resume SOP as code
└── models.py
```

**selector.py**:
```python
class TemplateSelector:
    """Recommend best templates for a job"""
    
    def __init__(self, db: AsyncSession, matcher: SemanticMatcher):
        self.db = db
        self.matcher = matcher
    
    async def recommend(
        self, 
        job_id: int, 
        limit: int = 2
    ) -> list[dict]:
        """
        Rank templates by fit to job requirements.
        
        Returns top 2:
            [{
                template_id: int,
                template_name: str,
                archetype: str,
                score: float,
                matched_skills: list[str],
                reasoning: str
            }]
        """
        ...
```

**customizer.py**:
```python
class ResumeCustomizer:
    """LLM-powered resume customization"""
    
    def __init__(
        self, 
        llm_service: LLMService,
        matcher: SemanticMatcher,
        sop: ResumeSOPRules
    ):
        self.llm = llm_service
        self.matcher = matcher
        self.sop = sop
    
    async def customize(
        self,
        application_id: int,
        template_id: int,
        job_id: int,
        provider: str = "anthropic",
        prompt_version: str = "v1"
    ) -> dict:
        """
        Generate customized resume content.
        
        Process:
        1. Get semantic matches for JD requirements
        2. Build prompt with template + matches + SOP rules
        3. Call LLM for customization
        4. Validate output against SOP
        5. Store generation and return
        
        Returns:
            {
                customized_content: dict,  # Full resume structure
                generation_id: int,
                tokens_used: {input, output},
                validation_issues: list
            }
        """
        ...
    
    async def get_second_opinion(
        self,
        application_id: int,
        provider: str = "openai",
        prompt_version: str = "v1"
    ) -> dict:
        """
        Get alternative LLM review of customized resume.
        
        Returns:
            {
                suggestions: list[str],
                diff_summary: str,
                alternative_bullets: list[dict],
                generation_id: int
            }
        """
        ...
```

**validator.py**:
```python
class ResumeValidator:
    """Validate resume against SOP and ATS requirements"""
    
    def __init__(self, sop: ResumeSOPRules):
        self.sop = sop
    
    def validate(self, content: dict) -> list[dict]:
        """
        Run all validations.
        
        Returns list of issues:
            [{
                type: str,           # char_count, formatting, ats, sop
                severity: str,       # error, warning
                message: str,
                location: str,       # e.g., "summary", "meta.bullets.2"
                expected: str | None,
                actual: str | None
            }]
        """
        ...
    
    def check_character_counts(self, content: dict) -> list[dict]:
        """
        Validate character counts per SOP:
        - Professional summary: 225-400 chars
        - Role intro: 150-225 chars
        - Short bullets: 60-80 chars
        - Long bullets: 130-160 chars
        - No bullets in 81-129 range
        """
        ...
    
    def check_ats_compliance(self, content: dict) -> list[dict]:
        """
        Check ATS-friendly formatting:
        - No tables
        - No images
        - Standard fonts
        - No headers/footers with critical info
        - Contact info in body
        """
        ...
    
    def check_sop_rules(self, content: dict) -> list[dict]:
        """
        Verify SOP compliance:
        - 15+ years stated
        - No pre-2004 roles
        - Required sections present
        - Formatting correct
        """
        ...
```

**sop_rules.py**:
```python
class ResumeSOPRules:
    """Resume SOP as code"""
    
    # Character count ranges
    SUMMARY_MIN_CHARS = 225
    SUMMARY_MAX_CHARS = 400
    
    ROLE_INTRO_MIN_CHARS = 150
    ROLE_INTRO_MAX_CHARS = 225
    
    BULLET_SHORT_MIN = 60
    BULLET_SHORT_MAX = 80
    BULLET_LONG_MIN = 130
    BULLET_LONG_MAX = 160
    BULLET_FORBIDDEN_MIN = 81
    BULLET_FORBIDDEN_MAX = 129
    
    # Content rules
    YEARS_EXPERIENCE = "15+"
    EXCLUDE_ROLES_BEFORE = 2004
    MIN_BULLETS_PER_ROLE = 3
    MAX_BULLETS_PER_ROLE = 6
    
    # Required sections
    REQUIRED_SECTIONS = [
        "PROFESSIONAL SUMMARY",
        "PROFESSIONAL EXPERIENCE", 
        "ADDITIONAL TECHNICAL SKILLS",
        "EDUCATION & CERTIFICATIONS"
    ]
    
    def is_bullet_length_valid(self, length: int) -> tuple[bool, str]:
        """Check if bullet length is valid"""
        if length < self.BULLET_SHORT_MIN:
            return False, f"Too short ({length} < {self.BULLET_SHORT_MIN})"
        if self.BULLET_FORBIDDEN_MIN <= length <= self.BULLET_FORBIDDEN_MAX:
            return False, f"In forbidden range ({self.BULLET_FORBIDDEN_MIN}-{self.BULLET_FORBIDDEN_MAX})"
        if length > self.BULLET_LONG_MAX:
            return False, f"Too long ({length} > {self.BULLET_LONG_MAX})"
        return True, "Valid"
```

---

### 3.4 LLM Service Module (`packages/llm-service/`)

**Owner**: Bee 1

**Purpose**: Multi-provider LLM with cost tracking

**Files**:
```
llm-service/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── base.py           # Abstract provider
│   ├── anthropic.py      # Claude adapter
│   └── openai.py         # GPT adapter
├── router.py             # Provider selection
├── prompts/
│   ├── jd_extraction.py
│   ├── resume_customization.py
│   ├── cover_letter.py
│   └── second_opinion.py
├── cost_tracker.py       # Token and cost logging
└── models.py
```

**providers/base.py**:
```python
class LLMProvider(ABC):
    """Abstract LLM provider"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> dict:
        """
        Generate completion.
        
        Returns:
            {
                text: str,
                input_tokens: int,
                output_tokens: int,
                model: str,
                generation_time_ms: int
            }
        """
        ...
    
    @property
    @abstractmethod
    def cost_per_input_token(self) -> float:
        ...
    
    @property
    @abstractmethod
    def cost_per_output_token(self) -> float:
        ...
```

**cost_tracker.py**:
```python
class CostTracker:
    """Track LLM token usage and costs"""
    
    # Current rates (update as needed)
    RATES = {
        "anthropic": {
            "claude-sonnet-4-20250514": {"input": 0.003/1000, "output": 0.015/1000},
            "claude-3-5-haiku-20241022": {"input": 0.0008/1000, "output": 0.004/1000},
        },
        "openai": {
            "gpt-4o": {"input": 0.0025/1000, "output": 0.01/1000},
            "gpt-4o-mini": {"input": 0.00015/1000, "output": 0.0006/1000},
        }
    }
    
    async def log_generation(
        self,
        generation_id: int,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Log generation and return cost.
        
        Returns:
            Total cost in USD
        """
        ...
    
    async def get_summary(
        self,
        date_from: date = None,
        date_to: date = None
    ) -> dict:
        """
        Get cost summary.
        
        Returns:
            {
                total_cost: float,
                by_provider: {provider: cost},
                by_generation_type: {type: cost},
                total_applications: int,
                avg_per_application: float
            }
        """
        ...
```

---

### 3.5 Document Generator Module (`packages/doc-generator/`)

**Owner**: Bee 3

**Purpose**: Generate formatted docx and PDF files

**Files**:
```
doc-generator/
├── __init__.py
├── docx_builder.js       # Node.js docx-js implementation
├── pdf_converter.py      # LibreOffice wrapper
├── file_manager.py       # Filesystem organization
└── templates/            # docx-js template configs
```

**docx_builder.js** (Node.js):
```javascript
/**
 * Build resume docx from structured content.
 * Uses docx-js library per SKILL.md guidelines.
 */

const { Document, Packer, Paragraph, TextRun, ... } = require('docx');

async function buildResume(content, outputPath) {
    /**
     * Args:
     *   content: {
     *     contact: {name, title, location, email, phone, linkedin},
     *     summary: string,
     *     experience: [{
     *       title, company, location, dates,
     *       intro, technologies, bullets
     *     }],
     *     skills: {category: [skills]},
     *     education: [{degree, institution, status}],
     *     certifications: [string]
     *   }
     *   outputPath: string
     * 
     * Returns:
     *   {success: boolean, path: string, error: string}
     */
    
    // Follow docx-js rules from SKILL.md:
    // - US Letter page size
    // - Proper numbering config for bullets
    // - No unicode bullets
    // - Arial font
    // etc.
}

async function buildCoverLetter(content, outputPath) {
    /**
     * Args:
     *   content: {
     *     contact: {...},
     *     recipient: {name, title, company, address},
     *     date: string,
     *     subject: string,
     *     paragraphs: [string],
     *     closing: string
     *   }
     */
}

module.exports = { buildResume, buildCoverLetter };
```

**file_manager.py**:
```python
class FileManager:
    """Manage output file organization"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
    
    def create_application_directory(
        self,
        company: str,
        title: str,
        date: date = None
    ) -> Path:
        """
        Create directory for application files.
        
        Structure:
            /postings/2025-01/quince-director-wfm/
        
        Returns:
            Path to created directory
        """
        ...
    
    def save_application_files(
        self,
        application_id: int,
        directory: Path,
        files: dict
    ) -> dict:
        """
        Save all application files to directory.
        
        Args:
            files: {
                resume_docx: bytes,
                resume_pdf: bytes,
                cover_docx: bytes,
                cover_pdf: bytes,
                job_posting: str,
                skills_analysis: dict,
                metadata: dict
            }
            
        Returns:
            {filename: filepath} for all saved files
        """
        ...
```

---

## 4. Data Contracts

### 4.1 Pydantic Models (`packages/common/schemas/`)

```python
# jobs.py
class JobCreate(BaseModel):
    url: str | None = None
    raw_text: str | None = None
    company_name: str | None = None

class JobExtractedData(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    remote_type: Literal["remote", "hybrid", "onsite"] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "USD"
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    tools_technologies: list[str] = []
    soft_skills: list[str] = []
    years_experience: int | None = None
    education_requirements: list[str] = []
    team_size: str | None = None
    reports_to: str | None = None
    benefits: list[str] = []
    application_deadline: date | None = None

class Job(BaseModel):
    id: int
    company_id: int | None
    title: str
    url: str | None
    raw_posting: str
    extracted_data: JobExtractedData
    status: str
    created_at: datetime
    updated_at: datetime

# applications.py
class ApplicationCreate(BaseModel):
    job_id: int
    template_id: int | None = None

class ApplicationUpdate(BaseModel):
    status: str | None = None
    applied_date: date | None = None
    notes: str | None = None
    customized_content: dict | None = None

class Application(BaseModel):
    id: int
    job_id: int
    template_id: int
    resume_docx_path: str | None
    resume_pdf_path: str | None
    cover_letter_docx_path: str | None
    cover_letter_pdf_path: str | None
    output_directory: str | None
    customized_content: dict | None
    skills_matched: list[str]
    skills_gap: list[str]
    status: str
    applied_date: date | None
    response_date: date | None
    outcome: str | None
    salary_offered: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

# embeddings.py
class ExperienceMatch(BaseModel):
    experience_text: str
    source_type: str
    source_reference: str
    similarity_score: float
    metadata: dict

class RequirementMatches(BaseModel):
    requirement_text: str
    requirement_type: str
    matches: list[ExperienceMatch]

class SkillsCoverage(BaseModel):
    matched: list[str]
    partial: list[str]
    gap: list[str]

# generations.py
class GenerationResult(BaseModel):
    generation_id: int
    text: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    generation_time_ms: int

class ValidationIssue(BaseModel):
    type: str
    severity: Literal["error", "warning"]
    message: str
    location: str
    expected: str | None = None
    actual: str | None = None
```

---

## 5. LLM Prompt Templates

### 5.1 JD Extraction Prompt

```python
JD_EXTRACTION_SYSTEM = """
You are a job description parser. Extract structured information from job postings.
Return valid JSON only, no markdown formatting.
"""

JD_EXTRACTION_USER = """
Parse the following job description and extract all available fields.

<job_description>
{raw_text}
</job_description>

Return JSON with these fields (use null for unavailable):
{{
    "title": "exact job title",
    "company": "company name",
    "location": "city, state or remote",
    "remote_type": "remote" | "hybrid" | "onsite",
    "salary_min": number or null,
    "salary_max": number or null,
    "salary_currency": "USD",
    "required_skills": ["skill 1", "skill 2"],
    "preferred_skills": ["skill 1", "skill 2"],
    "tools_technologies": ["tool 1", "tool 2"],
    "soft_skills": ["skill 1", "skill 2"],
    "years_experience": number or null,
    "education_requirements": ["requirement 1"],
    "team_size": "description or null",
    "reports_to": "title or null",
    "benefits": ["benefit 1"],
    "application_deadline": "YYYY-MM-DD or null",
    "raw_requirements": [
        {{"text": "requirement text", "type": "required_skill|preferred_skill|tool|soft_skill|qualification"}}
    ]
}}
"""
```

### 5.2 Resume Customization Prompt

```python
RESUME_CUSTOMIZATION_SYSTEM = """
You are a resume customization expert. Tailor resumes to job requirements while 
following strict formatting rules.

CRITICAL CHARACTER COUNT RULES:
- Professional summary: 225-400 characters (including spaces/punctuation)
- Role introduction: 150-225 characters
- Bullets: Either 60-80 chars (short) OR 130-160 chars (long)
- FORBIDDEN: Any bullet between 81-129 characters
- FORBIDDEN: Any bullet under 60 or over 160 characters

Always use "15+ years" for experience references.
Do not include any roles that started before 2004.
"""

RESUME_CUSTOMIZATION_USER = """
Customize this resume for the target job.

<job_requirements>
{job_requirements_json}
</job_requirements>

<semantic_matches>
{semantic_matches_json}
</semantic_matches>

<base_resume>
{template_content_json}
</base_resume>

<sop_rules>
{sop_rules}
</sop_rules>

Return the customized resume as JSON matching the base_resume structure.
Incorporate the semantic matches to highlight relevant experience.
Follow all SOP rules exactly.
"""
```

### 5.3 Second Opinion Prompt

```python
SECOND_OPINION_SYSTEM = """
You are a resume reviewer providing a second opinion on customized resumes.
Identify improvements without completely rewriting.
"""

SECOND_OPINION_USER = """
Review this customized resume against the job requirements.

<job_requirements>
{job_requirements_json}
</job_requirements>

<customized_resume>
{customized_content_json}
</customized_resume>

<sop_rules>
{sop_rules}
</sop_rules>

Provide:
1. List of specific suggestions (max 5)
2. Alternative bullet phrasings if any could be improved
3. Any SOP violations found
4. Overall assessment (1-5 rating)

Return JSON:
{{
    "suggestions": ["suggestion 1", ...],
    "alternative_bullets": [{{"location": "meta.bullets.2", "original": "...", "improved": "..."}}],
    "sop_violations": ["violation 1", ...],
    "rating": 4,
    "summary": "Brief assessment"
}}
"""
```

---

## 6. Resume SOP Rules

Full SOP rules are embedded in `packages/resume-engine/sop_rules.py`.

Key rules for LLM prompts:

```
RESUME SOP RULES - MUST FOLLOW EXACTLY

1. CHARACTER COUNTS (including spaces and punctuation):
   - Professional Summary: 225-400 characters
   - Role Introduction: 150-225 characters  
   - Bullets: ONLY two valid ranges:
     * Short: 60-80 characters
     * Long: 130-160 characters
   - INVALID: <60, 81-129, or >160 characters

2. CONTENT RULES:
   - Always state "15+ years" of experience
   - Exclude ALL roles starting before January 2004
   - 3-6 bullets per role
   - No repeated bullets across roles
   - Use quantifiable metrics when available

3. FORMATTING:
   - Name: Bold or uppercase
   - Section headings: Bold (PROFESSIONAL SUMMARY, etc.)
   - Role titles: Bold, ALL CAPS
   - Company/dates: Italics
   - No horizontal lines
   - No soft returns in bullets

4. REQUIRED SECTIONS:
   - PROFESSIONAL SUMMARY
   - PROFESSIONAL EXPERIENCE
   - ADDITIONAL TECHNICAL SKILLS
   - EDUCATION & CERTIFICATIONS
```

---

## 7. Testing Requirements

### 7.1 Unit Tests per Module

**Embeddings**:
- `test_voyage_client.py`: Mock API calls, verify embedding dimensions
- `test_indexer.py`: Test experience JSON parsing, embedding creation
- `test_matcher.py`: Test similarity scoring, top-k retrieval

**JD Parser**:
- `test_scraper.py`: Mock HTTP responses for each job board
- `test_extractor.py`: Mock LLM, verify field extraction
- `test_corpus.py`: Test skill normalization, frequency updates

**Resume Engine**:
- `test_selector.py`: Test template ranking logic
- `test_customizer.py`: Mock LLM, verify SOP integration
- `test_validator.py`: Test all character count rules, ATS checks

**LLM Service**:
- `test_providers.py`: Mock API calls for each provider
- `test_cost_tracker.py`: Verify cost calculations

**Doc Generator**:
- `test_docx_builder.js`: Verify docx structure (Jest)
- `test_file_manager.py`: Test directory creation, file organization

### 7.2 Integration Tests

```python
# test_full_workflow.py

async def test_jd_to_resume_flow():
    """Test complete workflow from JD input to resume export"""
    
    # 1. Parse JD
    job = await parse_jd(raw_text=SAMPLE_JD)
    assert job.extracted_data.required_skills
    
    # 2. Create application
    app = await create_application(job_id=job.id)
    assert len(app.recommended_templates) == 2
    
    # 3. Select template
    await select_template(app.id, app.recommended_templates[0].id)
    
    # 4. Generate resume
    result = await generate_resume(app.id)
    assert result.validation_issues == []
    
    # 5. Get second opinion
    opinion = await get_second_opinion(app.id)
    assert opinion.rating >= 3
    
    # 6. Export
    files = await export_application(app.id)
    assert Path(files.resume_pdf).exists()
```

### 7.3 Fixtures

```python
# conftest.py

@pytest.fixture
def sample_jd():
    return """
    Director, WFM, Planning, & Business Operations
    Quince - Remote
    $140,000 - $170,000
    
    Requirements:
    - 5+ years workforce management experience
    - Experience with capacity planning and forecasting
    - Strong SQL skills
    - Experience managing BPO relationships
    ...
    """

@pytest.fixture
def sample_experiences():
    return json.load(open("fixtures/experiences.json"))

@pytest.fixture
def mock_voyage():
    """Mock Voyage API returning consistent embeddings"""
    ...

@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API"""
    ...
```

---

## Appendix: Environment Setup

### A.1 Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/job_tracker

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
VOYAGE_API_KEY=pa-...

# Paths
POSTINGS_DIR=/path/to/postings
TEMPLATES_DIR=/path/to/templates
EXPERIENCES_JSON=/path/to/experiences.json

# Optional
LOG_LEVEL=INFO
ENABLE_COST_TRACKING=true
```

### A.2 Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: jobtracker
      POSTGRES_PASSWORD: localdev
      POSTGRES_DB: job_tracker
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### A.3 Python Dependencies

```toml
[project]
name = "job-tracker"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncpg>=0.29.0",
    "pgvector>=0.2.4",
    "alembic>=1.13.1",
    "pydantic>=2.5.3",
    "httpx>=0.26.0",
    "anthropic>=0.18.0",
    "openai>=1.10.0",
    "beautifulsoup4>=4.12.3",
    "python-docx>=1.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.4",
    "pytest-asyncio>=0.23.3",
    "pytest-cov>=4.1.0",
]
```
