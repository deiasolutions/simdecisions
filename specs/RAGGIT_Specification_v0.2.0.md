# RAGGIT Specification

**The Global Bazaar for the Third Millennium**

**Version:** 0.2.0-draft
**Date:** 2026-02-01
**Author:** Dave (@justra96it)
**Movement:** We are the 96%

---

## 1. Vision

RAGGIT is an open creator marketplace where anyone can publish, version, license, and monetize structured knowledge collections. It combines GitHub's version control, Patreon's creator monetization, and TikTok's social discovery—for all creatable content types.

**Core thesis:** The 96% create the value. The current system extracts it. RAGGIT reverses the flow.

**The 96 in RA96IT:**
- Mathematical: 96° interior angles of a dodecagon (12-sided harmony)
- Cultural: "We are the 96%" — creators vs. extractive platforms
- Operational: No Billionaires Clause — individual wealth capped at $999M

---

## 2. What is a Ragg?

A **ragg** (or **ra96**) is the atomic unit of RAGGIT: a versioned, licensed, attributed knowledge collection.

| Component | Description |
|-----------|-------------|
| **Content** | RAG collections, prompts, datasets, templates, media, any structured knowledge |
| **Metadata** | Creator attribution, version history, provenance chain |
| **Commerce** | License tier, pricing, access controls |
| **Transport** | ClipEgg-compatible reference for lightweight sharing |

### 2.1 Ragg = Egg + Commerce

RAGGIT extends ClipEgg's reference-first protocol:

| ClipEgg Egg | RAGGIT Ragg Adds |
|-------------|------------------|
| `uri` | `ragg_version` |
| `label` | `license_tier` |
| `type` | `creator_id` |
| `content` (minimal) | `price` |
| `caps` | `provenance` |
| `action` (copy/cut) | `action` (share/show/borrow/rent/subscribe/purchase) |
| hatch protocol | commerce hooks at hatch time |

---

## 3. Commerce Actions

Six verbs define all marketplace interactions:

| Action | Payment | Access Level | Duration |
|--------|---------|--------------|----------|
| **share** | free | reference only | permanent link |
| **show** | free | reference only | link expires |
| **borrow** | free | full content | access expires |
| **rent** | paid | full content | access expires |
| **subscribe** | paid | full content | renews on date |
| **purchase** | paid | full content | permanent |

### 3.1 Action Matrix

|  | Free | Paid |
|--|------|------|
| **Reference only** | share / show | — |
| **Full content, expires** | borrow | rent |
| **Full content, ongoing** | — | subscribe / purchase |

### 3.2 Definitions

**share** — Free, permanent reference link. Recipient sees preview, metadata, hatch point. No full content without further action. *Use case: "check this out" in chat/social.*

**show** — Free, expiring reference link. Same as share but link dies after duration. *Use case: limited-time preview, embargoed content tease.*

**borrow** — Free, full content access with expiration. Creator sets duration. *Use case: library model, try-before-you-buy, educational access.*

**rent** — Paid, full content access with expiration. Creator sets price and duration. *Use case: project-based licensing, short-term needs.*

**subscribe** — Paid, full content access with renewal date. Access continues while subscription active. *Use case: ongoing access to evolving raggs, creator relationship.*

**purchase** — Paid, permanent full content access. One-time transaction, perpetual license. *Use case: own it forever.*

### 3.3 Monetization Ladder

```
share → show → borrow → rent → subscribe → purchase
  │       │       │        │        │          │
  └── free discovery ──────┴── paid conversion ┘
```

Free actions drive discovery and trial. Paid actions drive revenue.

---

## 4. Architecture

### 4.1 Layer Separation

| Layer | Protocol | Responsibility |
|-------|----------|----------------|
| **Transport** | ClipEgg | How eggs move between apps (copy, cut) |
| **Commerce** | RAGGIT | What raggs mean in a marketplace |
| **Trust** | Provenance | Who created what, when, with what sources |

ClipEgg doesn't know about payments, licenses, or attribution. It just moves eggs.

RAGGIT extends eggs into raggs. The hatch endpoint enforces access rights based on action verb.

### 4.2 Reference-First Philosophy

Both ClipEgg and RAGGIT share the same architectural principle: **reference-first, resolve on demand**.

- Minimal payload travels through clipboard/network
- Full content resolves only when needed
- Access rights enforced at hatch time
- Creator retains control until resolution

### 4.3 Provenance Chain

Every ragg carries cryptographic provenance:

| Field | Purpose |
|-------|---------|
| `creator_id` | Verified creator identity |
| `created_at` | Timestamp of original creation |
| `version_history` | Chain of all modifications |
| `source_attribution` | References to upstream content |
| `signature` | C2PA-compatible content authenticity |

This enables:
- Creator attribution that survives remix/fork
- Revenue sharing to upstream sources
- Trust verification without central authority
- Legal defensibility for licensing

---

## 5. User Flows

### 5.1 Creator Flow

1. **Publish** — Upload ragg content, set metadata, choose license tier
2. **Price** — Configure which actions are available at what price points
3. **Version** — Update content, version history preserved
4. **Earn** — Revenue from rent/subscribe/purchase actions
5. **Attribute** — Credit upstream sources, receive credit from downstream

### 5.2 Consumer Flow

