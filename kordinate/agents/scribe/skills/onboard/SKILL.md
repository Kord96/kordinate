---
name: onboard
description: Add a new agent to the team. Creates identity, Claude native agent file, kord entry, and KORD.md registration.
---

Onboard a new agent. $ARGUMENTS should include the agent name and optionally a description.

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Agent name (required, kebab-case)
    - One-line description (required)
    - Tools (optional, defaults to standard set)
    - Kord expertise — what this agent provides when consulted (required)

2. **Create agent directory:**
    ```
    agents/<name>/
    ├── identity.md
    ├── skills/
    └── memory/
    ```

3. **Generate identity.md** — see [identity-template.md](../remember/identity-template.md) for the template.

4. **Write Claude native agent file** — see [claude-native.md](../remember/claude-native.md) for how to map identity.md to `~/.claude/agents/<name>.md`.

5. **Create default kord** — use `/scribe:kord default-<name>` with the expertise from step 1.

6. **Update KORD.md** — add the new agent's identity and any memory files.

7. **Report** what was created.
