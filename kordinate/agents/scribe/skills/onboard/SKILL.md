---
name: onboard
description: Add a new agent to the team or sync existing agents to the runtime.
argument-hint: "<agent-name> or sync"
curated: true
scope: global
---

Two modes:

- `/scribe:onboard <name>` — create a new agent. See [new-agent.md](new-agent.md).
- `/scribe:onboard sync` — sync all existing agents to runtime. See [sync.md](sync.md).

Authenticate before writing: use `/authenticate`.

After either mode, verify with [claude-checklist.md](claude-checklist.md).
