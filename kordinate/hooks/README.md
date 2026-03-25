# Hooks

Pre/post-tool hooks that enforce domain boundaries and automate workflows. Configured in `settings.json`.

## Guards

Guards block operations unless the responsible agent has authenticated (lock file in `/tmp/`).

| Hook | Protects | Auth required | Trigger |
|------|----------|---------------|---------|
| [guard-kubectl.sh](guard-kubectl.sh) | kubectl write operations | `/tmp/.deployer-auth` | Bash (PreToolUse) |
| [guard-git.sh](guard-git.sh) | git push to test/prod | `/tmp/.deployer-auth` | Bash (PreToolUse) |
| [guard-grafana.sh](guard-grafana.sh) | Grafana MCP, dashboard JSON, API calls | `/tmp/.sauron-auth` | Edit/Write + Bash (PreToolUse) |
| [guard-md.sh](guard-md.sh) | .md file edits (except agent-memory) | `/tmp/.scribe-auth` | Edit/Write (PreToolUse) |

## Automation

| Hook | Purpose | Trigger |
|------|---------|---------|
| [agent-memory.sh](agent-memory.sh) | Regenerate agent MEMORY.md on spawn (hash-based caching) | Agent (PreToolUse) |
| [auto-merge-to-dev.sh](auto-merge-to-dev.sh) | Fast-forward session branches to main after push | Bash (PostToolUse) |
