---
description: Scribe authentication and write workflow
curated: true
scope: global
---
# Workflow

1. **Authenticate** — once per invocation, not per file:
   1. `cp profile/locks/scribe /tmp/.scribe-auth`
   2. Perform ALL Edit/Write operations for the entire task
   3. `rm /tmp/.scribe-auth` only when all writes are complete

   Never cp/rm per file. Authenticate once and batch all writes.

2. **Classify the request** — profile doc edit or project doc edit?

3. **Profile doc edits** — match to a command:

   | Request contains | Command file |
   |-----------------|-------------|
   | new MCP, new tool | `commands/scribe/add-mcp.md` |
   | agent docs | `commands/scribe/update-agent-docs.md` |
   | agent memory | `commands/scribe/update-subagent-memory.md` |
   | project docs, README | `commands/scribe/update-project-docs.md` |

4. **Project doc edits** — follow caller's instructions directly.

5. **Review gate** — validate changes using Gemini MCP before committing.

6. **Commit** — with `[scribe]` in the message.
