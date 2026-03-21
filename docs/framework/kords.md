# Kords

A **kord** is a single consultation link between two agents — a template that defines one specific thing one agent provides to another. Two agents can be linked by multiple kords. A default kord exists for free-form queries.

| Concept | What it is | Where it lives | Nature | Analogy |
|---------|-----------|----------------|--------|---------|
| **Kord** | Template/protocol | `agents/root/kords/<name>/kord.md` | Static, root-owned | class |
| **Consultation** | Actual knowledge | `agents/<requester>/memory/dynamic/consultations/<result>.md` | Dynamic, requester-owned | instance |

### Example

Deployer is about to roll a new service version. Before applying, it needs to know whether monitoring is ready — are dashboards, alerts, and health checks in place? This is Sauron's domain, not Deployer's.

```
/consult monitoring-impact "rolling enricher v2.3 to prod — is monitoring ready?"
```

`/consult` resolves the `monitoring-impact` kord, checks freshness, invokes Sauron with the kord's provider guidelines, caches the response, and returns it. The cached result is reused until Sauron's knowledge changes.

??? example "monitoring-impact kord"

    ```markdown
    # monitoring-impact

    Monitoring impact assessment for infrastructure changes.

    ## Requester

    deployer

    ## Provider

    sauron

    ## Provider Guidelines

    Assess monitoring coverage for the affected service.
    Report gaps, not what's already working.
    Keep under 50 lines.

    ### Response Format

    | Field | Required |
    |-------|----------|
    | Gaps by severity (blocking, warning, info) | yes |
    | Missing dashboards or metrics | yes |
    | Missing alerts | yes |
    | Summary | no |
    ```

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
| **Provider Guidelines** | Behavioral instructions + response format |

??? example "pattern-review kord"

    ```markdown
    # pattern-review

    Architecture review for deployment and monitoring changes.

    ## Requester

    deployer, sauron

    ## Provider

    designer

    ## Provider Guidelines

    Review the proposed change against established patterns.
    Include specific file paths and what should change.
    Keep under 50 lines.

    ### Response Format

    | Field | Required |
    |-------|----------|
    | Violations by severity (blocking, warning, info) | yes |
    | Affected files + suggested changes | yes |
    | Summary | no |
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

## Creating Kords

You don't need to remember the kord template. Just describe what you need — the `.md` guard automatically delegates kord creation to scribe, which enforces the standard structure (Provider Guidelines + Response Format).

```
"create a kord between deployer and sauron for pre-deployment health checks"
```

---

??? note "Related commands"

    | Command | Purpose |
    |---------|---------|
    | `/consult pattern-review "question"` | Consult via explicit kord |
    | `/consult designer "question"` | Consult via default kord |
