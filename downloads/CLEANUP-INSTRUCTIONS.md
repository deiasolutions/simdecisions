# PHASE 0 CLEANUP - Execute with Claude Code

## Instructions for Claude Code

You are cleaning up the deiasolutions/deia repo. Execute these steps in order.

---

## Step 1: Show Current State

```bash
cd /path/to/deiasolutions/deia
find . -maxdepth 2 -type d | grep -v node_modules | grep -v __pycache__ | grep -v .git/ | head -80
```

Report what you find, especially:
- Is there a `deia_raqcoon_v1/` anywhere?
- Is there a `raqcoon_improv/` anywhere?
- What's inside `deia_raqcoon/`?

---

## Step 2: Create Archive Branch (Preserve History)

```bash
git checkout -b archive/pre-cleanup-2026-02-01
git push origin archive/pre-cleanup-2026-02-01
git checkout master
```

---

## Step 3: Create _archive Directory

```bash
mkdir -p _archive/2026-02-01-cleanup
```

---

## Step 4: Move Dormant/Experimental Folders to Archive

```bash
# Dormant experiments
git mv .simulations _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv .git-rewrite _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv extensions _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv llama-chatbot _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv website _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv examples _archive/2026-02-01-cleanup/ 2>/dev/null || true

# IDE/private (shouldn't be in repo)
git mv .idea _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv .private _archive/2026-02-01-cleanup/ 2>/dev/null || true

# If these exist, archive them:
git mv deia_raqcoon_v1 _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv raqcoon_improv _archive/2026-02-01-cleanup/ 2>/dev/null || true

# Check if they're inside deia_raqcoon and move if so:
git mv deia_raqcoon/deia_raqcoon_v1 _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv deia_raqcoon/raqcoon_improv _archive/2026-02-01-cleanup/ 2>/dev/null || true
```

---

## Step 5: Delete Cruft

```bash
# Obvious cruft
rm -rf "New folder" 2>/dev/null || true
rm -f BACKLOG.md.backup 2>/dev/null || true
rm -f README_OLD.md 2>/dev/null || true

# Garbled filename
rm -f "CUsersdaveeOneDriveDocumentsGitHubdeiasolutions.deiabot-logsCLAUDE-CODE-005-activity.jsonl" 2>/dev/null || true
rm -f "C*.jsonl" 2>/dev/null || true

# Root-level scripts that should be in scripts/
mkdir -p scripts/legacy
git mv launch-bot-002.bat scripts/legacy/ 2>/dev/null || true
git mv launch-bot-002.ps1 scripts/legacy/ 2>/dev/null || true
git mv launch_platform.py scripts/legacy/ 2>/dev/null || true
git mv open-hivemind-chat.bat scripts/legacy/ 2>/dev/null || true
git mv open-hivemind-ui.bat scripts/legacy/ 2>/dev/null || true
git mv run_bots.py scripts/legacy/ 2>/dev/null || true
git mv run_dashboard.py scripts/legacy/ 2>/dev/null || true
git mv run_gemini_worker.ps1 scripts/legacy/ 2>/dev/null || true
git mv run_scrum_master.py scripts/legacy/ 2>/dev/null || true
git mv run_scrum_master_terminal.py scripts/legacy/ 2>/dev/null || true
git mv run_single_bot.py scripts/legacy/ 2>/dev/null || true
git mv spawn_hive.py scripts/legacy/ 2>/dev/null || true
git mv start-bot.ps1 scripts/legacy/ 2>/dev/null || true
git mv start-hivemind.ps1 scripts/legacy/ 2>/dev/null || true
git mv connect-discord.ps1 scripts/legacy/ 2>/dev/null || true
git mv create-startup-shortcut.ps1 scripts/legacy/ 2>/dev/null || true
git mv test-mcp-server.bat scripts/legacy/ 2>/dev/null || true
git mv test-mcp-server.ps1 scripts/legacy/ 2>/dev/null || true

# Root-level test files that should be in tests/
git mv .test_websocket.py tests/ 2>/dev/null || true
git mv test_adapter.py tests/ 2>/dev/null || true
git mv test_adapter_quick.py tests/ 2>/dev/null || true
git mv test_bot_controller.sh tests/ 2>/dev/null || true
git mv test_uat_all.py tests/ 2>/dev/null || true
```

