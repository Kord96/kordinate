# Recall System

Everything in kordinate — identity, skills, memory, contracts — is knowledge. The recall system defines how knowledge is stored, loaded, and discovered.

## Properties

Every piece of knowledge is described by eight properties:

| Property | Question | Values | Default |
|----------|----------|--------|---------|
| **Path** | Where is it? | file path | required |
| **Name** | Short identifier | text | derived from path |
| **Description** | What is this? | one-line text | required |
| **Template** | Does it follow a template? | `none` / `<template>` | `none` |
| **Curated** | Updated only when explicitly requested? | `true` / `false` | `false` |
| **Preloaded** | Loaded at startup? | `true` / `false` | `false` |
| **Owner** | Who owns it? | `team` / `<kord>` / `<agent>` | `agent` |
| **Scope** | Where does it apply? | `global` / `project` | `global` |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` |

- **Curated** files are not auto-updated by agents. Changes only happen when a human explicitly requests them.
- **Template** files must follow the referenced template.
- **Scope**: `global` properties live in `~/.claude/kord/`. `project` properties live in `.claude/kord/`.

## KORD.md

`KORD.md` is the human-readable registry of all knowledge — maintained by scribe. A validation script parses it for the guard. If KORD.md is malformed, the guard blocks writes.

Only non-default values need to be specified.


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

    === "kord"

        **contract.md** — consultation protocol:

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

        **data.md** — follows the Response Format from contract.md:

        ```markdown
        <field>: <value>
        <field>: <value>
        ```

## Claude Code

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/CLAUDE.md` | Loaded into every session and inherited by all subagents. Developer-written. |
    | auto memory index | `~/.claude/projects/<project>/memory/MEMORY.md` | Per-project. Claude writes this itself. First 200 lines auto-loaded at startup. Acts as router to topic files. |
    | auto memory files | `~/.claude/projects/<project>/memory/*.md` | Per-project. Topic files — Claude reads these on-demand when it needs the information. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`) + markdown body as system prompt. |
    | auto memory index | `~/.claude/agent-memory/<name>/MEMORY.md` | First 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate. May support topic files (same architecture as main session). |
