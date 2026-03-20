# 2D Memory

How agents store and discover knowledge. Two layers — shared (framework) and per-agent (2D model) — assembled at spawn time.

## Shared Memory

Common rules and the consultation directory injected into **every** agent's MEMORY.md:

```
agents/shared/
├── MEMORY.md                    # rules, conventions, consultation directory
└── memory/dynamic/              # consultation cache files
```

This is the framework base layer — every agent gets it regardless of their role.

## Per-Agent Memory

Each agent's own knowledge is organized on two axes — **scope** and **mutability**:

| | Static (pre-defined structure) | Dynamic (free-form) |
|---|---|---|
| **Global** | `agents/<agent>/memory/static/` | `agents/<agent>/memory/dynamic/` |
| **Project** | `<project>/<agent>/static/` | `<project>/<agent>/dynamic/` |

**Static** holds content with pre-defined structure — pattern definitions, infrastructure docs, dashboard schemas. Committed and reviewed.

**Dynamic** holds free-form agent notes — operational findings, session state, consultation caches. Auto-managed by agents.

The linking layer maps dynamic dirs into the runtime's expected paths:

```mermaid
flowchart LR
    subgraph global[Global]
        GS[agents/sauron/memory/static]
        GD[agents/sauron/memory/dynamic]
    end

    subgraph project[Project]
        PS[sauron/static]
        PD[sauron/dynamic]
    end

    GD -.-|symlink| GAM["~/.claude/agent-memory/sauron"]
    PD -.-|symlink| PAM[".claude/agent-memory/sauron"]
```

=== "Global"

    ```
    agents/<agent>/
    ├── AGENT.md              # role, commands, rules
    ├── instructions/         # procedures (workflow, auth, tools)
    ├── memory/
    │   ├── static/           # pre-defined structure
    │   └── dynamic/          # free-form (auto-generated MEMORY.md, notes)
    └── commands/             # slash command definitions
    ```

=== "Project"

    ```
    <project>/<agent>/
    ├── static/               # pre-defined structure (manifests, dashboards)
    └── dynamic/              # free-form (operational notes, findings)
    ```

## Assembly

At spawn time, `agent-memory.sh` combines shared + per-agent into a single `MEMORY.md`:

```mermaid
flowchart TD
    SP[agent spawn] --> HC{sources changed?}
    HC -->|no| SK[skip — cached MEMORY.md is fresh]
    HC -->|yes| GEN[regenerate MEMORY.md]
    GEN --> ST[store new hash]
    ST --> SK
```

??? info "What gets assembled"

    | Source | How it's included |
    |--------|------------------|
    | `shared/MEMORY.md` | Always inlined — shared rules for all agents |
    | `instructions/*.md` | Always inlined — agent-specific procedures |
    | `memory/static/*.md` | Inlined if ≤500 lines, indexed if larger |
    | Previous `## Notes` | Preserved — Claude's auto-managed section |

    The agent gets full context on startup without needing to read files itself.

## Cache System

The `lib/cache.sh` library provides hash-based invalidation — a primitive used across the framework to detect when source files have changed.

```mermaid
flowchart LR
    S[source dirs] --> H[MD5 hash<br/>all files]
    H --> C{matches<br/>stored hash?}
    C -->|yes| F[fresh — skip]
    C -->|no| R[stale — regenerate]
    R --> W[store new hash]
```

| Function | Purpose |
|----------|---------|
| `cache_hash <dirs...>` | Compute MD5 of all files in given directories |
| `cache_check <hash_file> <dirs...>` | Returns 0 if fresh, 1 if stale |
| `cache_store <hash_file> <dirs...>` | Store current hash |
| `cache_invalidate <hash_file>` | Remove hash to force regeneration |

=== "Memory regeneration"

    `agent-memory.sh` hashes `shared/MEMORY.md` + `instructions/` + `memory/static/`. If stale, regenerates the agent's `MEMORY.md`. Hash stored at `memory/dynamic/.hash`.

=== "Consultation"

    `/consult` hashes the consultant's source dirs. If stale, re-spawns the agent. `/invalidate <agent>` forces re-consultation.

=== "Doc audit"

    `/scribe:audit-docs` hashes implementation source files mapped in `docs/.source-map.yaml`. If stale, flags the doc page for review.
