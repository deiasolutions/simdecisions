# RAGGIT PROJECT CONTEXT DUMP
## All Ideas, Decisions, and Archived Concepts

**Last Updated:** November 20, 2025  
**Status:** Early-stage product development, pre-code  
**Purpose:** Complete context capture for new Claude instances

---

## CORE VISION (KEPT)

- Platform name: **RAGGIT**
- Tagline: "Global Bazaar for the Third Millennium"
- Positioning: **GitHub + Patreon + TikTok for all creatable content**
- Market positioning: "GitHub for RAGs" - first mover advantage
- Target valuation: **$100B IPO in 3 years**
- Movement: **"We are the 96%"** (wealth redistribution through creator economy)

---

## BUSINESS MODEL (KEPT)

- **30% platform take rate**
- **70% to creators**
- Revenue streams:
  - Transaction fees on RAG sales
  - Subscription revenue split
  - API usage fees (future)
- Payout frequency: Monthly via Stripe
- No freemium model discussed yet - TBD

---

## DOMAINS & HANDLES (KEPT)

### Domains Registered/Available:
- **ra96it.com** (kept)
- **ra96it.app** (kept)
- ra96.com (available, not purchased yet)
- ra-96.com (available, not purchased yet)

### Social Media:
- Primary handle: **@ra96it** (cross-platform)
- Previously considered: @justra96it (archived)
- Previously considered: @ra86 variants (archived - typo correction)

### Domain Strategy:
- .IT domains NOT available (raggit.it, rag96.it checked - all taken)
- .COM considered better for global platform anyway
- Decision: Stick with ra96it branding across web + social

---

## COMPETITOR RESEARCH (COMPLETED)

### Findings:
- **No direct "GitHub for RAGs" competitor exists** - blue ocean
- Related platforms found:
  - Galileo (RAG development platform)
  - Orq.ai (collaborative RAG tools)
  - ChatBees (serverless RAG APIs)
  - RAGFlow (open-source RAG engine)
  - VersionRAG (research project on version-aware retrieval)
- None offer marketplace + version control + monetization combined
- **Market gap validated**

---

## TECHNICAL INFRASTRUCTURE (DECISIONS MADE)

### Hosting:
- **Cloudflare Pages** for hosting
- **Cloudflare DNS** management
- SSL/TLS: Full (strict) mode
- CDN: Cloudflare global network

### Deployment:
- Connect via GitHub
- Auto-deploy on push
- Framework: Next.js (assumed, not explicitly stated)
- Build output: Static export

### GitHub Repo:
- Current name: **ra96-url-shortener** (needs renaming to RAGGIT)
- Repo exists but empty/minimal
- Needs restructuring for full platform

---

## MVP FEATURE SCOPE (HIGH-LEVEL IDEAS)

### Creator Features (Kept):
- RAG collection creation (upload docs, URLs, text)
- Auto-chunking and embedding
- Version control system (v1.0, v1.1, etc.)
- Creator profiles with portfolios
- Earnings dashboard
- Set pricing (free, one-time, subscription)
- License selection (MIT, CC, Commercial)
- Fork/collaboration tools
- Co-creator attribution

### Consumer Features (Kept):
- Marketplace browse and search
- RAG collection preview/demo
- One-click purchase
- Subscription management
- API key generation for access
- REST API integration
- Python SDK (future)

### Platform Features (Kept):
- Stripe payment processing
- OAuth2 authentication
- API key management
- Rate limiting
- Analytics dashboards
- Usage tracking

---

## DEFERRED/OUT OF SCOPE FOR V1.0 (ARCHIVED FOR LATER)

- Mobile apps (web-first approach)
- Video content RAGs
- Real-time collaboration
- Advanced analytics
- White-label solutions
- Enterprise SSO
- Custom licensing agreements
- In-platform RAG builder (use external tools initially)
- Reviews/ratings system (maybe v1.1)

---

## BRAND IDENTITY (CONCEPTUAL - NOT FINALIZED)

### Logo Direction (Ideas):
- Combine visual elements: network/graph, marketplace, version control branching, global/world
- Typography: Bold, modern, tech-forward geometric sans-serif
- Should feel: Trustworthy, innovative, accessible
- Need variations: full lockup, icon only, monochrome, small format

### Color Palette (Proposed):
- Primary: #2D5BFF (vibrant blue)
- Secondary: #FF6B35 (coral orange)
- Accent: #00D9A3 (mint green)
- Neutrals: #0F1419 to #FFFFFF range

### Voice & Tone (Kept):
- Empowering, inclusive, technical, bold, accessible
- Direct and clear writing
- Active voice, short sentences
- Conversational but professional
- Key phrase: "Keep 70% of what you earn"

---

## USER FLOWS (CONCEPTUAL)

### Creator Onboarding:
Sign up → Verify email → Complete profile → Create first RAG → Set pricing → Publish → Share

### Consumer Purchase:
Browse → Preview → Add to cart → Checkout → Get API key → Integrate → Query RAG

### Collaboration:
Find RAG → Fork → Make improvements → Submit for merge → Review → Merge/decline → Update attribution

---

## DATABASE SCHEMA (STARTED, NOT COMPLETED)

### Core Entities Identified:
- Users table (with creator/consumer flags)
- RAG Collections table
- Versions table (for RAG versioning)
- Transactions table (purchases, subscriptions)
- API Keys table
- Follows table (social graph)
- Forks table (collaboration tracking)
- Reviews table (future)

