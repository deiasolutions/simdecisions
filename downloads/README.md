# ClipEgg 🥚

**Reference-based clipboard protocol.**

Copy references, not payloads. Claim tickets, not cargo.

## The Problem

We confused copying with hoarding.

40 billion copy operations happen every day. Average payload: 100KB of stuff nobody asked for. That's 4 exabytes sitting in RAM, syncing across devices, getting pasted into AI tools that charge per token.

The energy cost: 33 million tons of CO2 annually. For clipboard formatting.

## The Solution

**Old copy:** Here's everything. Hoard it.

**New copy:** Here's a reference. Fetch what you need, when you need it, if you're allowed.

An egg. 200 bytes. A claim ticket, not cargo.

```json
{
  "v": 1,
  "kind": "clipegg",
  "uri": "https://app.example.com/doc/abc123",
  "label": "Q3 Financial Summary",
  "type": "document",
  "caps": ["view"],
  "policy": { "revocable": true }
}
```

The receiver hatches the egg based on context. Paste into a terminal? Plain text. Paste into Figma? Hatch the full asset. Paste into a system that shouldn't have access? Nothing.

## Demo

**[See it work →](https://daaaave-atx.github.io/clipe96)**

## Docs

- [Full Specification](./SPEC.md)
- [WICG Proposal](./WICG_PROPOSAL.md)

## The Insight

Copy = Frosting.
Cut = Cake.

---

*Dave @daaaave-atx*  
*November 2025*
