---
name: onboard
description: Add a new agent or sync existing agents to the runtime. Creates identity, kord entry, memory, and KORD.md registration.
argument-hint: "<agent-name> or sync"
---

Onboard agents into the team. Two modes:

- `/scribe:onboard <name>` — create a new agent from scratch
- `/scribe:onboard sync` — sync all existing kordinate agents to the current runtime

## New Agent

$ARGUMENTS should include the agent name and optionally a description.

1. **Gather information** — parse from arguments or ask:
    - Agent name (required, kebab-case)
    - One-line description (required)
    - Tools (optional, defaults to standard set)
    - Kord expertise — what this agent provides when consulted (required)

2. **Create agent directory** in kordinate:
    ```
    $KORDINATE_HOME/agents/<name>/
    ├── identity.md
    ├── skills/
    └── memory/
        └── scratchpad.md
    ```

3. **Generate identity.md** — see [identity-template.md](../remember/identity-template.md) for the template. Add frontmatter properties (`curated: true`, `scope: global`).

4. **Generate scratchpad.md** with empty frontmatter (`curated: false`, `scope: global`).

5. **Create default kord** — use `/scribe:kord default-<name>` with the expertise from step 1.

6. **Sync to runtime** — write the agent to the runtime's native paths.
    See [claude-native.md](../remember/claude-native.md) for the current runtime.

7. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

8. **Report** what was created.

## Sync Existing

When called with `sync`, read all agents from `$KORDINATE_HOME/agents/` and ensure each one exists in the runtime's native paths. This is useful after:

- First install
- Adding an agent manually
- Switching runtimes

For each agent found in kordinate:

1. Read `identity.md`
2. Write to the runtime's native agent path
3. Ensure memory paths exist in the runtime
4. Report what was synced
