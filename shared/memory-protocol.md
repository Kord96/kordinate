---
description: Instructs agents to save insights to memory before finishing
---

Before finishing your task, save any new insights worth keeping. Write memory files directly, then run `/remember` to register them in KORD.json (scope, preload, owner).

Examples of things worth remembering:
- Facts about infrastructure, services, or configurations you discovered
- Patterns or anti-patterns you identified
- Workarounds for issues you encountered
- Decisions that were made and why

Don't remember:
- Ephemeral task details (what you were asked to do this time)
- Information already in git (code changes, commit history)
- Things derivable from running a command

