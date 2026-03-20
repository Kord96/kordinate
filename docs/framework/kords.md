# Kords

A **kord** is a single consultation link between two agents — not the entire relationship, but one specific thing one agent provides to another. Two agents can be linked by multiple kords, each addressing a different need.

A kord defines the **template** of a response (like a class). The cache file holds the **actual response** (like an instance). A default kord exists for free-form inquiries that don't fit a specific template.

## Ownership & Structure

Root owns all kord definitions centrally in `agents/root/kords/`. Each kord is its own directory. A registry file lists all agents with brief descriptions.

**Naming:** directories named `<consulter>-<consultant>-<topic>/` — Default kords: `default-<consultant>/`. Each directory contains `kord.md` (definition), `freshness.sh` (script called directly by `/consult`), and `cache` (the cached response).

```
agents/root/kords/
├── registry.md
├── deployer-designer-pattern-review/
│   ├── kord.md          # definition (template, guidelines, rules)
│   ├── freshness.sh     # script, called directly by /consult
│   └── cache            # the cached response
├── deployer-designer-architecture-constraints/
│   ├── kord.md
│   ├── freshness.sh
│   └── cache
└── default-designer/
    ├── kord.md
    ├── freshness.sh
    └── cache
```

## Kord as Multi-Reader Source of Truth

A kord directory contains files read by different agents at different times:

| Reader | Extracts | Purpose |
|--------|----------|---------|
| `/consult` | `freshness.sh` | Check cache cheaply — no need to read `kord.md` |
| Consulter | Template from `kord.md` | Know what shape of response to expect (only when needed) |
| Consultant | Guidelines, Rules from `kord.md` | Know how to answer, evaluate deeper freshness |
| `/scribe:kord` | All fields in `kord.md` | Create/edit the full definition |

The primary cheap check is `freshness.sh` directly — the kord definition (`kord.md`) is only read when the consultant is actually spawned.

## Definition Fields

| Field | Reader | Description |
|-------|--------|-------------|
| **Consulter** | Both | Agent asking |
| **Consultant** | Both | Agent answering |
| **Provides** | Both | What this kord delivers |
| **Template** | Consulter | Shape of the expected response |
| **Guidelines** | Consultant | How to answer — sources, format, constraints |
| **Rules** | Consultant | Deeper freshness logic, cross-kord invalidation |

??? example "deployer → designer: pattern review"

    ```markdown
    # Kord: deployer → designer (pattern review)

    | Field | Value |
    |-------|-------|
    | **Consulter** | deployer |
    | **Consultant** | designer |
    | **Provides** | Pattern compliance review for a proposed deployment |

    ## Template

    - **Compliant patterns:** list
    - **Violations:** list with severity
    - **Suggestions:** optional remediation steps

    ## Guidelines

    Check the deployment manifest against the pattern library in
    `agents/designer/patterns/`. Report violations by severity
    (blocking, warning, info). Keep response under 40 lines.

    ## Rules

    Stale when any file in `agents/designer/patterns/` changes.
    Invalidates `deployer-designer-architecture-constraints` if
    a blocking violation is found.
    ```

## Flow

1. `/consult` calls `freshness.sh` directly — no need to read `kord.md` first.
2. Fresh → read cache. Stale or missing → spawn consultant.
3. Consultant reads `kord.md` for guidelines and rules, produces response, writes cache.

```mermaid
flowchart TB
    C[/consult] --> F[freshness.sh]
    F -->|fresh| CA[cache]
    F -->|stale| A[Consultant]
    A -->|reads| K[kord.md]
    A --> CA
```

## Freshness & Invalidation

Four layers, from cheapest to most disruptive:

| Layer | Trigger | Who runs it |
|-------|---------|-------------|
| **`freshness.sh`** | On consult — called directly, no spawn needed | `/consult` (passive) |
| **Rules** | When consultant is already spawned for another reason | Consultant (opportunistic) |
| **`/invalidate`** | User manually forces stale | User |
| **Event-driven** | Hooks (e.g., post-deploy) invalidate specific kords | System |

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

Agents discover their kords through three mechanisms:

1. **Dynamic memory file** — a script scans `agents/root/kords/` for kords involving the agent and generates a summary of available kords and connected agents.
2. **Hook on kord directory** — fires when any file in `agents/root/kords/` changes, regenerating the dynamic memory file.
3. **Guard** — blocks the agent from acting until it re-reads the updated memory file.

No staleness, no injection timing issues. The guard ensures agents never act on outdated kord knowledge.