---

## Step 6: Consolidate Docs

```bash
mkdir -p docs/governance
mkdir -p docs/vision
mkdir -p docs/guides
mkdir -p docs/specs

# Move governance docs
git mv CONSTITUTION.md docs/governance/ 2>/dev/null || true
git mv PRINCIPLES.md docs/governance/ 2>/dev/null || true

# Move vision docs
git mv MULTI_DOMAIN_VISION.md docs/vision/ 2>/dev/null || true
git mv deia-vision-technical.md docs/vision/ 2>/dev/null || true

# Move guides/specs
git mv IDEA_METHOD.md docs/guides/ 2>/dev/null || true
git mv DEIA_ASSESSMENT.md docs/specs/ 2>/dev/null || true
git mv MULTI-AGENT-ARCHITECTURE.md docs/specs/ 2>/dev/null || true
git mv CONVERSATION_LOGGING_QUICKSTART.md docs/guides/ 2>/dev/null || true
git mv DEIA-HIVE-QUICKSTART.md docs/guides/ 2>/dev/null || true
git mv WINDOWS-SETUP.md docs/guides/ 2>/dev/null || true
git mv UAT-TEST-PLAN.md docs/specs/ 2>/dev/null || true
git mv WEBSITE-LAUNCH-PLAN.md docs/specs/ 2>/dev/null || true
git mv CODEX-SPEC-ADDENDUM.md docs/specs/ 2>/dev/null || true
git mv test-spec-e2e.md docs/specs/ 2>/dev/null || true

# One-off docs to archive
git mv "Bot Instructions 1.md" _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv Claude-Decisions.md _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv deia_project_inventory.md _archive/2026-02-01-cleanup/ 2>/dev/null || true
git mv BOK_MOVED.md _archive/2026-02-01-cleanup/ 2>/dev/null || true
```

---

## Step 7: Update .gitignore

Add these lines to .gitignore if not present:

```
# IDE
.idea/
.vscode/

# Private
.private/

# Cache
__pycache__/
*.pyc
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Temp
New folder/
```

---

## Step 8: Commit Clean State

```bash
git add -A
git status
# Review what changed

git commit -m "chore: Phase 0 cleanup - archive dormant code, consolidate docs, remove cruft

- Archived: .simulations, extensions, llama-chatbot, website, deia_raqcoon_v1, raqcoon_improv
- Moved root scripts to scripts/legacy/
- Moved root tests to tests/
- Consolidated docs into docs/governance, docs/vision, docs/guides, docs/specs
- Removed cruft: New folder, backup files, garbled filenames
- Preserved history in archive/pre-cleanup-2026-02-01 branch"
```

---

## Step 9: Report Final State

```bash
# Show clean structure
find . -maxdepth 2 -type d | grep -v node_modules | grep -v __pycache__ | grep -v .git | sort

# Count files at root
ls -la | wc -l
```

**Expected root files (should be ~15-20):**
- README.md
- LICENSE
- CONTRIBUTING.md
- INSTALLATION.md
- ROADMAP.md
- BACKLOG.md
- QUICKSTART.md
- BUG_REPORTS.md
- FEATURE_REQUESTS.md
- pyproject.toml
- pytest.ini
- package.json
- netlify.toml
- .gitignore
- coverage.json
- project_resume.md

**Expected root folders (should be ~10-12):**
- .claude/
- .deia/
- .github/
- _archive/
- bok/
- deia_raqcoon/
- docs/
- scripts/
- src/
- templates/
- tests/

---

## Step 10: Verify Nothing Broke

```bash
# Check Python package still works
pip install -e . --quiet
deia --help

# Run tests
pytest tests/ -x -q --tb=short
```

---

## Done

Report back:
1. What was archived
2. What was deleted
3. What the clean structure looks like
4. Any errors encountered
