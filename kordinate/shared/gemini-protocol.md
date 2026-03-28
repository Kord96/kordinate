---
description: How to call the Gemini CLI for peer review and second opinions
preloaded: all
curated: true
scope: global
---

## Gemini CLI

Binary: `/home/claude/.npm-global/bin/gemini`
Auth: `GEMINI_API_KEY` env var (set in settings.json, inherited by all agents)

### Usage

```bash
# Simple prompt
gemini -p "your prompt here"

# With specific model
gemini -m gemini-2.5-pro -p "your prompt here"

# JSON output (for parsing)
gemini -o json -p "your prompt here"

# Feed files via @ syntax (uses Gemini's massive context window)
gemini -m gemini-2.5-pro -p "review this" @src/

# Pipe content via stdin
cat file.md | gemini -p "review this"

# Background (non-blocking)
gemini -p "review" < draft.md > /tmp/review.json &
```

### Correct flags

| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Non-interactive headless mode |
| `-m model` | Model override (default: gemini-2.5-flash) |
| `-o json` | JSON output with stats |
| `-o text` | Plain text output (default) |
| `@path` | Inject file/directory into context |
| `--yolo` | Auto-approve tool calls |

Do NOT use `--json_output`, `--model`, `--prompt`, or other invented flags. The above are the only valid options.

### When to use

Gemini is a **peer reviewer**, not a replacement. Use it to:
- Validate analysis outputs (patterns, architecture, debt scores)
- Catch factual errors in narratives
- Get a second opinion on architectural assessments

Always run in background when possible. Incorporate valid critiques, ignore opinions that contradict tool evidence (ast-grep/semgrep matches outweigh Gemini opinions).
