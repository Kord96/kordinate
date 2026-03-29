---
name: kord
description: Route a request to another agent. Uses the kord MCP server for delegation.
argument-hint: "<agent> <message>"
---

Route a request to another agent via the kord MCP server. The server reads KORD.json to find the right agent and skill.

## Usage

```
/kord augur analyze /path/to/project
/kord sauron monitor myproject --diagnose "API returning 503s"
/kord alfred get config home
/kord warden validate /path/to/memory/
/kord scribe doctor-k --scope global
```

## Resolution

1. Parse `<agent>` and `<message>` from `$ARGUMENTS`.
2. Call the kord MCP delegate tool: `mcp__kord__delegate` with `agent`, `caller: main`, and `prompt`.
3. The MCP returns either:
   - `local: true` + gate secret → write the gate secret, spawn the agent locally via Agent tool.
   - A direct response (for lightweight/cached queries).

## Lifecycle

When spawning an agent (local or remote), the agent should:

1. **Boot** — run `/boot` to load preloaded memory from KORD.json.
2. **Work** — execute the requested task.
3. **Remember** — if new memory files were written, they'll be picked up by the nudge hook. The agent doesn't need to call `/remember` explicitly — the hook handles registration after the session.
