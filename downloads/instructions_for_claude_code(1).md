# Instructions for Claude Code

Run these commands and put ALL output into a file called `response.md` in the repo root.

## Commands to Run

```bash
echo "# Inventory Response" > response.md
echo "" >> response.md
echo "## 1. .simulations contents" >> response.md
tree .simulations/ -L 3 2>&1 >> response.md || echo "folder not found or empty" >> response.md
echo "" >> response.md
echo "## 2. All raqcoon folders" >> response.md
find . -type d -name "*raqcoon*" 2>/dev/null >> response.md
echo "" >> response.md
echo "## 3. All v1 folders" >> response.md
find . -type d -name "*v1*" 2>/dev/null >> response.md
echo "" >> response.md
echo "## 4. Top-level folders" >> response.md
ls -la | grep "^d" >> response.md
echo "" >> response.md
echo "## 5. Uncommitted changes (first 50)" >> response.md
git status --short | head -50 >> response.md
echo "" >> response.md
echo "## 6. deia_raqcoon_v1 location check" >> response.md
ls -la deia_raqcoon_v1/ 2>&1 >> response.md || echo "not in repo root" >> response.md
echo "" >> response.md
echo "Done." >> response.md
```

Then say: "Done. response.md is ready."
