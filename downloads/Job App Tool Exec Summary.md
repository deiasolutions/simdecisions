# Job Application Tracker - Executive Summary

## Business Case

### Current State

Dave manually processes 5-10 job applications per weekday:
- **Time per application**: 30-60 minutes (JD review, resume tailoring, cover letter, submission)
- **Weekly time investment**: 12-25 hours
- **Pain points**:
  - Repetitive customization work
  - Inconsistent quality across applications
  - No systematic tracking of what works
  - Manual follow-up management
  - No visibility into market trends

### Target State

Automated pipeline reduces time-per-application to 10-15 minutes:
- **JD parsing**: Automated extraction (2 min review vs. 10 min manual)
- **Experience matching**: Semantic AI suggests best-fit content (instant vs. 15 min searching)
- **Resume generation**: LLM drafts with SOP compliance (5 min review vs. 20 min writing)
- **Cover letter**: LLM drafts personalized letter (3 min review vs. 15 min writing)
- **Tracking**: Automatic status management, follow-up reminders

### Expected Outcomes

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Time per application | 45 min avg | 12 min avg | **73% reduction** |
| Weekly time | 18 hrs | 5 hrs | **13 hrs saved/week** |
| Application quality | Inconsistent | Standardized | Fewer rejections |
| Follow-up compliance | ~50% | ~95% | More responses |
| Market intelligence | None | Real-time trends | Better targeting |

---

## MVP Scope

### Must Have (v1.0)

**Core Workflow**
1. JD input (URL scrape or paste) with comprehensive field extraction
2. **Role page as central hub** (single source of truth for each opportunity)
3. **Versioned Job Descriptions** linked to roles
4. Semantic similarity matching (Voyage embeddings) for experience-to-JD alignment
5. JD corpus tracking with skill frequency analytics
6. Resume template recommendation (top 2 ranked, user selects)
7. LLM customization with resume SOP enforcement
8. Second opinion (configurable LLM provider pairs, A/B prompt testing)
9. **Human-in-the-loop review UI** with diff view and editable fields
10. **SOP auto-compliance helpers** (live counters, auto-trim/expand)
11. Cover letter generation (same dual-opinion flow)
12. ATS validation + character count checks
13. Export docx + PDF to organized filesystem with **provenance logging**

**Infrastructure**
14. **Background job system** for long-running work (scraping, LLM calls, PDF generation)
15. **Site Intelligence Layer** for scraping heuristics and learning
16. Token and cost tracking per generation
17. LLM quality logging for A/B analysis

**Tracking & Analytics**
18. Application CRUD with status management
19. Response rate analytics by resume version
20. Outcome funnel visualization
21. Salary range tracking

### Deferred (v2.0+)

- **Follow-up reminders** (requires calendar/email integration)
- Interview prep module (question generation, STAR story matcher)
- Company research aggregator
- LinkedIn integration
- Email/calendar integration for interviews
- Mobile app
- External notifications

---

## Technical Architecture

### Entity Model

```
Role (anchor entity - company + title + location)
│
├── JobDescription v1
├── JobDescription v2 (current) ──────────┐
│                                         │
├── ResumeGeneration                      │
│   ├── linked to JD version ─────────────┘
│   ├── linked to template
│   ├── provenance (exact reproduction)
│   └── CoverLetterGeneration
│
└── Application
    ├── resume_generation_id
    └── applied tracking
```

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Job Board     │     │   JD Parser     │     │   PostgreSQL    │
│   (LinkedIn,    │────▶│   + Site Intel  │────▶│   + pgvector    │
│   Indeed, etc.) │     │   (learns!)     │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Experiences   │────▶│    Voyage AI    │────▶│   Embeddings    │
│   JSON          │     │   (Embedding)   │     │   (pgvector)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Resume SOP     │────▶│  Anthropic /    │────▶│   Customized    │
│  Rules          │     │  OpenAI LLM     │     │   Content       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Background     │────▶│   docx-js +     │────▶│   /postings/    │
│  Job Worker     │     │   LibreOffice   │     │   filesystem    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Tech Stack Summary

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | React + TypeScript | SPA with Role hub as central view |
| Backend | FastAPI + Python 3.13 | Async, type-safe API |
| Database | PostgreSQL 15 + pgvector | Relational + vector search |
| Embeddings | Voyage AI | High-quality semantic matching |
| LLM Primary | Anthropic Claude | Resume/cover letter generation |
| LLM Secondary | OpenAI GPT-4o | Second opinion, A/B testing |
| Documents | docx-js + LibreOffice | Professional formatting |
| Background Jobs | Custom queue (PostgreSQL) | Long-running work |

### Scale Expectations

| Metric | Year 1 Estimate | pgvector Capacity |
|--------|-----------------|-------------------|
| Applications | ~2,000 | ✓ Trivial |
| JD embeddings | ~30,000 | ✓ Easy |
| Experience embeddings | ~200 | ✓ Trivial |
| Total vectors | ~30,200 | ✓ <1% of limit |

