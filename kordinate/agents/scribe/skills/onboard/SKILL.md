---
name: onboard
description: Add a new agent or sync existing agents to the runtime. Use when creating a new agent, linking agents after updates, or verifying the kordinate-to-Claude-native integration.
argument-hint: "<agent-name> | --sync"
curated: true
---

Add a new kordinate agent or sync existing agents to the Claude Code runtime.

Authenticate before writing: use `/authenticate`.

## Modes

- **New agent**: `/onboard <name>` -- creates agent directory, identity, default kord, and links to runtime. See [new-agent.md](new-agent.md).
- **Sync**: `/onboard --sync` or `/onboard --sync <name>` -- re-links existing agents to the runtime after kordinate changes. Runs the linking procedure in [link.md](link.md) without creating new agent directories.

## Procedure

1. **Parse arguments** -- if `--sync`, skip to step 3. Otherwise, proceed with new agent creation.

2. **Create new agent** -- follow [new-agent.md](new-agent.md) to create the agent directory, IDENTITY.md, scratchpad, and default kord.

3. **Link to runtime** -- write agent files to Claude Code's native paths per [link.md](link.md). For `--sync` without a name, re-link all agents. For `--sync <name>`, re-link only that agent.

4. **Verify** -- run through [claude-checklist.md](claude-checklist.md) to confirm the integration is correct. For quick automated verification, run [smoke-test.sh](smoke-test.sh).
