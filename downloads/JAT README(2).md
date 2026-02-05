# Job Application Tracker & Resume Automation Platform

## Overview

A localhost web application that automates the job application workflow: parsing job descriptions, semantically matching requirements to experience, generating tailored resumes and cover letters with LLM assistance, and tracking application outcomes.

## Problem Statement

Manual resume customization is time-consuming and inconsistent. Dave submits 5-10 applications per weekday, requiring:
- Reading and extracting key requirements from each JD
- Matching his experience to those requirements
- Customizing resume content and formatting
- Writing cover letters
- Tracking application status and follow-ups
- Analyzing what's working (which resume versions, which companies)

## Solution

Automate the entire pipeline with semantic AI matching and LLM-powered document generation, while maintaining human control over final decisions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Role Hub │ │ Resume   │ │ Cover    │ │ Tracker  │ │Analytics │      │
│  │ (JD+Gen) │ │ Review   │ │ Letter   │ │ Dashboard│ │ & Trends │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │  JD Parser   │ │   Semantic   │ │  LLM Service │ │Doc Generator │   │
│  │  + Site Intel│ │   Matcher    │ │  (Multi-LLM) │ │ (docx/PDF)   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                                      │
│  │  Background  │ │   Resume     │                                      │
│  │  Job Worker  │ │   Engine     │                                      │
│  └──────────────┘ └──────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL + pgvector                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Roles   │ │ JD       │ │Embeddings│ │ LLM Logs │ │ Site     │      │
│  │          │ │ Versions │ │ (vector) │ │ & Costs  │ │ Intel    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                 │
│  │ Resume   │ │ Apps     │ │Background│                                 │
│  │ Gens     │ │          │ │ Jobs     │                                 │
│  └──────────┘ └──────────┘ └──────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Filesystem                                       │
│  /postings/                                                              │
│  └── 2025-01/                                                            │
│      └── quince-director-wfm/                                            │
│          ├── job_posting.txt                                             │
│          ├── skills_analysis.json                                        │
│          ├── resume_v1.docx / .pdf                                       │
│          ├── cover_letter_v1.docx / .pdf                                 │
│          ├── provenance.json                                             │
│          └── metadata.json                                               │
└─────────────────────────────────────────────────────────────────────────┘
```

## Entity Model

```
Role (anchor entity)
├── company_id → Company
├── site_id → SiteIntelligence
│
├── JobDescription (versioned)
│   ├── version 1
│   ├── version 2 (current)
│   └── ...
│
├── ResumeGeneration (versioned per JD)
│   ├── jd_version_id → JobDescription
│   ├── template_id → ResumeTemplate
│   ├── provenance (full reproducibility)
│   └── CoverLetterGeneration
│
└── Application
    ├── resume_generation_id
    └── cover_letter_generation_id
```

## Core Workflow

```
1. INPUT           2. ANALYZE           3. MATCH              4. GENERATE
┌─────────┐       ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
│ Paste   │──────▶│ Extract:    │─────▶│ Semantic    │──────▶│ LLM Primary │
│ JD URL  │       │ - Title     │      │ similarity  │       │ customizes  │
│ or text │       │ - Skills    │      │ vs. your    │       │ resume      │
└─────────┘       │ - Salary    │      │ experience  │       └──────┬──────┘
                  │ - Remote    │      │ embeddings  │              │
                  │ - Tools     │      └─────────────┘              ▼
                  └─────────────┘                            ┌─────────────┐
                        │                                    │ LLM Second  │
                        ▼                                    │ opinion     │
                  ┌─────────────┐                            └──────┬──────┘
                  │ Update      │                                   │
                  │ JD corpus   │                                   ▼
                  │ analytics   │                            ┌─────────────┐
                  └─────────────┘                            │ Human       │
                                                             │ review &    │
5. EXPORT          6. TRACK            7. ANALYZE            │ approve     │
┌─────────┐       ┌─────────────┐      ┌─────────────┐       └─────────────┘
│ docx +  │◀──────│ Application │◀─────│ Response    │
│ PDF     │       │ status      │      │ rates by    │
│ to disk │       │ follow-ups  │      │ template    │
└─────────┘       └─────────────┘      └─────────────┘
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Frontend | React + TypeScript | Dave's recent experience, component reuse |
| Backend | FastAPI + Python | Fast dev, async support, type hints |
| Database | PostgreSQL + pgvector | Single DB for relational + vector, sufficient scale |
| Embeddings | Voyage AI | High quality, Dave has account |
| LLM Primary | Anthropic Claude | Quality, Dave has account |
| LLM Secondary | OpenAI GPT-4o | Alternative perspective, A/B testing |
| Doc Generation | docx-js (Node) | Proven for Dave's resume formatting |
| PDF Conversion | LibreOffice headless | Reliable docx→PDF |
| Web Scraping | BeautifulSoup + requests | JD extraction from job boards |

## Project Structure

