# Vision Docs Commit Instructions

## Placement

```
deia_raqcoon/
  docs/
    vision/
      UNIFIED-VISION.md
      BACKLOG.md
      ROADMAP-AGGRESSIVE.md
```

## Commands

```bash
cd C:\Users\davee\OneDrive\Documents\GitHub\deiasolutions

# Create folder
mkdir -p deia_raqcoon/docs/vision

# Copy files (from Downloads)
copy Downloads\vision-docs\UNIFIED-VISION.md deia_raqcoon\docs\vision\
copy Downloads\vision-docs\BACKLOG.md deia_raqcoon\docs\vision\
copy Downloads\vision-docs\ROADMAP-AGGRESSIVE.md deia_raqcoon\docs\vision\

# Commit
cd deia_raqcoon
git add docs/vision/
git commit -m "docs: add vision docs - WIRE-001 complete"
git push
```

## What Changed

- UNIFIED-VISION: "Exists but NOT wired" → "Wired (WIRE-001 complete)"
- BACKLOG: WIRE-001 tasks marked ✅ done

## Next Sprint

Phase 2: Metrics (Feb 16-28)
- Event ledger
- Cost tracking
- Basic dashboard
