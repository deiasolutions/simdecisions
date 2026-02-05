# ClipEgg: We Left the Clipboard Unguarded for 40 Years

In 1984, Apple shipped copy and paste. It was a miracle of usability—and architecturally broken from day one.

Press Ctrl+C and the entire payload—bytes, formatting, metadata, embedded objects—dumps into a system buffer that any application can read. No auth. No logging. No revocation.

The clipboard is a broadcast channel disguised as a convenience.

**The catastrophe:** The clipboard is now the #1 data exfiltration vector in enterprise. 77% of knowledge workers paste corporate data into AI tools. Every paste bypasses your CASB, EDR, SIEM, and DLP. Your security stack guards the front door while users walk data out the side.

**The waste:** 40 billion copy operations/day × ~100KB average = 4 exabytes of daily churn. RAM pressure, cloud sync, VM duplication—all unnecessary. Annualized: 83B kWh, 33M tons CO₂, $10B in energy costs. We're burning a small nation's power grid because nobody questioned whether copying a sentence needed to ship a document.

**The semantic lie:** Copy and cut were always opposites, but we implemented them identically. COPY means "give me a reference." CUT means "I'm taking this." Human intention: reference. System behavior: duplication. The mismatch is the original sin.

**The confession:** The most common paste operation on Earth is Paste Special → Unformatted Text. Billions of people daily, manually fighting the clipboard. We already behave as if copy is a request for meaning, not payload.

**The shift:** We moved from the marketplace of ideas to the marketplace of intentions. Ideas were static, self-contained, ready for duplication. Intentions are contextual—who's asking, where, for what purpose. Copy is no longer "give me the thing." Copy is "here's what I intend to do with this meaning." The clipboard still acts like it's 1984.

**ClipEgg:** Copy becomes a declaration of intent. A copy emits a 4KB "egg"—a reference plus capabilities plus policy. No payload.

```json
{"v":1,"uri":"https://app.example.com/doc/123","label":"Q3 Report","type":"document","caps":["view"],"policy":{"expires":"2025-12-31","destinations":["internal://*"]}}
```

Paste becomes the trust boundary. Paste asks: "Given who I am and where I'm pasting, what am I allowed to receive?"

- Notepad → plain text
- Word → fetch formatting on demand  
- ChatGPT → hydration denied
- Internal app → full content via auth endpoint

**Copy = Frosting. Cut = Cake.** Copy gives you the lightweight reference—hydrate richness on demand. Cut gives you the full payload—it's a transfer, not a reference.

**The security dividend:** Paste-target validation. Complete audit trails. Revocation after copy. Expiration. Contextual access. This is clipboard-level Zero Trust.

**Implementation:** 50 lines of JavaScript. Existing Clipboard API. No browser changes, no extensions. Legacy apps get graceful fallback (title + link). Gradual adoption, immediate value.

**This is not a product.** ClipEgg is an open protocol. MIT implementation, CC BY 4.0 spec. I'm giving it away—because some problems shouldn't have owners.

For engineers: In programming, `=` passes reference, `==` checks value. For 40 years, copy behaved like `==`. ClipEgg makes it behave like `=`.

Spec: https://github.com/daaaave-ATX/clipegg