---

## Cost Estimates

### LLM Costs (per application)

| Step | Provider | Est. Tokens | Est. Cost |
|------|----------|-------------|-----------|
| JD extraction | Claude | 2K in, 1K out | $0.02 |
| Resume primary | Claude | 4K in, 2K out | $0.04 |
| Resume secondary | GPT-4o | 4K in, 2K out | $0.03 |
| Cover primary | Claude | 3K in, 1K out | $0.03 |
| Cover secondary | GPT-4o | 3K in, 1K out | $0.02 |
| **Total per app** | | | **~$0.14** |

### Monthly Costs (assuming 150 apps/month)

| Service | Cost |
|---------|------|
| LLM (Anthropic + OpenAI) | ~$21 |
| Voyage embeddings | ~$2 |
| PostgreSQL (local) | $0 |
| **Total** | **~$23/month** |

---

## HiveMind Development Plan

### Team Structure

- **Q33N (Dave)**: Architecture, integration, code review
- **Bee 1**: Database layer, LLM service, background job worker
- **Bee 2**: Embeddings, JD parser, site intelligence, corpus analytics
- **Bee 3**: Resume engine, document generator, SOP validation
- **Bee 4**: Frontend (if parallelizing UI)

### Phase 1: Foundation (Week 1)

| Task | Owner | Deliverable |
|------|-------|-------------|
| Project scaffolding | Q33N | Monorepo structure, CI setup |
| Schema design | Q33N | Pydantic models, TypeScript types |
| Database setup | Bee 1 | Models, migrations, pgvector |
| Background job queue | Bee 1 | Queue, worker, handlers skeleton |
| Voyage integration | Bee 2 | Embedding client, indexer |

### Phase 2: Core Pipeline (Week 2)

| Task | Owner | Deliverable |
|------|-------|-------------|
| Site intelligence | Bee 2 | Learning layer for job boards |
| JD scraping | Bee 2 | URL→text with site adapters |
| JD field extraction | Bee 2 | LLM-powered parsing |
| Experience indexing | Bee 2 | Embed Dave's JSON |
| Semantic matcher | Bee 2 | Ranked experience matches |
| LLM service | Bee 1 | Multi-provider, cost tracking |

### Phase 3: Generation (Week 3)

| Task | Owner | Deliverable |
|------|-------|-------------|
| Template management | Bee 3 | Import existing resumes |
| Resume customizer | Bee 3 | LLM + SOP enforcement |
| SOP validator | Bee 3 | ATS + char count + auto-fix |
| docx builder | Bee 3 | Formatted output |
| PDF converter | Bee 3 | LibreOffice integration |
| Provenance logging | Bee 1 | Full reproducibility |

### Phase 4: Tracking & UI (Week 4)

| Task | Owner | Deliverable |
|------|-------|-------------|
| API orchestration | Q33N | Full workflow endpoints |
| Role hub page | Bee 4 | Central entity view |
| Resume review UI | Bee 4 | Diff view, editable fields |
| Tracker CRUD | Bee 1 | Application management |
| Analytics queries | Bee 1 | Funnel, response rates |
| Corpus analytics | Bee 2 | Skill frequency trends |

### Phase 5: Polish (Week 5)

| Task | Owner | Deliverable |
|------|-------|-------------|
| Integration testing | All | End-to-end flows |
| Bug fixes | All | Stability |
| Documentation | Q33N | User guide |
| A/B testing setup | Bee 1 | Prompt versioning |
| Site intelligence tuning | Bee 2 | Per-site adapters |

---

## Success Metrics

### Efficiency

- [ ] Time per application < 15 minutes average
- [ ] Resume generation < 60 seconds
- [ ] Cover letter generation < 30 seconds

### Quality

- [ ] ATS validation pass rate > 99%
- [ ] Character count compliance 100%
- [ ] User approval rate > 80% (minimal edits needed)

### Tracking

- [ ] 100% of applications tracked
- [ ] Follow-up reminder compliance > 90%
- [ ] Response rate visibility by template version

### Cost

- [ ] LLM cost per application < $0.20
- [ ] Monthly total < $50

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Job board scraping blocked | Manual paste fallback, respect robots.txt |
| LLM quality variance | A/B testing, human review step |
| Embedding quality | Voyage known for quality; can swap if needed |
| Scope creep | Clear MVP definition, defer v2 features |
| SOP compliance drift | Automated validation, test suite |

---

## Next Steps

1. **Q33N**: Finalize SPECS.md, create GitHub repo, set up CI
2. **Q33N**: Define interface contracts in `packages/common/`
3. **Bees**: Clone repo, review specs, begin module implementation
4. **Daily**: Async standups in project chat
5. **Weekly**: Integration checkpoint, demo progress
