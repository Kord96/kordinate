---
description: Instructs agents to save insights to memory before finishing
preloaded: all
curated: true
scope: global
---

Before finishing your task, save any new insights worth keeping using the `write_memory` tool (provided by Beorn).

Scribe decides scope (global vs project) and where to write. You don't need to think about paths.

Examples of things worth remembering:
- Facts about infrastructure, services, or configurations you discovered
- Patterns or anti-patterns you identified
- Workarounds for issues you encountered
- Decisions that were made and why

Don't remember:
- Ephemeral task details (what you were asked to do this time)
- Information already in git (code changes, commit history)
- Things derivable from running a command
