---
name: register
description: Register a new agent or kord, or sync existing agents to the runtime.
argument-hint: "<agent-name> | kord <kord-name> | --sync"
curated: true
scope: global
---

Add a new kordinate agent, define a new kord, or sync existing agents to the Claude Code runtime.

Authenticate before writing: use `/authenticate`.

## Modes

- **New agent**: `/register <name>` -- creates agent directory, identity, default kord, and links to runtime. See [new-agent.md](new-agent.md).
- **New kord**: `/register kord <name>` -- defines a new consultation contract between agents. See [create-kord.md](create-kord.md).
- **Sync**: `/register --sync` or `/register --sync <name>` -- re-links existing agents to the runtime after kordinate changes. Runs the linking procedure in [link.md](link.md) without creating new agent directories.

## Procedure

1. **Parse arguments** -- if `kord`, follow [create-kord.md](create-kord.md). If `--sync`, skip to step 3. Otherwise, proceed with new agent creation.

2. **Create new agent** -- follow [new-agent.md](new-agent.md) to create the agent directory, IDENTITY.md, scratchpad, and default kord.

3. **Link to runtime** -- write agent files to Claude Code's native paths per [link.md](link.md). For `--sync` without a name, re-link all agents. For `--sync <name>`, re-link only that agent.

4. **Verify** -- run through [claude-checklist.md](claude-checklist.md) to confirm the integration is correct. For quick automated verification, run [smoke-test.sh](smoke-test.sh).
