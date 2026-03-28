# Identity Template

Level 3 resource for the register skill.

## Template

```markdown
---
name: <agent-name>
description: <one-line role description>
tools: [Read, Edit, Write, Bash, Glob, Grep]
model: inherit
color: <color>
memory: user
curated: true
preloaded: <agent-name>
scope: global
---

# <Agent Name>

<Role description.>

## Skills

| Skill | Purpose | Kord mode |
|-------|---------|-----------|

## Capabilities

- Can <testable action> via <skill or mechanism>
- Can <testable action> via <skill or mechanism>

## Rules

- Never write to kordinate or memory paths directly — use /kord remember
- <agent-specific rules>

## Consultation

<What this agent provides when consulted.> See kords: `<name>-default`.
```

## Field Notes

- `name`: lowercase, hyphens only — must match filename
- `description`: one line — Claude uses this to decide when to delegate
- `tools`: list only what the agent needs
- `model`: usually `inherit` (uses parent's model)
- `memory: user` for global persistence via Claude native fallback
- `curated: true`, `preloaded: <name>`, `scope: global` — kordinate properties (stripped during sync to Claude native)
- `Capabilities`: testable assertions about what the agent can do. Used by `/eval health --e2e` for per-agent verification. Each entry: "Can <action> via <skill>". Only include capabilities that can be mechanically tested.
