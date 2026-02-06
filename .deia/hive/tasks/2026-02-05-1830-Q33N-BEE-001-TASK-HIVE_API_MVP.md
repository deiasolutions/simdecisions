# Task: Scaffold Hive Control Plane API (MVP)

**ID:** TASK-HIVE_API_MVP
**Assigned To:** BEE-001
**Issued By:** Q33N
**Date:** 2026-02-05
**Priority:** HIGH

---

## 1. Objective

Scaffold and deploy a minimal Hive Control Plane API on Railway, implementing the core endpoints from ADR-006. This is the foundation for all coordination — tribunal, dashboard, bee communication.

---

## 2. Context

- **Spec:** `specs/ADR-006-Hive-Control-Plane.md`
- **Frontend:** `frontend/` (Next.js scaffolded, ready for API integration)
- **Infrastructure:** Railway (backend) + Vercel (frontend)

---

## 3. Deliverables

### 3.1 Project Structure

Create `backend/` directory:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # Postgres connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task model
│   │   ├── message.py       # Message model
│   │   └── audit.py         # Audit log model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task endpoints
│   │   ├── tribunal.py      # Tribunal endpoints
│   │   └── health.py        # Health check
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   └── websocket.py         # WebSocket handler
├── alembic/                  # Database migrations
├── tests/
│   └── test_tasks.py
├── requirements.txt
├── Dockerfile
├── railway.toml
└── README.md
```

### 3.2 API Endpoints (MVP)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/tasks` | List tasks (filterable by status) |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get task details |
| POST | `/api/v1/tasks/{id}/claim` | Claim task (requires bee API key) |
| POST | `/api/v1/tasks/{id}/progress` | Log progress |
| POST | `/api/v1/tasks/{id}/complete` | Mark complete |
| POST | `/api/v1/tasks/{id}/release` | Release claim |
| GET | `/api/v1/tribunal/pending` | List PRs awaiting review |
| POST | `/api/v1/tribunal/verdict` | Submit tribunal verdict |
| WS | `/ws` | WebSocket for real-time updates |

### 3.3 Database Schema

Per ADR-006, create tables:

```sql
-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    task_ref VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_to VARCHAR(50),
    claimed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    outcome VARCHAR(20),
    created_by VARCHAR(50) NOT NULL,
    priority INT DEFAULT 0,
    tags VARCHAR[] DEFAULT '{}',
    workspace_id VARCHAR(50) DEFAULT 'default'
);

-- Audit log (append-only)
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    details JSONB NOT NULL
);

-- Append-only triggers
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_update_audit
BEFORE UPDATE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

CREATE TRIGGER prevent_delete_audit
BEFORE DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
```

### 3.4 Authentication

- API keys for bees (header: `Authorization: Bearer <key>`)
- Store hashed keys in database
- Scoped by bee ID
- For MVP: hardcode one admin key in env var, implement proper key management later

### 3.5 Configuration

Environment variables:

```
DATABASE_URL=postgresql://...
API_ADMIN_KEY=<generated>
CORS_ORIGINS=http://localhost:3000,https://simdecisions.vercel.app
LOG_LEVEL=INFO
```

---

## 4. Action Plan

### Step 1: Create project structure
```bash
mkdir -p backend/app/{models,routers,services}
mkdir -p backend/{alembic,tests}
```

### Step 2: Create requirements.txt
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose>=3.3.0
passlib>=1.7.4
websockets>=12.0
httpx>=0.26.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
```

### Step 3: Implement core files
- `main.py` - FastAPI app with CORS, routers
- `config.py` - Settings from env vars
- `database.py` - SQLAlchemy async setup
- `models/task.py` - Task SQLAlchemy model
- `routers/tasks.py` - CRUD endpoints
- `routers/health.py` - Health check

### Step 4: Create Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 5: Create railway.toml
```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
```

### Step 6: Deploy to Railway
- Create Railway project
- Add Postgres plugin
- Set environment variables
- Deploy

### Step 7: Test endpoints
- Health check
- Create task
- List tasks
- Claim/complete flow

---

## 5. Success Criteria

| Criterion | Verification |
|-----------|--------------|
| API deployed on Railway | URL accessible |
| Health endpoint returns 200 | `curl /health` |
| Can create task via API | POST returns 201 |
| Can list tasks | GET returns array |
| Can claim/complete task | State machine works |
| WebSocket connects | Client receives events |
| Database persists | Data survives restart |

---

## 6. Out of Scope (For Later)

- Full tribunal integration (just stubs for now)
- File sync worker
- LLM conflict resolution
- Discord/G-Drive webhooks
- API key management UI

---

## 7. Reporting

Upon completion, create response file:
`.deia/hive/responses/YYYY-MM-DD-HHMM-BEE-001-Q33N-RESPONSE-HIVE_API_MVP.md`

Include:
- Railway deployment URL
- API documentation link (FastAPI auto-generates)
- Any deviations from spec
- Blockers or issues encountered

---

## 8. References

- `specs/ADR-006-Hive-Control-Plane.md`
- `specs/SPEC-Tribunal-SDK.md` (API contract)
- `specs/SPEC-Tribunal-Onboarding.md` (endpoint usage)

---

*Task issued by Q33N. Priority: HIGH. This unblocks dashboard, tribunal, and bee coordination.*
