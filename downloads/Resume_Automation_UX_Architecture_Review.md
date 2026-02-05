# Resume Application Automation – UX & Architecture Review (Revised)

## Scope Clarifications (Incorporating New Notes)

- **Primary entities**
  - **Role / Job**: A canonical role entity (company + title + location).
  - **Job Description (JD)**: The parsed description text associated with a role; may have multiple versions over time.
- **Login to job page**
  - The system should support *authenticated access* to job postings where required.
  - Store credentials securely (OS keychain / env secrets) and tag JDs as:
    - `public`
    - `authenticated`
    - `manual-paste`
- **Learning from each site**
  - Introduce a **Site Intelligence Layer**:
    - Track patterns per job board (HTML structure, auth needs, blocking behavior).
    - Persist extraction success/failure metadata.
    - Gradually build heuristics for “what to expect” per site (fields reliably available, quirks, limits).
- **Follow‑up reminders**
  - Explicitly deferred to **future version** (out of MVP scope).

---

## UX Evaluation

### What Works Well
- Clear end‑to‑end flow: JD → Match → Generate → Validate → Export.
- Strong SOP‑driven guardrails improve resume consistency and ATS compatibility.
- Explicit “second opinion” LLM step is a quality differentiator.

### UX Gaps & Fixes
1. **Job Page as a Hub**
   - Each role/job page should act as a *single source of truth*:
     - Raw JD
     - Parsed fields
     - Site metadata (source, auth, scrape notes)
     - Generated resumes & versions
     - Validation results
   - This aligns with your need to “log in to the job page” conceptually and operationally.

2. **Human‑in‑the‑Loop Review Screen**
   Add a first‑class review UI showing:
   - Extracted JD fields (editable).
   - Matched experiences *with rationale*.
   - Proposed resume diffs (before/after).
   - SOP violations + one‑click “make compliant” fixes.
   - Deterministic export action.

3. **SOP Friction Management**
   - Live bullet counters.
   - Auto‑trim / auto‑expand helpers.
   - Bounded retry loop (“iterate until compliant or fail clearly”).

---

## Architecture & Logic Review

### What’s Solid
- FastAPI backend + relational DB + embeddings store.
- Prompt/version logging and cost tracking.
- Clear separation between extraction, generation, validation.

### Key Logic Adjustment (Refined)
- Keep **Role/Job** as the anchor entity.
- Treat **Job Descriptions** as versioned artifacts linked to the role.
- Resume generations attach to *(role, JD version, resume version)*.
- This avoids state confusion while preserving your conceptual model.

### Long‑Running Work
- Generation, scraping, embeddings, and document rendering should run as **background jobs**:
  - Job table with states (`queued → running → completed → failed`).
  - Progress polling or lightweight events.
  - Clear UX on partial failure.

---

## Site Intelligence Layer (New)

Add a lightweight learning system per job site:
- Fields:
  - `site_name`
  - `auth_required`
  - `scrape_success_rate`
  - `known_blocks`
  - `preferred_extraction_method`
- Benefits:
  - Better defaults for new JDs.
  - Faster failure detection.
  - Gradual improvement without hard‑coding per site.

---

## Scraping Reality Check

- MVP stack (`requests` + `BeautifulSoup`) is fine *with guardrails*.
- Required additions:
  - Per‑site adapters.
  - Exponential backoff + clear failure states.
  - Explicit “paste JD text” fallback UX.
  - Visibility into *why* a scrape failed.

---

## Document Generation Contract

- Define a strict JSON → DOCX/PDF contract:
  - Deterministic file naming.
  - Explicit schema for sections and bullets.
  - OS‑aware path handling (Windows first‑class).
- Avoid hidden coupling between Node and Python steps.

---

## Provenance & Reproducibility

Upgrade logging to support:
- Exact prompt version.
- Model + parameters.
- Inputs, outputs, validator results.
- Ability to “re‑run this exact resume” later.

This supports debugging, learning, and trust.

---

## Explicit MVP Additions (Summary)

1. Job/Role page as central UX hub.
2. Versioned Job Description model.
3. Background job system with progress.
4. Review + diff UI.
5. SOP auto‑compliance helpers.
6. Site intelligence learning layer.
7. Deterministic export & provenance.

---

## Deferred to Future Versions

- Follow‑up reminders & calendar/email integrations.
- External notifications.
- Deep analytics dashboards.

---

*This revision integrates user notes and preserves the original architectural intent while tightening UX, logic boundaries, and operational resilience.*
