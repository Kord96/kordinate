# Scribe

Documentation gate — the sole agent authorized to write structured files. All other agents delegate structured edits to scribe.

## How It Works

When any agent attempts to write a structured file:

1. Guard hook fires
2. Checks file against registered structured patterns
3. No scribe auth token → blocked, told to delegate to scribe
4. Scribe auth token present → validates against template → allows

Scribe authenticates once per task, performs all writes, removes auth token.

## Structured Files

| File | Path | Purpose |
|------|------|---------|
| identity | `<agent>/identity.md` | Agent role, tools, workflow, rules |
| skill | `<agent>/skills/<name>/SKILL.md` | Skill definition |
| contract | `team/kords/<name>/contract.md` | Consultation protocol |
| data | `team/kords/<name>/data.md` | Cached kord result |
| MAP | `MAP.md` | Root router — lists agents, memory, kords |

??? note "Templates"

    === "identity.md"

        ```markdown
        ---
        name: <agent-name>
        description: <one-line role description>
        tools: [Read, Edit, Write, Bash, Glob, Grep]
        model: inherit
        ---

        # <Agent Name>

        <Role description.>

        ## Workflow

        1. <step>
        2. <step>

        ## Rules

        - <rule>
        ```

    === "SKILL.md"

        ```markdown
        ---
        name: <skill-name>
        description: <one-line description>
        allowed-tools: [Read, Edit, Bash, Glob]
        ---

        <Instructions for the skill.>
        ```

    === "contract.md"

        ```markdown
        ---
        description: <what this kord provides>
        requester: <agent or "any">
        provider: <agent>
        ---

        ## Provider Guidelines

        <Instructions for how the provider should respond.>

        ### Response Format

        | Field | Required |
        |-------|----------|
        | <field> | yes/no |

        ## Provider State Invalidation

        Invalidate when:
        - <condition>
        ```

    === "data.md"

        Follows the Response Format from the kord's `contract.md`:

        ```markdown
        <field>: <value>
        <field>: <value>
        ```

    === "MAP.md"

        ```markdown
        - [<agent>/identity.md](<agent>/identity.md) — <description>
        - [team/memory/<topic>.md](team/memory/<topic>.md) — <description>
        - [team/kords/<name>/contract.md](team/kords/<name>/contract.md) — <description>
        ```