```
job-tracker/
├── packages/
│   ├── common/              # Shared types, schemas, constants
│   │   ├── schemas/         # Pydantic models
│   │   ├── types/           # TypeScript types
│   │   └── constants.py     # Shared constants
│   │
│   ├── db/                  # Database layer
│   │   ├── models/          # SQLAlchemy models
│   │   ├── migrations/      # Alembic migrations
│   │   └── repository.py    # Data access patterns
│   │
│   ├── embeddings/          # Semantic similarity engine
│   │   ├── voyage_client.py # Voyage AI integration
│   │   ├── indexer.py       # Experience embedding management
│   │   └── matcher.py       # JD-to-experience matching
│   │
│   ├── jd-parser/           # JD extraction & corpus
│   │   ├── scraper.py       # URL→text extraction
│   │   ├── site_adapters/   # Per-site scraping adapters
│   │   │   ├── linkedin.py
│   │   │   ├── greenhouse.py
│   │   │   └── generic.py
│   │   ├── extractor.py     # LLM-powered field extraction
│   │   ├── site_intelligence.py # Site learning layer
│   │   └── corpus.py        # Skill frequency tracking
│   │
│   ├── resume-engine/       # Template & customization
│   │   ├── templates.py     # Template management
│   │   ├── selector.py      # Ranking & recommendation
│   │   ├── customizer.py    # LLM customization with SOP
│   │   └── validator.py     # ATS & char count validation
│   │
│   ├── llm-service/         # Multi-provider LLM
│   │   ├── providers/       # Claude, OpenAI adapters
│   │   ├── router.py        # Provider selection logic
│   │   ├── prompts/         # Versioned prompt templates
│   │   └── cost_tracker.py  # Token & cost logging
│   │
│   ├── doc-generator/       # Document output
│   │   ├── docx_builder.js  # docx-js implementation
│   │   ├── pdf_converter.py # LibreOffice wrapper
│   │   └── file_manager.py  # Filesystem organization
│   │
│   ├── worker/              # Background job processing
│   │   ├── queue.py         # Job queue management
│   │   ├── worker.py        # Job execution worker
│   │   └── handlers/        # Job type handlers
│   │
│   └── api/                 # FastAPI application
│       ├── routes/          # Endpoint definitions
│       ├── middleware/      # Auth, logging, etc.
│       └── main.py          # App entry point
│
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Route pages
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client
│   │   └── store/           # State management
│   └── package.json
│
├── data/
│   ├── experiences.json     # Dave's experience inventory
│   ├── resume_templates/    # Base docx templates
│   └── sop/                 # Resume SOP rules
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docker-compose.yml       # PostgreSQL, app services
├── alembic.ini              # DB migration config
├── pyproject.toml           # Python dependencies
└── README.md
```

## Module Ownership (HiveMind Distribution)

Each module is designed for independent development by worker bees:

| Module | Owner | Dependencies | Interface |
|--------|-------|--------------|-----------|
| `common` | Q33N | None | Defines all shared types |
| `db` | Bee 1 | common | Repository pattern, migrations |
| `embeddings` | Bee 2 | common, db | `match_experience(jd_id) → ranked_matches` |
| `jd-parser` | Bee 2 | common, db, llm-service | `parse_jd(url_or_text) → Role, JobDescription` |
| `resume-engine` | Bee 3 | common, db, embeddings | `customize_resume(role_id, jd_id, template_id) → ResumeGeneration` |
| `llm-service` | Bee 1 | common, db | `generate(prompt, provider) → Response` |
| `doc-generator` | Bee 3 | common | `build_docx(resume_gen) → filepath` |
| `worker` | Bee 1 | all | Background job processing |
| `api` | Q33N | all | Orchestration layer |
| `frontend` | Bee 4 | api | React UI |

## Setup Instructions

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL 15+ with pgvector extension
- Docker (optional, for PostgreSQL)

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/job_tracker

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
VOYAGE_API_KEY=pa-...

# Paths
POSTINGS_DIR=/path/to/postings
TEMPLATES_DIR=/path/to/templates
EXPERIENCES_JSON=/path/to/experiences.json
```

### Database Setup

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Seed experience embeddings
python -m packages.embeddings.indexer --seed
```

### Backend

```bash
cd job-tracker
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn packages.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Quick Reference

See `SPECS.md` for complete API documentation.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs/parse` | POST | Parse JD from URL or text |
| `/api/v1/applications` | POST | Start new application |
| `/api/v1/applications/{id}/generate-resume` | POST | LLM customization |
| `/api/v1/applications/{id}/second-opinion` | POST | Secondary LLM review |
| `/api/v1/applications/{id}/export` | POST | Generate docx/PDF |
| `/api/v1/analytics/funnel` | GET | Application outcome funnel |
| `/api/v1/analytics/corpus` | GET | JD skill frequency trends |

## Development Workflow

1. **Q33N** creates feature branch, defines interfaces in `common/`
2. **Bees** implement modules against interfaces in parallel
3. **Bees** write tests, ensure module works in isolation
4. **Q33N** integrates modules, runs integration tests
5. **All** code review before merge

## Testing

```bash
# Unit tests (per module)
pytest tests/unit/embeddings -v

# Integration tests
pytest tests/integration -v

# Full test suite
pytest --cov=packages
```

## License

Private - Dave's personal productivity tool
