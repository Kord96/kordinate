---
name: register
description: Register a runtime, agent, or kord — or re-link after changes.
argument-hint: "runtime [--dev <path>|--from <url>] | agent <name> | kord <name> | --link [<name>]"
---

One-time runtime setup, new agent/kord creation, or re-linking after kordinate changes.

Authenticate before writing: use `/authenticate`.

## Modes

- **Runtime**: `register runtime [--dev <path>|--from <url>]` -- one-time setup: detect runtime, pull package, link, optional backup. See [runtime.md](runtime.md).
- **Runtime (dev)**: `register runtime --dev <path>` -- developer mode: use local repo as package source, install auto-sync hook.
- **New agent**: `register agent <name>` -- creates agent directory, identity, default kord, and links to runtime. See [new-agent.md](new-agent.md).
- **New kord**: `register kord <name>` -- defines a new consultation contract between agents. See [create-kord.md](create-kord.md).
- **Link**: `register --link` or `register --link <name>` -- re-link existing agents to the runtime after kordinate changes. Runs the linking procedure in [link.md](link.md) without creating new agent directories.

## Procedure

1. **Parse arguments** -- route on the first argument:
   - `runtime` -- follow [runtime.md](runtime.md).
   - `kord` -- follow [create-kord.md](create-kord.md).
   - `--link` -- skip to step 3.
   - `agent` or bare `<name>` -- proceed with new agent creation.

2. **Create new agent** -- follow [new-agent.md](new-agent.md) to create the agent directory, IDENTITY.md, scratchpad, and default kord.

3. **Link to runtime** -- write agent files to Claude Code's native paths per [link.md](link.md). For `--link` without a name, re-link all agents. For `--link <name>`, re-link only that agent.

4. **Verify** -- run through [claude-checklist.md](claude-checklist.md) to confirm the integration is correct. For quick automated verification, run [smoke-test.sh](smoke-test.sh).
