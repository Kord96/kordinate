# Identity Template

Level 3 resource for the onboard skill.

## Template

```markdown
---
name: <agent-name>
description: <one-line role description>
tools: [Read, Edit, Write, Bash, Glob, Grep]
model: inherit
memory: user
---

# <Agent Name>

<Role description.>

## Workflow

1. <step>
2. <step>

## Rules

- Read your memory before every operation
- Never write .md files directly — delegate to scribe
- <agent-specific rules>

## Consultation

<What this agent provides when consulted.> See kords: `default-<name>`.
```

## Field Notes

- `name`: lowercase, hyphens only
- `description`: one line, used by Claude to decide when to delegate
- `tools`: list only what the agent needs
- `model`: usually `inherit` (uses parent's model)
- `memory: user` for global persistence, `memory: project` for project-only
