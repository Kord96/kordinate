# Kords

A **kord** is a single consultation link between two agents — a template that defines one specific thing one agent provides to another. Two agents can be linked by multiple kords. A default kord exists for free-form queries.

## Two Concepts

| Concept | What it is | Where it lives | Nature |
|---------|-----------|----------------|--------|
| **Kord** | Template/protocol | `agents/root/kords/<name>/kord.md` | Static, root-owned |
| **Consultation result** | Actual knowledge from a consultation | `agents/<consulter>/memory/dynamic/consultations/<result>.md` | Dynamic, consulter-owned |

The kord is the template (like a class). The consultation result is the actual knowledge (like an instance).

## Structure

Root owns all kord definitions centrally. Each kord is a directory. A registry file lists all agents with brief descriptions.

**Naming:** `<consulter>-<consultant>-<topic>/` — Default kords: `default-<consultant>/`

```
agents/root/kords/
├── registry.md
├── deployer-designer-pattern-review/
│   ├── kord.md                              # template definition
│   └── freshness.sh                         # cheap freshness check
├── deployer-sauron-monitoring-impact/
│   ├── kord.md
│   └── freshness.sh
└── default-designer/
    ├── kord.md
    └── freshness.sh
```

Consultation results live in the consulter's dynamic memory:

```
agents/deployer/memory/dynamic/
└── consultations/
    ├── designer-pattern-review.md
    └── sauron-monitoring-impact.md
```

These are real knowledge — accessible anytime without `/consult`.

## Kord Definition

Each `kord.md` contains:

| Field | Description |
|-------|-------------|
| **Consulter** | Agent asking |
| **Consultant** | Agent answering |
| **Provides** | What this kord delivers |
| **Guidelines** | How to answer — sources, format, constraints |
| **Rules** | Deeper freshness logic, cross-kord invalidation |

??? example "deployer → designer: pattern review"

    ```markdown
    # Kord: deployer → designer (pattern review)

    | Field | Value |
    |-------|-------|
    | **Consulter** | deployer |
    | **Consultant** | designer |
    | **Provides** | Pattern compliance review for a proposed deployment |

    ## Guidelines

    Check the deployment manifest against the pattern library in
    `agents/designer/patterns/`. Report violations by severity
    (blocking, warning, info). Keep response under 40 lines.

    ## Rules

    Stale when any file in `agents/designer/patterns/` changes.
    Invalidates `deployer-designer-architecture-constraints` if
    a blocking violation is found.
    ```

## Who Reads What

| File | Who reads it | When |
|------|-------------|------|
| `freshness.sh` | Freshness Guard | Every consultation (pre-hook on `/consult`) |
| Consultation result | Consulter | Anytime (it's in its memory) |
| `kord.md` (Guidelines, Rules) | Consultant | When consulted for this kord |
| `kord.md` (Consulter, Consultant, Provides) | Consulter Awareness Script | When generating dynamic memory summary |

## Flow

1. Agent runs `/consult`
2. Freshness guard fires — runs `freshness.sh` from the kord directory
3. Fresh → guard blocks, agent reads result from its own dynamic memory
4. Stale → guard allows `/consult` to proceed, spawns consultant
5. Consultant reads `kord.md`, follows guidelines, produces result
6. Result written to consulter's `consultations/` directory

```mermaid
flowchart TB
    C[/consult] --> G{Freshness Guard}
    G -->|fresh — blocked| M[Read from memory]
    G -->|stale — allowed| A[Consultant]
    A -->|reads| K[kord.md]
    A -->|writes result| R[consultations/]
```

## Freshness & Invalidation

Four layers:

| Layer | Who runs it | When |
|-------|-------------|------|
| **Freshness Guard** | Pre-hook on `/consult` | Every consultation — runs `freshness.sh`, blocks if fresh |
| **Rules** (in `kord.md`) | Consultant | When already spawned — evaluates deeper freshness |
| **Event-driven** | Hooks | On events (e.g. post-deploy) invalidate specific kords |

## Using a Kord

=== "Explicit"

    Target a specific kord by name:

    ```
    /consult designer:pattern-review "is the sidecar compliant?"
    ```

=== "Default"

    Free-form question routed through the default kord:

    ```
    /consult designer "free-form question"
    ```

    Uses `default-designer/`.

## Agent Awareness

Agents know their kords without reading them on every action:

1. **Consulter Awareness Script** — scans `agents/root/kords/` for kords involving this agent, generates a summary in the agent's dynamic memory
2. **Hook on kord directory** — fires when any file in `agents/root/kords/` changes, regenerates the summary
3. **Guard** — blocks the agent from acting until it re-reads the updated summary

No staleness. The guard ensures agents never act on outdated kord knowledge.

??? note "Related commands"

    | Command | Purpose |
    |---------|---------|
    | `/scribe:kord deployer designer` | Create a new kord |
    | `/scribe:onboard designer` | Onboard a new agent |
    | `/consult designer:pattern-review "question"` | Consult via explicit kord |
    | `/consult designer "question"` | Consult via default kord |
