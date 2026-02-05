# Task: Add Headless CLI Mode for Bot Execution

## Context
- Existing code in `adapters/cli_adapter.py` and `adapters/registry.py` launches Claude Code interactively via PTY
- I want a second option: headless execution using `claude -p --output-format json`
- This avoids interactive prompts and returns structured JSON output

## Requirements

### 1. Create `adapters/headless_adapter.py`

Create a `HeadlessAdapter` class that:
- Takes a prompt/task payload and repo_root
- Runs `claude -p "{prompt}" --output-format json --allowedTools Read,Write,Edit,Bash` as a subprocess
- Sets cwd to repo_root before execution
- Captures stdout as JSON, parses it, returns structured result
- Supports optional `--max-turns` limit
- Supports `--append-system-prompt` for KB injection

### 2. Update `adapters/registry.py`

- Add `get_headless_adapter(tool: str)` factory function
- Support "claude-code" tool (uses `claude` command)

### 3. Add new endpoint in `server.py`

Add `POST /api/bees/run-headless`:
- Request model: `bot_id`, `prompt`, `repo_root`, `max_turns` (optional), `system_prompt` (optional)
- Calls headless adapter, returns JSON result
- Non-blocking if possible (or document that it blocks until complete)

### 4. Preserve existing functionality

Keep existing PTY-based `/api/bees/launch` unchanged - this is an alternative path

## Expected Output Format

Claude Code headless returns JSON like:
```json
{
  "result": "...",
  "cost": {"total_cost": ...},
  "session_id": "..."
}
```

## Test Criteria

After implementation, I should be able to POST to `/api/bees/run-headless` with a simple prompt and get back structured JSON without any interactive prompts.

## Example Usage

```bash
claude -p "Review this file for bugs" \
  --output-format json \
  --allowedTools Read,Write,Edit,Bash \
  --max-turns 3
```

With system prompt injection:
```bash
claude -p "Implement the feature" \
  --output-format json \
  --append-system-prompt "Follow these rules: ..." \
  --allowedTools Read,Write,Edit,Bash
```
