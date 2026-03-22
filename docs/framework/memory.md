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

- **On-demand files must be indexed** in the owner's `index.md`. Orphaned on-demand files are dead knowledge.
- **Structured files** are validated on write. The template defines what valid content looks like.
- **`index.md`** is auto-generated per owner (team and each agent). Lists all on-demand files. Preloaded so the agent knows what to look for.

## Framework Memories

Memories that ship with kordinate and their properties:

### Team

| File | Path | Purpose | Structured | On-demand | Expiry |
|------|------|---------|:----------:|:---------:|:------:|
| team index | `team/index.md` | Team roster — agents, shared rules, available kords | yes | no | — |
| kord contract | `team/kords/<name>/contract.md` | Consultation protocol between agents | yes | yes | — |
| kord data | `team/kords/<name>/data.md` | Cached result of a consultation | yes | yes | `expiry.sh` |
| kord registry | `team/kords/index.md` | Lists all available kords | yes | no | — |

### Agent

| File | Path | Purpose | Structured | On-demand | Expiry |
|------|------|---------|:----------:|:---------:|:------:|
| identity | `<agent>/identity.md` | Who the agent is — role, tools, auth, workflow, rules | yes | no | — |
| index | `<agent>/index.md` | Lists available on-demand files | yes | no | — |
| commands | `<agent>/commands/*.md` | Skill definitions — invoked by name | yes | yes | — |
| static knowledge | `<agent>/memory/static/*.md` | Curated domain knowledge | no | yes | — |
| dynamic memory | `<agent>/memory/dynamic/*.md` | Auto-managed notes and findings | no | yes | — |

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.

## Structured Templates

Every structured file follows a template. Scribe validates on write.

### team/index.md

```markdown
## Agents

| Agent | Role |
|-------|------|
| <name> | <one-line role> |

## Shared Rules

- <rule>

## Kords

| Kord | Provider |
|------|----------|
| <name> | <agent> |
```

### identity.md

```markdown
---
name: <name>
model: <model>
tools: [<tool>, ...]
triggers: ["<trigger>", ...]
---

# <Name>

<one-line description>

## Auth

<authentication procedures for protected operations>

## Workflow

<step-by-step procedure when triggered>

## Rules

- <rule>

## Consultation

<what this agent answers when consulted>
```

### commands/*.md

```markdown
<one-line description>

**Input**: $ARGUMENTS (<usage>)

## Procedure

1. <step>
2. <step>
```

### kord contract.md

```markdown
---
description: <one-line>
requester: <agent(s)>
provider: <agent>
---

## Provider Guidelines

<behavioral instructions>

### Response Format

| Field | Required |
|-------|----------|
| <field> | yes/no |

## Provider State Invalidation

Invalidate when:
- <condition>
```

### kord data.md

Follows the Response Format defined in the kord's `contract.md`.

### index.md (agent)

```markdown
| File | Description |
|------|-------------|
| <path> | <one-line purpose> |
```

## Index

Each owner (team and each agent) has an `index.md` — auto-generated, preloaded, structured. Lists all on-demand files available.

The agent sees this on spawn, knows what's available, reads specific files when needed.

**Dead-end detection**: scan on-demand files, compare to index, flag anything missing.
