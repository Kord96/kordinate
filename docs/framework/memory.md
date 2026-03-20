# 2D Memory

Every agent has two layers: **identity** (KORD.md) and **knowledge** (2D memory).

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

Each agent declares its cache sources in `KORD.md` — the files that define its knowledge freshness. When these change, the agent's cached outputs (memory, consultation answers) need refreshing.

Each agent owns a **refresh hook** (`hooks/refresh.sh`) that receives the changed file path and decides whether the change warrants a cache refresh. The framework calls this hook after edits; the agent's logic determines significance.

```
KORD.md:
  ## Cache Sources
  - memory/static/
  - manifests/

  Refresh: hooks/refresh.sh
```

What gets cached:

| What | Where |
|------|-------|
| Assembled memory (static → MEMORY.md) | `memory/dynamic/` |
| Consultation answers | consultation cache |

Manual override: `/invalidate <agent>` forces refresh regardless of hook decision.

| Function | Purpose |
|----------|---------|
| `cache_hash <dirs...>` | Compute MD5 of all files in given directories |
| `cache_check <hash_file> <dirs...>` | Returns 0 if fresh, 1 if stale |
| `cache_store <hash_file> <dirs...>` | Store current hash |
| `cache_invalidate <hash_file>` | Remove hash to force refresh |
