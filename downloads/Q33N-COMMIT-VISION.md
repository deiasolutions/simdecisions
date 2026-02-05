# Q33N: Commit Vision Docs

## Location
```
C:\Users\davee\Downloads\
```

## File
```
simdecisions-vision-pack.zip
```

## Instructions

1. Extract zip to Downloads
2. Create destination folder:
   ```bash
   mkdir -p docs/vision
   ```
3. Copy files:
   ```bash
   cp Downloads/vision-docs/UNIFIED-VISION.md docs/vision/
   cp Downloads/vision-docs/BACKLOG.md docs/vision/
   cp Downloads/vision-docs/ROADMAP-AGGRESSIVE.md docs/vision/
   ```
4. Commit:
   ```bash
   git add docs/vision/
   git commit -m "docs: add vision docs - WIRE-001 complete"
   git push
   ```

## Context

WIRE-001 sprint is complete:
- ✅ Router wired
- ✅ KB injection wired
- ✅ WebSocket broadcasts
- ✅ Gates enforced

These docs reflect that status.

## Next

Phase 2: Metrics (starts when ready)
