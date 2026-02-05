# ClipEgg Specification

**Version:** 0.2.0-draft  
**Status:** Draft  
**Author:** Dave [LastName]  
**Date:** November 2025  
**Repository:** https://github.com/[your-handle]/clipegg  
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

The actual content lives at the origin. The egg just points to it.

---

## 2. Three-Component Pattern

ClipEgg enforces separation of concerns across three components:

| Component | Role | Contains | Location |
|-----------|------|----------|----------|
| **Egg** | Reference metadata | URI, label, caps, policy | Clipboard |
| **Content** | Actual data | Documents, images, records | Origin server |
| **Hydration Protocol** | Resolution logic | Auth, validation, audit | Shared convention |

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
                     │ Hydration       │  Shared protocol for
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

Capabilities are **declarative intent**, not enforcement. The hydration endpoint enforces actual access control.

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

### 3.4 Optional Fields

```json
{
  "thumb": "https://app.example.com/thumb/a1b2c3d4.png",
  "hydrate": "https://api.example.com/.well-known/clipegg/resolve",
  "created": "2025-11-24T10:30:00Z",
  "actor": "user@example.com",
  "status": "active",
  "notes": "Copied from Q3 board meeting materials"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `thumb` | string | URL to thumbnail (< 10KB recommended) |
| `hydrate` | string | Explicit hydration endpoint |
| `created` | ISO 8601 | When the egg was created |
| `actor` | string | Who created the egg |
| `status` | string | `active`, `revoked`, `expired` |
| `notes` | string | Human context |

### 3.5 Complete Example

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
- Hydration requires authentication
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
  // Only intercept for ClipEgg-enabled elements
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
    
    // Validate egg structure
    if (egg.v !== 1 || egg.kind !== 'clipegg') {
      console.warn('Invalid ClipEgg format');
      return;
    }
    
    // Check policy constraints
    if (!validateDestination(egg.policy?.destinations)) {
      console.warn('This destination not authorized');
      // Show user message, fall back to label only
      return;
    }
    
    // Hydrate if needed, or use reference directly
    handleClipEgg(egg);
  }
});
```

---

## 6. Hydration Protocol

### 6.1 Overview

Hydration is the process of resolving an egg reference to retrieve full content. Hydration is OPTIONAL — applications MAY use the egg metadata directly without resolution.

### 6.2 Endpoint Discovery

1. Explicit `hydrate` field in egg (if present)
2. Well-known path: `{uri.origin}/.well-known/clipegg/resolve`
3. Direct GET to `uri` with `Accept: application/x-clipegg-hydrate+json`

### 6.3 Request Format

```http
POST /.well-known/clipegg/resolve HTTP/1.1
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

### 6.5 Error Codes

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
3. **Policy Enforcement:** Hydration endpoints MUST validate `target_origin` against `policy.destinations`.
4. **Audit Trail:** All hydration requests MUST be logged (DND compliance).
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

**Example scenario:**

1. User copies "Q3 Revenue Report" from internal app
2. Clipboard holds: `{ uri: "internal://doc/q3", caps: ["view"], policy: { destinations: ["internal://*"] }}`
3. User pastes into ChatGPT
4. ChatGPT receives the egg, attempts hydration
5. Hydration endpoint checks `target_origin`: `chat.openai.com` ≠ `internal://*`
6. Returns 403, logs attempt
7. ChatGPT gets useless reference, not the data

### 7.3 Fallback Data Leakage

The `label` and plaintext fallback may leak information. Implementations SHOULD:

- Use generic labels for sensitive content ("Confidential Document")
- Omit URIs from plaintext fallback for internal resources
- Consider fallback content as effectively public

### 7.4 Threat Model

| Threat | Mitigation |
|--------|------------|
| Data exfiltration via paste | Destination allowlist, audit logging |
| Clipboard snooping | Reference-only, no inline data |
| Stale access after revocation | Revocation support, expiration |
| Unauthorized resharing | `reshare` capability control |
| Spoofed eggs | Origin validation at hydration |

---

## 8. Compliance

### 8.1 ROTG (Rules of the Game)

Conformant implementations:
- Use schema version `v: 1`
- Include all required fields
- Declare capabilities explicitly
- Enforce policy constraints
- Support hydration protocol

### 8.2 DND (Do Not Delete)

When `policy.dnd` is true:
- Archive eggs before deletion
- Log all hydration attempts
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

---

## 10. Mental Model

```
ClipEgg = Claim ticket that says:
  "Content X lives at location Y"
  "You may do Z with it"
  "Under these conditions..."

NOT:
  "Here is the actual content"
  "Here is an encoded copy"
  "Do whatever you want with it"
```

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
- [ ] Check policy constraints before hydration
- [ ] Handle hydration errors gracefully
- [ ] Fall back to label/URI for unauthorized destinations

### 11.3 Hydration Endpoint

- [ ] Validate authentication
- [ ] Check authorization for resource
- [ ] Validate `target_origin` against policy
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

Note: Custom MIME types in clipboard require `ClipboardItem` API or `clipboardData.setData()`.

---

## 13. Future Considerations

- **Signed eggs:** Cryptographic proof of origin
- **Encrypted references:** URI obfuscation for sensitive resources
- **Batch eggs:** Multiple resources in single egg
- **Streaming hydration:** Progressive content resolution
- **Cross-origin negotiation:** Federated trust for hydration

---

## 14. References

- [Clipboard API and Events (W3C)](https://www.w3.org/TR/clipboard-apis/)
- [Web Custom Formats (Chromium)](https://github.com/nicell/web-custom-formats)
- [DEIA Egg Specification](https://github.com/[your-handle]/deia) — Conceptual foundation

---

## Appendix A: JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://clipegg.org/schema/v1/egg.json",
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
    "thumb": { "type": "string", "format": "uri" },
    "hydrate": { "type": "string", "format": "uri" },
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

**Hydrate:**
```http
POST /.well-known/clipegg/resolve
{ "uri": "...", "context": { "target_origin": "..." } }
```

---

**Version:** 0.2.0-draft  
**Created:** November 2025  
**Author:** Dave [LastName]  
**Status:** Draft Specification  
**License:** CC BY 4.0