### Key Fields Noted:
- Users: UUID, username, email, stripe_account_id, total_earnings, follower_count
- Collections: pricing, license type, version info, creator attribution
- Transactions: 30/70 split tracking, platform fees

**Note:** Schema was started in handoff doc but got cut off - needs completion

---

## GO-TO-MARKET STRATEGY (HIGH-LEVEL)

### Success Metrics Proposed:
**Phase 1 (0-6 months):**
- 10K creator accounts
- 1K published RAG collections
- $100K monthly GMV

**Phase 2 (6-12 months):**
- 100K creator accounts
- 50K published RAG collections
- $10M monthly GMV

**Phase 3 (12-24 months):**
- 1M+ creator accounts
- 500K+ published RAG collections
- $100M monthly GMV

### North Star Metrics:
- Monthly Active Creators (MAC)
- RAG Collections Published
- Gross Merchandise Value (GMV)
- Creator Earnings (70% of GMV)

---

## TECHNICAL ARCHITECTURE (NOT YET DESIGNED)

### Components Needed (Identified but not detailed):
- Frontend web app
- Backend API
- RAG processing pipeline
- Vector database for embeddings
- Payment processing integration
- Authentication system
- API gateway for consumer access
- Analytics pipeline

### Integrations Required:
- Stripe (payments)
- OAuth providers (Google, GitHub, etc.)
- Vector DB (Pinecone, Weaviate, or similar - TBD)
- Embedding models (OpenAI, Cohere, or open-source - TBD)
- CDN/hosting (Cloudflare decided)

---

## MESSAGING & POSITIONING (KEPT)

### Key Messages:
1. "GitHub for everything that isn't code"
2. "Version control for knowledge"
3. "Turn your expertise into revenue"
4. "Join the 96% building the new economy"
5. "The first marketplace for RAG collections"

### Target Audiences:
- **Creators:** Knowledge workers, consultants, educators, researchers, domain experts
- **Consumers:** Developers, businesses, AI teams, researchers needing specialized knowledge
- **Movement participants:** People who believe in wealth redistribution via creator economy

---

## DEVELOPMENT APPROACH (CURRENT PHASE)

### Where We Are:
- ✅ Vision defined
- ✅ Business model set
- ✅ Domains secured
- ✅ Social handles claimed
- ✅ Competitor research done
- ✅ GitHub repo created
- ❌ Detailed specs NOT written
- ❌ Architecture NOT designed
- ❌ Wireframes NOT created
- ❌ Database schema NOT finalized
- ❌ Code NOT started

### Next Steps:
1. Create comprehensive handoff doc for Claude Code
2. Claude Code expands vision into detailed specs
3. Claude Code designs architecture
4. Claude Code creates wireframes/designs
5. Claude Code proposes database schema
6. Claude Code writes technical documentation
7. THEN start coding

### Bot Strategy:
- Use Claude Code DEIA platform (PM bot + Codex bot + 3 dev bots)
- PM bot coordinates overall product strategy
- Codex bot handles documentation and specs
- Dev bots execute implementation
- All bots need context from this project's conversations

---

## OPEN QUESTIONS & DECISIONS NEEDED

- Which vector database to use?
- Which embedding model(s) to support?
- Pricing tiers for creators (free tier? limits?)
- API rate limits and pricing
- Launch timeline (target date?)
- Initial creator seeding strategy
- Marketing/growth strategy details
- Legal entity structure
- Terms of service details
- Privacy policy requirements
- International expansion plan
- Localization priority (English-first, then what?)

---

## ARCHIVED IDEAS (NOT PURSUING NOW)

- @justra96it as social handle (chose @ra96it instead)
- .IT domain extensions (not available)
- @ra86 variants (typo, corrected to ra96)
- In-platform RAG builder for v1.0 (deferred)
- Mobile apps for v1.0 (web-first)
- Real-time collaboration for v1.0 (deferred)
- Video RAGs for v1.0 (deferred)

---

## CRITICAL CONTEXT FOR NEW CLAUDE INSTANCES

1. **Read ALL past conversations in this project** - use conversation_search and recent_chats tools
2. **This is pre-code phase** - focus on design, specs, architecture first
3. **Vision is ambitious** - $100B IPO, global movement, first-mover advantage
4. **Business model is set** - 30/70 split, don't change without explicit approval
5. **Brand identity is flexible** - colors and logo concepts are proposals, not final
6. **User wants collaboration** - expect iterative discussions, not one-shot answers
7. **Claude Code is the execution platform** - handoff doc needs to be comprehensive for bots
8. **Movement matters** - "We are the 96%" is core to mission, not just marketing

---

## FILE STRUCTURE (CURRENT STATE)

```
GitHub Repo: ra96-url-shortener (needs renaming)
├── (mostly empty, needs structure)
└── (handoff doc will go here)

Domains:
├── ra96it.com (registered)
├── ra96it.app (registered)
├── ra96.com (available)
└── ra-96.com (available)

Social:
└── @ra96it (across platforms)
```

---

## USAGE INSTRUCTIONS FOR THIS DOCUMENT

**For new Claude instance:**
1. Read this entire document first
2. Read all past conversations in project using tools
3. Synthesize into comprehensive understanding
4. Ask clarifying questions if needed
5. Create handoff document for Claude Code
6. Focus on expanding vision into actionable specs
7. Remember: design phase, not implementation phase yet

**For human (project owner):**
- Update this doc as decisions are made
- Archive old ideas but keep them documented
- Add new open questions as they arise
- Mark items as KEPT/ARCHIVED/TBD clearly
- Keep this as single source of truth for context dumps