1. **Discover** — Browse, search, receive shared links
2. **Preview** — See metadata, preview via share/show
3. **Try** — Full content via borrow (free trial)
4. **Access** — Rent for short-term, subscribe for ongoing, purchase for permanent
5. **Use** — Integrate ragg into own workflows, RAG systems, applications

### 5.3 Platform Flow

1. **Index** — Catalog all published raggs
2. **Match** — Surface relevant content to consumers
3. **Transact** — Process payments, enforce access
4. **Attribute** — Track provenance, distribute revenue
5. **Govern** — Community-driven rules and disputes

---

## 6. Governance

### 6.1 The 96% Principle

RAGGIT exists to serve creators, not extract from them. Governance reflects this:

- **No Billionaires Clause** — Individual wealth from RAGGIT capped at $999M
- **Creator-majority governance** — Platform decisions require creator consent
- **Transparent economics** — All fee structures, revenue splits publicly documented
- **Fork rights** — If governance fails, community can fork the protocol

### 6.2 Governance Tiers (from Ostrom principles)

| Tier | Scope | Threshold |
|------|-------|-----------|
| **Operational** | Day-to-day decisions | Core team |
| **Tactical** | Feature priorities, policies | 60% community vote |
| **Strategic** | Protocol changes, economics | 75% community vote |

### 6.3 Dispute Resolution

- Creator-to-creator: Mediation, then arbitration
- Consumer complaints: Tiered support, refund policies
- Attribution disputes: Provenance chain as evidence

---

## 7. Target Users

### 7.1 Phase 1: Developers
- RAG system builders needing quality collections
- AI prompt engineers sharing/selling prompts
- Dataset creators monetizing curated data

### 7.2 Phase 2: Creators
- DJs licensing sample packs, stems, remixes
- Designers selling templates, assets, systems
- Researchers sharing methodologies, datasets
- Educators packaging curricula, materials

### 7.3 Phase 3: Mainstream
- Writers licensing content for AI training
- Musicians controlling how their work is used
- Any creator with structured knowledge to share

---

## 8. MVP Recommendation

Launch with four verbs:

| Verb | Why |
|------|-----|
| **share** | Core virality — free reference sharing |
| **borrow** | Conversion funnel — free trial of full content |
| **rent** | Low-commitment revenue — paid temporary access |
| **purchase** | High-commitment revenue — paid permanent access |

Add **show** and **subscribe** when use cases demand them.

### 8.1 MVP Technical Scope

1. Ragg publishing with versioning
2. Four commerce actions (share/borrow/rent/purchase)
3. Creator profiles with attribution
4. Basic discovery (search, browse, categories)
5. Payment processing (Stripe or equivalent)
6. ClipEgg integration for transport

### 8.2 MVP Out of Scope

- Advanced provenance chain (Phase 2)
- Governance voting (Phase 2)
- Subscription billing (Phase 2)
- Show with expiration (Phase 2)
- Revenue sharing to upstream sources (Phase 3)

---

## 9. Relationship to ClipEgg

ClipEgg is an open clipboard protocol replacing payload-based copy/paste with lightweight references. RAGGIT adopts ClipEgg as a **component, not a dependency**.

### 9.1 Why ClipEgg Matters

- Same architectural philosophy: reference-first, resolve on demand
- Transport already solved — no need to reinvent clipboard handling
- Minimal egg travels through clipboard, hatching resolves to preview or gated content

### 9.2 No Changes Needed to ClipEgg

ClipEgg is correctly scoped as transport layer. RAGGIT's commerce verbs live in the ragg extension. The only clarification already applied: "cut" is destructive move, not purchase or license transfer.

---

## 10. Relationship to DEIA

DEIA (Distributed Expertise and Intelligence Augmentation) provides infrastructure that RAGGIT can leverage:

| DEIA Component | RAGGIT Application |
|----------------|-------------------|
| **LIMB** (Local Intelligence) | Edge-based ragg resolution, privacy-first access |
| **BOK** (Book of Knowledge) | Commons-owned knowledge graph as ragg source |
| **Provenance (C2PA)** | Content authenticity for attribution chain |
| **Trust scoring** | Creator reputation, consumer verification |
| **DEIA Clock** | Coordinated versioning across distributed raggs |

RAGGIT can operate independently, but DEIA infrastructure amplifies its capabilities.

---

## 11. Assets

| Asset | Value |
|-------|-------|
| **Domains** | ra96it.com, ra96it.app |
| **Social** | @justra96it (RAGGIT), @ra96it (broader brand) |
| **Movement** | "We are the 96%" |
| **Protocol** | ClipEgg (open, public good) |

---

## 12. Open Questions

1. **Open standard vs. business** — Is RAGGIT a protocol anyone can implement, or a platform with a specific implementation?
2. **Payment rails** — Crypto, fiat, or both? What's the fee structure?
3. **AI licensing** — How do raggs interact with AI training rights?
4. **Coalition building** — Which smaller platforms could adopt the standard?
5. **International** — How does commerce work across jurisdictions?

---

## 13. Next Steps

1. Finalize commerce verb definitions
2. Draft ragg schema (JSON/YAML)
3. Prototype hatch endpoint with access control
4. Build creator onboarding flow
5. Identify launch creators for Phase 1

---

*Part of the RA96IT ecosystem.*
*ClipEgg: Open protocol for the public good.*
*RAGGIT: The Global Bazaar for the Third Millennium.*
