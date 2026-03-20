# Memory & Cache

How agents store and discover knowledge. See [Architecture Overview](consultation.md#agent-structure) for KORD.md identity and the directory skeleton.

## Knowledge Model

Each agent's knowledge is organized on two axes — **scope** and **mutability**:

| | Static | Dynamic |
|---|---|---|
| **Global** | `agents/<agent>/memory/static/` | `agents/<agent>/memory/dynamic/` |
| **Project** | `<project>/<agent>/static/` | `<project>/<agent>/dynamic/` |

**Static** — curated, committed. Includes both domain knowledge (patterns, infra docs) and procedures (instructions for consultation, workflow, auth). Pre-defined structure.

**Dynamic** — free-form, auto-managed. Operational notes, consultation caches, session findings.

Project-level memory follows the same model:

```
<project>/<agent>/
├── static/                        # project artifacts (manifests, dashboards)
└── dynamic/                       # project notes (operational findings)
```

## Cache

Each agent declares its cache in `KORD.md`:

```
## Cache
- memory/static/
- manifests/

Refresh: hooks/refresh.sh
```

**Sources** — the dirs whose content defines the agent's knowledge. Rarely change.

**Refresh hook** — called with the changed file path after edits. The hook decides: is this change significant? Config tweak → skip. Infrastructure redesign → refresh.

If the hook says "refresh," **all** cached outputs from that agent are cleared: its assembled MEMORY.md and all consultation answers it previously gave. This is intentional — if an agent's knowledge changed significantly, every answer it gave is potentially stale.

| Cached output | Where it lives |
|---------------|---------------|
| Assembled memory | agent's `memory/dynamic/` |
| Consultation answers | root's `memory/dynamic/team/` |

Manual override: `/invalidate <agent>` forces refresh regardless of hook decision.
