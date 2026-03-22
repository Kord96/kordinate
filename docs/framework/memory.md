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

- **On-demand files must be indexed** in the agent's `index.md`. Orphaned on-demand files are dead knowledge.
- **Structured files** are validated on write. The template defines what valid content looks like.
- **`index.md`** is auto-generated per agent. Lists all on-demand files available. Preloaded so the agent knows what to look for.

## Framework Files

Files that ship with kordinate and their properties:

### Team

| File | Structured | On-demand | Owner | Scope | Expiry |
|------|:----------:|:---------:|:-----:|:-----:|:------:|
| team identity | yes | no | team | global | — |
| kord contract (`kord.md`) | yes | yes | team | global | — |
| kord cache (consultation result) | yes | yes | team | global | `pre-consult.sh` |
| kord registry | yes | no | team | global | — |

### Agent

| File | Structured | On-demand | Owner | Scope | Expiry |
|------|:----------:|:---------:|:-----:|:-----:|:------:|
| `identity.md` | yes | no | agent | global | — |
| `index.md` | yes | no | agent | global | — |
| `commands/*.md` | yes | yes | agent | global | — |
| `instructions/*.md` | no | yes | agent | global | — |
| `memory/static/*.md` | no | yes | agent | global | — |
| `memory/dynamic/*.md` | no | yes | agent | global | — |
| consultation cache | yes | yes | agent | global | `pre-consult.sh` |
| operational notes | no | yes | agent | global | — |

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.

## Index

Each agent has an `index.md` — auto-generated, preloaded, structured. It lists all on-demand files the agent has access to:

```markdown
---
structured: true
on-demand: false
---

| File | Description |
|------|-------------|
| memory/static/infra.md | Infrastructure reference |
| memory/static/migration.md | Migration procedures |
| instructions/auth.md | Authentication rules |
```

The agent sees this on spawn, knows what's available, reads specific files when needed.

**Dead-end detection**: scan on-demand files, compare to index, flag anything missing.
