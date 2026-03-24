# Recall System

Everything in kordinate — identity, skills, memory, contracts — is knowledge. The recall system defines how knowledge is stored, loaded, and discovered.

## Properties

Every piece of knowledge is described by seven properties:

| Property | Question | Values | Default |
|----------|----------|--------|---------|
| **Description** | What is this? | one-line text | required |
| **Templated** | Does it follow a template? | `none` / `<template>` | `none` |
| **Curated** | Updated only when explicitly requested? | `true` / `false` | `false` |
| **Preloaded** | Loaded at startup? | `true` / `false` | `false` |
| **Owner** | Who owns it? | `team` / `agent` | `agent` |
| **Scope** | Where does it apply? | `global` / `project` | `global` |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` |

- Every file must have a **description** — a one-line summary of its content.
- **Curated** files are not auto-updated by agents. Changes only happen when a human explicitly requests them.
- **Templated** non-curated files can be written by their owning agent but must follow the referenced template.
- Any file can have `scope: project`. Project-scoped files live under `<project>/.kord/` instead of `~/.kord/`.

All properties live in `MAP.md` — the single registry for all knowledge. Not in per-file frontmatter.

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
