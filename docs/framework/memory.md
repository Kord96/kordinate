# Recall System

## Memory Properties

Every piece of knowledge in kordinate is described by five properties:

| Property | Question | Default | Override |
|----------|----------|---------|----------|
| **Structured** | Does it follow a template? | no | `structured: true` |
| **On-demand** | Preloaded or read when needed? | yes (on-demand) | `on-demand: false` → preloaded |
| **Owner** | Who owns it? | agent | `owner: team` |
| **Scope** | Where does it apply? | global | `scope: project` |
| **Expiry** | Does it expire? | no (always valid) | `expiry: <script>` |

### Constraints

- **On-demand files must be referenced** by at least one preloaded document (identity, kord, command, etc.). Orphaned on-demand files are dead knowledge — no agent will ever find them.
- **Structured files** are validated on write. The template defines what valid content looks like.

### Always Structured

These always follow a template — kordinate enforces this:

- **Identity** (agent or team)
- **Kords** (both contract and cached result)

Everything else: the user decides whether to make it structured or free-form.

---

!!! warning "Work in progress"
    The knowledge model below is stale and being redesigned around the five properties above.

## Knowledge Model (legacy)

Each agent's knowledge is organized on two axes — **scope** and **mutability**:

| | Static | Dynamic |
|---|---|---|
| **Global** | `agents/<agent>/memory/static/` | `agents/<agent>/memory/dynamic/` |
| **Project** | `<project>/<agent>/static/` | `<project>/<agent>/dynamic/` |

**Static** — curated, committed. Includes both domain knowledge (patterns, infra docs) and procedures (instructions for consultation, workflow, auth). Pre-defined structure.

**Dynamic** — free-form, auto-managed. Operational notes, consultation caches, session findings.
