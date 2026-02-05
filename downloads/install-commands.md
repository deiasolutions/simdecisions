# Installation Commands: FBB Experimentation Framework

**Date:** 2025-10-21  
**Purpose:** Install experimentation framework documentation to correct locations  
**Target:** CLI bot or manual execution

---

## Prerequisites

Ensure these directories exist:
```bash
mkdir -p familybondbot/docs/architecture
mkdir -p "C:\Users\davee\.deia\bok\patterns"
mkdir -p "C:\Users\davee\.deia\bok\decisions"
mkdir -p "C:\Users\davee\.deia\hive\queues\bot-003"
mkdir -p "C:\Users\davee\.deia\hive\queues\bot-004"
mkdir -p "C:\Users\davee\.deia\hive\queues\bot-005"
```

---

## File 1: Main Specification

**Download:** `experimentation-framework.md` from Canvas  
**Destination 1 (Primary):** `familybondbot/docs/architecture/experimentation-framework.md`  
**Destination 2 (Backup):** `C:/Users/davee/.deia/bok/patterns/experimentation-framework-design.md`

**Commands:**
```bash
# Assuming file downloaded to ~/Downloads/
copy "%USERPROFILE%\Downloads\experimentation-framework.md" "familybondbot\docs\architecture\experimentation-framework.md"
copy "%USERPROFILE%\Downloads\experimentation-framework.md" "C:\Users\davee\.deia\bok\patterns\experimentation-framework-design.md"
```

**Verify:**
```bash
dir familybondbot\docs\architecture\experimentation-framework.md
dir "C:\Users\davee\.deia\bok\patterns\experimentation-framework-design.md"
```

---

## File 2: Architecture Decision Record

**Download:** `ADR-0006-fbb-persistent-experimentation.md` from Canvas  
**Destination:** `C:/Users/davee/.deia/bok/decisions/ADR-0006-fbb-persistent-experimentation.md`

**Commands:**
```bash
copy "%USERPROFILE%\Downloads\ADR-0006-fbb-persistent-experimentation.md" "C:\Users\davee\.deia\bok\decisions\ADR-0006-fbb-persistent-experimentation.md"
```

**Verify:**
```bash
dir "C:\Users\davee\.deia\bok\decisions\ADR-0006-fbb-persistent-experimentation.md"
```

---

## Git Commit (Optional)

**If installing to familybondbot repo:**
```bash
cd familybondbot
git add docs/architecture/experimentation-framework.md
git commit -m "docs: Add experimentation framework specification"
git push
```

---

## Verification Checklist

After running commands, verify these files exist:

- [ ] `familybondbot/docs/architecture/experimentation-framework.md`
- [ ] `C:/Users/davee/.deia/bok/patterns/experimentation-framework-design.md`
- [ ] `C:/Users/davee/.deia/bok/decisions/ADR-0006-fbb-persistent-experimentation.md`

**Count lines (optional):**
```bash
# Should be ~15,000 words / ~600 lines
wc -l familybondbot\docs\architecture\experimentation-framework.md

# Should be ~3,000 words / ~150 lines
wc -l "C:\Users\davee\.deia\bok\decisions\ADR-0006-fbb-persistent-experimentation.md"
```

---

## Notes

- Files have installation instructions embedded (ignore those, use these commands instead)
- No bot task files created yet (defer to post-P0 work)
- Specs ready for reference when implementation starts

---

## What's Next

**After installation:**
1. Files are in place for reference
2. Focus on FBB P0 fixes first
3. Return to experimentation framework in week 2-3

**No action required beyond running the copy commands above.**

---

**END OF INSTALLATION COMMANDS**