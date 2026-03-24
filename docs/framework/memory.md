# Recall System

## Memory Properties

Every piece of knowledge in kordinate is described by five properties:

| Property | Question | Values | Default |
|----------|----------|--------|---------|
| **Structured** | Does it follow a template? | `true` / `false` | `false` |
| **On-demand** | Preloaded or read when needed? | `true` / `false` | `true` |
| **Owner** | Who owns it? | `team` / `agent` | `agent` |
| **Scope** | Where does it apply? | `global` / `project` | `global` |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` |

Files with no frontmatter use the defaults. Override any property in YAML frontmatter.

### Constraints

- **Structured** files can only be written by [scribe](../agents/scribe.md). See [Guards](guards.md) for enforcement details.
- **On-demand** files must be listed in `MAP.md` to be discoverable.

## MAP.md

`MAP.md` lives at `~/.kord/MAP.md` — the single entry point. Lists all agents, team memory, and kords with descriptions. Auto-generated, never manually edited.

Generation:

1. Scan `~/.kord/` for known patterns (`*/identity.md`, `*/memory/*.md`, `team/kords/*/contract.md`)
2. Read `name` and `description` from each file's frontmatter
3. Write one line per file to `MAP.md`

Runs as a hook on structured file writes, or on demand via `/scribe:map`.

## Framework Memories

=== "Agent"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | identity | `<agent>/identity.md` | Role, tools, auth, workflow, rules | yes | no | — |
    | skills | `<agent>/skills/<name>/SKILL.md` | Skill definitions | yes | yes | — |
    | memory | `<agent>/memory/*.md` | Domain knowledge, notes, findings | varies | yes | varies |

=== "Team"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | shared knowledge | `team/memory/*.md` | Team-wide conventions, standards | varies | varies | varies |
    | contract | `team/kords/<name>/contract.md` | Consultation protocol | yes | yes | — |
    | data | `team/kords/<name>/data.md` | Cached result | yes | yes | `team/kords/<name>/expiry.sh` |

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.

## Structured Files

| File | Path | Purpose |
|------|------|---------|
| identity | `<agent>/identity.md` | Agent role, tools, workflow, rules |
| skill | `<agent>/skills/<name>/SKILL.md` | Skill definition |
| contract | `team/kords/<name>/contract.md` | Consultation protocol |
| data | `team/kords/<name>/data.md` | Cached kord result |
| MAP | `MAP.md` | Root router — auto-generated from frontmatter |

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
