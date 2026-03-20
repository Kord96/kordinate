# Memory & Cache

Every agent has two layers: **identity** (KORD.md) and **knowledge** (structured memory with caching).

## KORD.md — Identity

Each agent's `KORD.md` defines who it is. Read once, rarely changes.

| Section | What it contains |
|---------|-----------------|
| **Description** | One-line role definition |
| **Commands** | Slash commands the agent owns |
| **Rules** | Behavioral constraints |
| **Consultation** | What it answers when consulted |
| **Cache Sources** | What files define this agent's knowledge freshness |

Root agent's `KORD.md` additionally contains the team routing table and team-wide rules inherited by all subagents.

## Per-Agent Knowledge

Each agent's knowledge is organized on two axes — **scope** and **mutability**:

| | Static | Dynamic |
|---|---|---|
| **Global** | `agents/<agent>/memory/static/` | `agents/<agent>/memory/dynamic/` |
| **Project** | `<project>/<agent>/static/` | `<project>/<agent>/dynamic/` |

**Static** — curated, committed. Includes both domain knowledge (patterns, infra docs) and procedures (instructions for consultation, workflow, auth). Pre-defined structure.

**Dynamic** — free-form, auto-managed. Operational notes, consultation caches, session findings.

### Agent skeleton

```
agents/<agent>/
├── KORD.md                        # identity + cache sources
├── memory/
│   ├── static/
│   │   ├── instructions/          # procedures (consultation, workflow, auth, tools)
│   │   └── ...                    # domain knowledge (infra.md, patterns/, etc.)
│   └── dynamic/                   # auto-managed (operational notes, caches)
└── commands/                      # slash command definitions
```

Project-level:

```
<project>/<agent>/
├── static/                        # project artifacts (manifests, dashboards)
└── dynamic/                       # project notes (operational findings)
```

How these files are loaded into the runtime is handled by the [linking layer](../reference/linking.md#memory-mapping).

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
