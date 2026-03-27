# Kords

A **kord** is a contract between two agents. See [Overview](overview.md#problem) for why kords exist.

## Modes

Each kord specifies how the provider fulfills the request:

- **`stateless`** — skill instructions are self-contained. Runs without the provider agent's memory or context. The requester executes the skill directly. Fast.
- **`stateful`** — skill works better with the provider agent's accumulated memory and context. Spawns the full agent (via Beorn or native subagent).

??? example "stateless — remember"

    ```markdown
    <!-- agents/scribe/kords/remember/contract.md -->
    ---
    description: Write a memory for an agent
    requester: any
    mode: stateless
    skill: remember
    ---
    ```

    Provider is `scribe` (derived from path). The requester invokes `/remember` directly — no scribe agent spawned.

??? example "stateful — deployer-default"

    ```markdown
    <!-- agents/deployer/kords/deployer-default/contract.md -->
    ---
    description: General deployment and cluster questions
    requester: any
    mode: stateful
    ---

    ## Provider Guidelines

    Answer with specific names, endpoints, and configuration paths.
    Keep under 50 lines.

    ### Response Format

    | Field | Required |
    |-------|----------|
    | Infrastructure topology (services, namespaces, dependencies) | yes |
    | Monitoring pipeline (collection → storage → visualization) | yes |
    | Configuration sources (files, ConfigMaps) | if applicable |

    ## Provider State Invalidation

    Invalidate when:
    - Cluster manifests are modified
    - Services are redeployed
    - Monitoring stack configuration changes
    ```

### Cache Freshness

Stateful kords cache results. Each kord can have an `expiry.sh` script that checks if the cache is still valid.

```mermaid
flowchart TB
    C["/kord"] --> M{mode?}
    M -->|stateless| S[Run skill directly]
    M -->|stateful| G{"expiry.sh"}
    G -->|fresh| D[Return data.md]
    G -->|stale| K[Spawn provider agent]
    K --> W[Write data.md]
```

### Creating Kords

Describe what you need. Scribe creates the contract:

```
/create-kord pattern-review "architecture review for deployment changes"
```

### Structure

Kords live under their provider agent's directory at `$KORDINATE_HOME/agents/<provider>/kords/`:

```
$KORDINATE_HOME/agents/
├── designer/kords/
│   └── pattern-review/
│       ├── contract.md         # protocol definition
│       ├── data.md             # cached result (stateful mode)
│       └── expiry.sh           # freshness check (optional)
├── scribe/kords/
│   └── remember/
│       └── contract.md         # stateless mode — no data.md needed
└── deployer/kords/
    └── deployer-default/
        ├── contract.md
        ├── data.md
        └── expiry.sh
```

The provider is implicit from the directory path — no `provider:` field in contract frontmatter.

??? note "Contract template"

    ```markdown
    ---
    description: <what this kord provides>
    requester: <agent or "any">
    mode: <stateless or stateful>
    skill: <skill-name>          # required if mode is stateless
    ---
    <!-- provider is implicit from the directory path: agents/<provider>/kords/<name>/ -->

    ## Provider Guidelines

    <Instructions for how the provider should respond.>

    ### Response Format

    | Field | Required |
    |-------|----------|
    | <field> | yes/no |

    ## Provider State Invalidation

    Invalidate when:
    - <condition>
    ```
