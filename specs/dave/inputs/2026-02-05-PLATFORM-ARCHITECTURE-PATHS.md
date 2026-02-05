# Platform Architecture Paths

**From:** Q33N (Dave)
**Date:** 2026-02-05
**Type:** Raw architectural input
**Status:** CAPTURE — needs refinement into ADR

---

## The Insight

> Treat this as "your Discord, but API-first" — Slack/Discord feature shape, Matrix architecture vibe — with auth, roles, auditability, and an SDK-able API from day 1.

---

## Tag Taxonomy (First-Class Objects)

```
#idea    — Raw thoughts, brainstorms
#note    — Reference information
#todo    — Actionable items
#ask     — Questions needing answers
#prep    — Pre-work, setup
#draft   — Work in progress
#review  — Awaiting review
#log     — Activity record
#log idea    — Logged insight
#log win     — Logged success
#log blocker — Logged obstacle
#tags    — Meta: about tagging itself
```

---

## Three Architecture Paths

### Path 1: Supabase Lane (Fastest Credible)

**Philosophy:** Build your UI, outsource the hard parts.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Web App     │────▶│ FastAPI/    │────▶│ Supabase    │
│ (Next.js)   │     │ Node API    │     │ (Postgres + │
└─────────────┘     └─────────────┘     │  RLS + Auth │
       │                   │            │  + Realtime)│
       │                   │            └─────────────┘
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Bot SDK     │     │ Mobile App  │
│ (Python)    │     │ (later)     │
└─────────────┘     └─────────────┘
```

**Pros:**
- Ship login/accounts/read-write quickly
- Enterprise-ish security primitives built-in
- Row Level Security for multi-tenant
- Realtime subscriptions included

**Cons:**
- Vendor lock-in
- Less control over auth flows
- May outgrow it

---

### Path 2: Keycloak Lane (Most "Yours")

**Philosophy:** Cleanly separate "who are you?" from "what can you do?"

```
┌─────────────┐
│ Keycloak    │◀── OIDC/OAuth2, MFA, SSO
│ (Identity)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ API Gateway │────▶│ Services    │
│             │     │ (REST/GQL)  │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ Postgres │ │ Redis    │ │ WebSocket│
       └──────────┘ └──────────┘ └──────────┘
```

**Pros:**
- Full control
- Clean separation of concerns
- Enterprise SSO-ready
- No vendor lock-in

**Cons:**
- More to build and maintain
- Keycloak has learning curve
- Slower to first working version

---

### Path 3: Matrix Lane (Protocol-First)

**Philosophy:** Future-proof comms, federation options.

```
┌─────────────────────────────────────────────┐
│ Matrix Homeserver (Synapse/Dendrite)        │
│ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │
│ │ Rooms   │ │ E2EE    │ │ Federation      │ │
│ │ (chats) │ │ (later) │ │ (optional)      │ │
│ └─────────┘ └─────────┘ └─────────────────┘ │
└──────────────────┬──────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌────────┐   ┌──────────┐   ┌──────────────┐
│ Custom │   │ DEIA     │   │ Moderation   │
│ Client │   │ Services │   │ Overlay      │
└────────┘   └──────────┘   └──────────────┘
```

**Pros:**
- Protocol-first (not platform-locked)
- Federation options later
- E2EE possible
- Rich existing ecosystem

**Cons:**
- Matrix complexity
- Homeserver ops
- Custom UX still needed

---

## Security Features (Minimum Viable Trust) — v1

| Category | Features |
|----------|----------|
| **Authentication** | OAuth2/OIDC login, MFA option, email verification, passwordless optional |
| **Authorization** | RBAC/ABAC permissions, scoped API keys for bots, clear tenant model (per org/workspace) |
| **Rate Limiting** | Per-user, per-bot, per-endpoint |
| **Audit** | Immutable-ish audit log |
| **Encryption** | In transit (TLS), at rest |
| **Secrets** | Secrets management (not in code) |

---

## DEIA Special Sauce (What Makes It Not "Just Chat")

| Feature | Description |
|---------|-------------|
| **Work Queues** | First-class objects with claims/releases, state machine |
| **Moderator Workflows** | Human-in-the-loop approval flows |
| **Bot-to-Bot Messaging** | With quotas and circuit-breakers |
| **Event Streaming** | Webhooks so agents react without polling |

These are the differentiators. Any path must support these natively or via extension.

---

## Decision Factors

| Factor | Supabase | Keycloak | Matrix |
|--------|----------|----------|--------|
| Time to first login | Days | Weeks | Days (if using existing client) |
| Time to custom UX | Days | Days | Weeks |
| Control over auth | Medium | High | Medium |
| Federation/interop | No | No | Yes |
| Bot SDK friendliness | High | High | Medium |
| Vendor lock-in risk | Medium | Low | Low |
| Ops complexity | Low | High | High |

---

## Questions to Resolve

1. **Do we need federation?** (Matrix wins if yes)
2. **Is enterprise SSO a near-term requirement?** (Keycloak wins if yes)
3. **How fast do we need first working version?** (Supabase wins if "now")
4. **Will we outgrow Supabase?** (Probably yes, but migration is possible)
5. **Do we have ops capacity for Keycloak/Matrix?** (Honest assessment needed)

---

## Recommended Path (BEE-001 Opinion)

**Start with Supabase, design for portability.**

1. Use Supabase Auth + RLS + Realtime for v1
2. Keep business logic in your API layer (not Supabase functions)
3. Design data model to be Postgres-portable
4. Build bot SDK against your API, not Supabase directly
5. Plan migration triggers (user count, feature needs, cost)

This gives fastest path to working product while keeping options open.

---

## Next Steps

1. Refine into ADR-006 (Platform Architecture Decision)
2. Spike: Supabase project with auth + one table + RLS
3. Define work queue schema
4. Design bot API contract

---

*Raw capture from Q33N. Needs refinement.*
