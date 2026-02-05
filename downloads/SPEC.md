# ClipEgg Specification

**Version:** 0.2.1-draft  
**Status:** Draft  
**Author:** Dave @daaaave-atx  
**Date:** November 2025  
**Repository:** https://github.com/daaaave-ATX/clipe96  
**Policy:** Open Specification (CC BY 4.0)

---

## Abstract

ClipEgg defines a reference-based clipboard protocol for web applications. Instead of copying data payloads to the system clipboard, ClipEgg copies minimal structured references ("eggs") that can be resolved on demand by authorized recipients.

**Critically:** An egg contains NO inline data payloads and NO executable code. It's pure reference metadata.

---

## 1. What is a ClipEgg?

A **ClipEgg** (or simply "egg") is a lightweight, minimal reference that points to content rather than containing it. Think of it as a **claim ticket** that tells you:

1. What you're referencing (URI, label, type)
2. What you're allowed to do with it (capabilities)
3. Under what conditions (policy)
4. Where it came from (provenance)
5. What rights apply (license)
6. What you should know (signals)

The actual content lives at the origin. The egg just points to it.

---

## 2. Three-Component Pattern

ClipEgg enforces separation of concerns across three components:

| Component | Role | Contains | Location |
|-----------|------|----------|----------|
| **Egg** | Reference metadata | URI, label, caps, policy | Clipboard |
| **Content** | Actual data | Documents, images, records | Origin server |
| **Hatching Protocol** | Resolution logic | Auth, validation, audit | Shared convention |

```
┌─────────────────┐
│  Egg            │  "Here's WHERE the content lives"
│  (clipboard)    │  "Here's WHAT you can do with it"
└────────┬────────┘
         │
         ├─────────> ┌─────────────────┐
         │           │ Content         │  Actual data stays here
         │           │ (origin)        │  Protected, auditable
         │           └─────────────────┘
         │
         └─────────> ┌─────────────────┐
                     │ Hatching        │  Shared protocol for
                     │ (convention)    │  resolving references
                     └─────────────────┘
```

**Why this matters:** The data never leaves the controlled environment at copy time. Only the reference travels. Resolution happens later, with full auth and audit.

---

## 3. Egg Schema

### 3.1 Core Fields

