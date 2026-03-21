# Kords

A **kord** is a single consultation link between two agents — a template that defines one specific thing one agent provides to another. Two agents can be linked by multiple kords. A default kord exists for free-form queries.

| Concept | What it is | Where it lives | Nature | Analogy |
|---------|-----------|----------------|--------|---------|
| **Kord** | Template/protocol | `agents/root/kords/<name>/kord.md` | Static, root-owned | class |
| **Consultation** | Actual knowledge | `agents/<requester>/memory/dynamic/consultations/<result>.md` | Dynamic, requester-owned | instance |

### Example

A deployer agent needs a design review before applying a manifest change:

```
/consult pattern-review "review the beorn deployment manifest for pattern violations"
```

`/consult` resolves the `pattern-review` kord, checks freshness, invokes the designer with the kord's guidelines, caches the response, and returns it. Next time the same question is asked with a fresh cache, the cached answer is returned instantly.

## Structure

Root owns all kord definitions. Each kord is a directory containing the definition and a freshness script. A registry file lists all agents with brief descriptions.

**Naming:** kord directories are named by topic. Default kords: `default-<provider>/`

```
agents/root/kords/
├── registry.md
├── pattern-review/
│   ├── kord.md                              # template definition
│   ├── freshness.sh                         # owned by provider
│   └── .valid                               # marker — deleted to invalidate
├── monitoring-impact/
│   ├── kord.md
│   └── freshness.sh
└── default-designer/
    ├── kord.md
    └── freshness.sh
```

Consultations live in the requester's dynamic memory:

```
agents/deployer/memory/dynamic/
└── consultations/
    ├── pattern-review.md
    └── monitoring-impact.md
```

Each `kord.md` contains:

| Field | Description |
|-------|-------------|
| **Requester** | Agent asking |
| **Provider** | Agent answering |
| **Provides** | What this kord delivers |
| **Guidelines** | How to answer — sources, format, constraints |

??? example "pattern-review kord"

    ```markdown
    # Kord: deployer → designer (pattern review)

    | Field | Value |
    |-------|-------|
    | **Requester** | deployer |
    | **Provider** | designer |
    | **Provides** | Pattern compliance review for a proposed deployment |

    ## Guidelines

    Check the deployment manifest against the pattern library in
    `agents/designer/patterns/`. Report violations by severity
    (blocking, warning, info). Keep response under 40 lines.

    ```

## Consultation Freshness

Each kord directory contains a `.valid` marker and a `freshness.sh` script. Freshness is controlled by two hooks, each owned by a different side:

- **Pre-consult hook** (requester) — runs `freshness.sh` before every consultation. The script checks `.valid` and any other criteria. Returns fresh or stale.
- **Post-event hook** (provider) — runs after events the provider cares about (e.g. post-deploy, config change). Deletes `.valid` to signal staleness.

The kord directory is the neutral ground — root-owned, both sides can touch it. The consultation stays in the requester's memory.

```mermaid
flowchart TB
    C["/consult"] --> G{"Pre-consult hook<br/>freshness.sh"}
    G -->|.valid exists + fresh| M[Read from memory]
    G -->|stale or missing| K[Read guidelines from kord.md]
    K --> A[Spawn provider with guidelines]
    A -->|response| W[Write result to memory + create .valid]

    E[Event] --> P["Post-event hook<br/>(provider)"]
    P -->|deletes| V[.valid]
```



## Kord Discovery

When kord files change, agents are automatically notified.

```mermaid
flowchart TB
    K[Kord files change] --> H[Hook regenerates summary<br/>in agent's dynamic memory]
    H --> G{Guard}
    G -->|summary outdated| B[Agent blocked]
    B -->|re-reads summary| U[Agent unblocked]
```

---

??? note "Related commands"

    | Command | Purpose |
    |---------|---------|
    | `/scribe:kord deployer designer` | Create a new kord |
    | `/consult pattern-review "question"` | Consult via explicit kord |
    | `/consult designer "question"` | Consult via default kord |
