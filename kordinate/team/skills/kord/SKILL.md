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

## Lifecycle wrapper

When spawning an agent locally, **always wrap the original prompt** with lifecycle instructions. The agent's prompt must be:

```
Follow this lifecycle exactly:

1. BOOT — run /boot to load your identity and preloaded memory.
2. WORK — execute the task below. When your skill procedure tells you to validate, delegate to warden via kord.
3. VALIDATE — before finishing, delegate to warden to validate your output. Do this at least once even if your skill didn't explicitly ask for it. If warden reports errors, fix them and validate again until it passes.
4. SLEEP — save any new insights worth keeping to memory files in your memory directory.

## Task

<original prompt from MCP response>
```

Never pass the raw prompt to the agent. The wrapper ensures the agent loads its skills, validates output, and saves memory.