```json
{
  "v": 1,
  "kind": "clipegg",
  "uri": "https://app.example.com/doc/a1b2c3d4",
  "label": "Q3 Financial Summary",
  "type": "document"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `v` | integer | Yes | Schema version (currently `1`) |
| `kind` | string | Yes | Always `"clipegg"` |
| `uri` | string | Yes | Canonical resource identifier |
| `label` | string | Yes | Human-readable display name |
| `type` | string | Yes | Content type hint |

### 3.2 Capabilities (caps)

Declares what operations the origin authorizes for this reference:

```json
{
  "caps": ["view", "embed"]
}
```

| Capability | Meaning |
|------------|---------|
| `view` | Recipient may display the content |
| `edit` | Recipient may request write access |
| `embed` | Recipient may inline-render the content |
| `reshare` | Recipient may copy this egg forward |
| `download` | Recipient may request a local copy |
| `print` | Recipient may generate hard copy |

Capabilities are **declarative intent**, not enforcement. The hatching endpoint enforces actual access control.

### 3.3 Policy Block

Defines constraints on the reference:

```json
{
  "policy": {
    "expires": "2025-12-31T23:59:59Z",
    "destinations": ["internal://*", "https://*.example.com"],
    "revocable": true,
    "dnd": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `expires` | ISO 8601 | Reference invalid after this time |
| `destinations` | string[] | Allowed paste target patterns |
| `revocable` | boolean | Origin may invalidate this reference |
| `dnd` | boolean | "Do Not Delete" - audit trail required |

### 3.4 License Block

Defines rights and commerce terms:

```json
{
  "license": {
    "tier": "preview",
    "commercial": false,
    "attribution": "Acme Corp",
    "upgrade_uri": "https://example.com/upgrade/abc123"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tier` | string | License level: `preview`, `personal`, `creator`, `pro`, `exclusive` |
| `commercial` | boolean | Commercial use permitted |
| `attribution` | string | Required attribution text |
| `upgrade_uri` | string | URL to upgrade license tier |

**Use case:** Content marketplaces, stock assets, music samples. The egg carries the license terms. Hatching returns content appropriate to the user's tier.

### 3.5 Signals Block

Creator-declared content metadata (NOT platform-mandated):

```json
{
  "signals": {
    "creator_declared": true,
    "tags": ["explicit-language", "mature-themes"],
    "context": "Contains profanity in vocal samples"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `creator_declared` | boolean | Signals set by creator, not algorithm |
| `tags` | string[] | Content tags (e.g., `explicit`, `nsfw`, `violence`, `workplace-safe`) |
| `context` | string | Human-readable explanation |

**Principles:**
- Creator-controlled — Only the creator sets signals. Platform doesn't override.
- Voluntary — No signal required. Absence ≠ "safe." It means "unspecified."
- Non-punitive — Signaling doesn't affect discoverability or licensing.
- Transparent — Signals are visible to users. No hidden metadata.

**What this enables:**
- Receiving apps decide how to handle tagged content
- Enterprise policies: "Accept only 'workplace-safe' tagged content"
- User preferences without platform-wide censorship

### 3.6 Provenance Block

Tracks content lineage:

```json
{
  "provenance": {
    "origin": "https://example.com/asset/original-123",
    "derived_from": ["asset/sample-456", "asset/loop-789"],
    "generation": 2,
    "license_chain": ["cc-by-4.0", "creator-tier"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `origin` | string | Original source URI |
| `derived_from` | string[] | Parent asset URIs (for remixes, samples) |
| `generation` | integer | How many derivations from original |
| `license_chain` | string[] | License terms through the chain |

**Use case:** Remixes, samples, AI-generated derivatives. The egg knows its parents. Attribution flows automatically. License compatibility is verifiable.

### 3.7 Optional Metadata Fields

```json
{
  "thumb": "https://app.example.com/thumb/a1b2c3d4.png",
  "hatch": "https://api.example.com/.well-known/clipegg/hatch",
  "created": "2025-11-24T10:30:00Z",
  "actor": "user@example.com",
  "status": "active",
  "notes": "Copied from Q3 board meeting materials"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `thumb` | string | URL to thumbnail (< 10KB recommended) |
| `hatch` | string | Explicit hatching endpoint |
| `created` | ISO 8601 | When the egg was created |
| `actor` | string | Who created the egg |
| `status` | string | `active`, `revoked`, `expired` |
| `notes` | string | Human context |

### 3.8 Complete Example

```json
{
  "v": 1,
  "kind": "clipegg",
  "uri": "https://app.example.com/doc/a1b2c3d4",
  "label": "Q3 Financial Summary",
  "type": "document",
  "caps": ["view", "embed"],
  "policy": {
    "expires": "2025-12-31T23:59:59Z",
    "destinations": ["internal://*"],
    "revocable": true,
    "dnd": true
  },
  "license": {
    "tier": "internal",
    "commercial": false,
    "attribution": "Acme Corp Finance Team"
  },
  "signals": {
    "creator_declared": true,
    "tags": ["confidential", "financial"],
    "context": "Internal Q3 numbers, pre-earnings"
  },
  "provenance": {
    "origin": "https://app.example.com/doc/a1b2c3d4",
    "generation": 0
  },
  "thumb": "https://app.example.com/thumb/a1b2c3d4.png",
  "created": "2025-11-24T10:30:00Z",
  "actor": "jane@example.com",
  "status": "active"
}
```

---

## 4. What ClipEgg CAN and CANNOT Contain

### 4.1 What the Egg CAN Do

✅ Reference content via URI  
✅ Provide human-readable labels  
✅ Declare intended capabilities  
✅ Define policy constraints  
✅ Carry license terms  
✅ Include creator-declared signals  
✅ Track provenance chain  
✅ Include small thumbnails (URL reference, not inline)  
✅ Carry audit metadata (actor, created, notes)  

### 4.2 What the Egg CANNOT Do

❌ Contain inline data payloads (base64, encoded files)  
❌ Contain executable code (scripts, handlers)  
❌ Embed full images or documents  
❌ Include credentials or tokens  
❌ Carry more than 4KB total  

### 4.3 Why This Matters: Preventing Viral Contamination

**BAD (Data Leak):**
```json
{
  "label": "Q3 Report",
  "content": "Revenue: $4.2M, Expenses: $3.1M, Net: $1.1M...",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Why it's bad:**
- Data leaves controlled environment at copy time
- No audit trail of where it went
- Can't revoke after copy
- Clipboard becomes exfiltration vector

**GOOD (Reference Only):**
```json
{
  "v": 1,
  "kind": "clipegg",
  "uri": "https://internal.example.com/reports/q3-2025",
  "label": "Q3 Report",
  "type": "report",
  "caps": ["view"],
  "policy": { "destinations": ["internal://*"] }
}
```

**Why it's good:**
- Only reference leaves the environment
- Hatching requires authentication
- Full audit of every resolution
- Can revoke access after copy
- Unauthorized destinations get useless reference

---

## 5. Clipboard Implementation

### 5.1 MIME Types

ClipEgg uses multiple clipboard formats for compatibility:

| Format | MIME Type | Content |
|--------|-----------|---------|
| Primary | `application/x-clipegg+json` | Full egg JSON |
| Fallback (plain) | `text/plain` | `{label}\n{uri}` |
| Fallback (HTML) | `text/html` | `<a href="{uri}">{label}</a>` |

### 5.2 Copy Implementation

```javascript
document.addEventListener('copy', (e) => {
  const target = e.target.closest('[data-clipegg]');
  if (!target) return;
  
  e.preventDefault();
  
  const egg = {
    v: 1,
    kind: "clipegg",
    uri: target.dataset.uri,
    label: target.dataset.label,
    type: target.dataset.type || "unknown",
    caps: JSON.parse(target.dataset.caps || '["view"]'),
    policy: JSON.parse(target.dataset.policy || '{}'),
    created: new Date().toISOString(),
    status: "active"
  };
  
  // Primary format
  e.clipboardData.setData(
    'application/x-clipegg+json', 
    JSON.stringify(egg)
  );
  
  // Fallbacks for non-ClipEgg-aware apps
  e.clipboardData.setData('text/plain', `${egg.label}\n${egg.uri}`);
  e.clipboardData.setData('text/html', `<a href="${egg.uri}">${egg.label}</a>`);
});
```

### 5.3 Paste Detection

```javascript
document.addEventListener('paste', (e) => {
  const eggData = e.clipboardData.getData('application/x-clipegg+json');
  
  if (eggData) {
    e.preventDefault();
    const egg = JSON.parse(eggData);
    
    if (egg.v !== 1 || egg.kind !== 'clipegg') {
      console.warn('Invalid ClipEgg format');
      return;
    }
    
    if (!validateDestination(egg.policy?.destinations)) {
      console.warn('This destination not authorized');
      return;
    }
    
    handleClipEgg(egg);
  }
});
```

---

## 6. Hatching Protocol

### 6.1 Overview

Hatching is the process of resolving an egg reference to retrieve full content. Hatching is OPTIONAL — applications MAY use the egg metadata directly without resolution.

### 6.2 Endpoint Discovery

1. Explicit `hatch` field in egg (if present)
2. Well-known path: `{uri.origin}/.well-known/clipegg/hatch`
3. Direct GET to `uri` with `Accept: application/x-clipegg-hatch+json`

### 6.3 Request Format

```http
POST /.well-known/clipegg/hatch HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "uri": "https://app.example.com/doc/a1b2c3d4",
  "egg_created": "2025-11-24T10:30:00Z",
  "accept": ["application/json", "text/html", "image/png"],
  "context": {
    "target_origin": "https://recipient-app.com",
    "target_app": "SlackDesktop/4.35",
    "purpose": "paste"
  }
}
```

### 6.4 Response Format

**Success:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok",
  "content_type": "application/json",
  "content": { ... },
  "expires": "2025-11-24T12:00:00Z",
  "audit_id": "evt_abc123"
}
```

**Denied:**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "status": "denied",
  "reason": "destination_not_authorized",
  "audit_id": "evt_abc124"
}
```

### 6.5 License-Aware Hatching

When egg contains `license` block, hatching returns content appropriate to user's tier:

| User Tier | Response |
|-----------|----------|
| No license | Preview only, watermarked |
| `personal` | Full content, non-commercial |
| `pro` | Full content, commercial rights |
| `exclusive` | Full content, exclusive rights |

### 6.6 Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 401 | Authentication required |
| 403 | Access denied (policy violation, unauthorized destination) |
| 404 | Resource not found |
| 410 | Resource revoked |
| 451 | Unavailable for legal reasons |

---

## 7. Security Model

### 7.1 Guardrails

1. **Size Limit:** Eggs MUST be < 4KB. Larger payloads indicate data smuggling.
2. **No Inline Data:** Validators SHOULD reject eggs containing base64 or encoded payloads.
3. **Policy Enforcement:** Hatching endpoints MUST validate `target_origin` against `policy.destinations`.
4. **Audit Trail:** All hatching requests MUST be logged (DND compliance).
5. **Expiration:** Eggs with `policy.expires` MUST be rejected after expiration.
6. **Revocation:** Origins MUST support revoking eggs when `policy.revocable` is true.

### 7.2 Data Loss Prevention

ClipEgg transforms clipboard from an exfiltration vector to an audit point:

| Traditional Clipboard | ClipEgg |
|-----------------------|---------|
| Data copied at rest | Reference copied |
| No visibility | Full audit trail |
| Can't revoke | Revocable |
| Any destination | Destination allowlist |
| Silent exfiltration | Logged resolution |

### 7.3 Threat Model

| Threat | Mitigation |
|--------|------------|
| Data exfiltration via paste | Destination allowlist, audit logging |
| Clipboard snooping | Reference-only, no inline data |
| Stale access after revocation | Revocation support, expiration |
| Unauthorized resharing | `reshare` capability control |
| Spoofed eggs | Origin validation at hatching |

---

## 8. Compliance

### 8.1 ROTG (Rules of the Game)

Conformant implementations:
- Use schema version `v: 1`
- Include all required fields
- Declare capabilities explicitly
- Enforce policy constraints
- Support hatching protocol

### 8.2 DND (Do Not Delete)

When `policy.dnd` is true:
- Archive eggs before deletion
- Log all hatching attempts
- Retain audit trail per retention policy
- Human approval for revocation

---

## 9. Comparison: Traditional vs ClipEgg

| Aspect | Traditional Clipboard | ClipEgg |
|--------|----------------------|---------|
| **Carries** | Full data payload | Reference metadata |
| **Size** | Unbounded (MB+) | < 4KB |
| **Exfiltration** | Immediate, silent | Blocked or audited |
| **Revocation** | Impossible | Supported |
| **Audit** | None | Full trail |
| **Auth** | None | Per-resolution |
| **License** | None | Embedded terms |
| **Provenance** | Lost | Tracked |

---

## 10. Mental Model

```
ClipEgg = Claim ticket that says:
  "Content X lives at location Y"
  "You may do Z with it"
  "Under these conditions..."
  "With these rights..."
  "From this source..."

NOT:
  "Here is the actual content"
  "Here is an encoded copy"
  "Do whatever you want with it"
```

**Copy = Frosting. Cut = Cake.**

---

## 11. Implementation Checklist

### 11.1 Origin App (Copy Side)

- [ ] Intercept copy events on ClipEgg-enabled elements
- [ ] Generate conformant egg JSON
- [ ] Set all three clipboard formats
- [ ] Enforce < 4KB limit
- [ ] Log copy events for audit

### 11.2 Destination App (Paste Side)

- [ ] Detect `application/x-clipegg+json` format
- [ ] Validate egg schema
- [ ] Check policy constraints before hatching
- [ ] Handle hatching errors gracefully
- [ ] Fall back to label/URI for unauthorized destinations

### 11.3 Hatching Endpoint

- [ ] Validate authentication
- [ ] Check authorization for resource
- [ ] Validate `target_origin` against policy
- [ ] Check license tier for content resolution
- [ ] Log all requests (success and failure)
- [ ] Support revocation queries
- [ ] Return appropriate error codes

---

## 12. Browser Compatibility

| Browser | `application/x-clipegg+json` | Fallbacks |
|---------|------------------------------|-----------|
| Chrome 76+ | ✅ | ✅ |
| Firefox 87+ | ✅ | ✅ |
| Safari 13.1+ | ✅ | ✅ |
| Edge 79+ | ✅ | ✅ |

---

## 13. Future Considerations

- **Signed eggs:** Cryptographic proof of origin
- **Encrypted references:** URI obfuscation for sensitive resources
- **Batch eggs:** Multiple resources in single egg
- **Streaming hatching:** Progressive content resolution
- **Cross-origin negotiation:** Federated trust for hatching
- **Payment triggers:** Commerce events on hatching/publish/cut

---

## 14. References

- [Clipboard API and Events (W3C)](https://www.w3.org/TR/clipboard-apis/)
- [Web Custom Formats (Chromium)](https://github.com/nicell/web-custom-formats)

---

## Appendix A: JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ra96it.app/schema/clipegg/v1/egg.json",
  "title": "ClipEgg",
  "type": "object",
  "required": ["v", "kind", "uri", "label", "type"],
  "properties": {
    "v": { "type": "integer", "const": 1 },
    "kind": { "type": "string", "const": "clipegg" },
    "uri": { "type": "string", "format": "uri" },
    "label": { "type": "string", "maxLength": 256 },
    "type": { "type": "string" },
    "caps": {
      "type": "array",
      "items": { 
        "type": "string",
        "enum": ["view", "edit", "embed", "reshare", "download", "print"]
      }
    },
    "policy": {
      "type": "object",
      "properties": {
        "expires": { "type": "string", "format": "date-time" },
        "destinations": { "type": "array", "items": { "type": "string" } },
        "revocable": { "type": "boolean" },
        "dnd": { "type": "boolean" }
      }
    },
    "license": {
      "type": "object",
      "properties": {
        "tier": { "type": "string" },
        "commercial": { "type": "boolean" },
        "attribution": { "type": "string" },
        "upgrade_uri": { "type": "string", "format": "uri" }
      }
    },
    "signals": {
      "type": "object",
      "properties": {
        "creator_declared": { "type": "boolean" },
        "tags": { "type": "array", "items": { "type": "string" } },
        "context": { "type": "string" }
      }
    },
    "provenance": {
      "type": "object",
      "properties": {
        "origin": { "type": "string", "format": "uri" },
        "derived_from": { "type": "array", "items": { "type": "string" } },
        "generation": { "type": "integer", "minimum": 0 },
        "license_chain": { "type": "array", "items": { "type": "string" } }
      }
    },
    "thumb": { "type": "string", "format": "uri" },
    "hatch": { "type": "string", "format": "uri" },
    "created": { "type": "string", "format": "date-time" },
    "actor": { "type": "string" },
    "status": { "type": "string", "enum": ["active", "revoked", "expired"] },
    "notes": { "type": "string", "maxLength": 512 }
  },
  "additionalProperties": false
}
```

---

## Appendix B: Quick Reference Card

**Copy:**
```javascript
e.clipboardData.setData('application/x-clipegg+json', JSON.stringify({
  v: 1, kind: "clipegg", uri, label, type, caps, policy
}));
```

**Paste:**
```javascript
const egg = JSON.parse(e.clipboardData.getData('application/x-clipegg+json'));
if (egg?.kind === 'clipegg') { /* handle */ }
```

**Hatch:**
```http
POST /.well-known/clipegg/hatch
{ "uri": "...", "context": { "target_origin": "..." } }
```

---

**Version:** 0.2.1-draft  
**Created:** November 2025  
**Author:** Dave @daaaave-atx  
**Status:** Draft Specification  
**License:** CC BY 4.0
