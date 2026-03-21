# Kords

## Problem

Dividing work across specialized agents keeps each one focused — but an agent's work can depend on another agent's domain knowledge.

**Sauron** is responsible for monitoring. When invoked on a new repo, it needs answers to key questions:

1. **What infrastructure do we have?**
    - System runs on Kubernetes
    - Grafana at `198.128.3.100:9000`, credentials: xxx
    - Loki at `198.128.3.100:9001`, Prometheus at `198.128.3.100:9002`
    - Shipping via Alloy, configured at `master-alloy.yml`

2. **What design patterns does this app use?**
    - Stream-to-store pattern — reads from Kafka, writes to S3
    - Typical metrics: message throughput, storage growth

Answering these questions requires scanning the repo and the deployment pipeline. The natural solution is to cache them — but how does **Sauron** detect a stale cache when Grafana moves to a new machine?

## What is a Kord

**Sauron** delegates these questions to specialized agents (**Deployer**, **Designer**). Each relationship is defined by a **kord** — a contract that specifies the provider, the requester, and the expected response format.

| Concept | What it is | Where it lives | Analogy |
|---------|-----------|----------------|---------|
| **Kord** | Contract definition | `agents/root/kords/<name>/kord.md` | class |
| **Consultation** | Cached result | `agents/<requester>/memory/dynamic/consultations/<kord>.md` | instance |

??? example "default-deployer kord (sauron asking deployer about infrastructure)"

    ```markdown
    ---
    description: General deployment and cluster questions
    requester: any
    provider: deployer
    ---

    ## Provider Guidelines

    Answer with specific names, versions, and states.
    Keep under 50 lines.

    ### Response Format

    | Field | Required |
    |-------|----------|
    | Current state (pods, versions, resources) | yes |
    | Relevant configuration (services, ingresses) | if applicable |
    | Recent changes | if applicable |

    ## Cache Invalidation

    Invalidate when:
    - Cluster manifests are modified
    - New deployments are applied
    - Service endpoints or configuration changes
    ```

### Cache Rehydration

Each kord has a `.valid` marker. Two hooks control it:

| Hook | Triggered by | Implemented by | Purpose |
|------|-------------|----------------|---------|
| `hydrate-cache.sh` (pre-consult) | requester | provider | Is the cache still fresh? |
| `hydrate-cache.sh store` (post-consult) | requester | provider | Reset freshness state after caching |
| `invalidate-cache.sh` (post-event) | system hook | provider | Invalidate when provider's files change |

```mermaid
flowchart TB
    C["/consult"] --> G{".valid exists?"}
    G -->|yes| M[Return cached result]
    G -->|no| K[Invoke provider with guidelines]
    K --> W[Cache result + create .valid]

    E[Provider's domain changes] --> P["Invalidation hook"]
    P -->|deletes| V[.valid]
```

### Creating Kords

Just describe what you need. The `.md` guard delegates kord creation to scribe, which asks for any missing details (name, requester, provider) and enforces the standard structure.

```
"create a kord between deployer and sauron for pre-deployment health checks"
```

### Structure

Root owns all kord definitions. Each kord is a directory containing the contract and a freshness script.

```
agents/root/kords/
├── pattern-review/
│   ├── kord.md           # contract: requester, provider, guidelines, format
│   ├── hydrate-cache.sh      # pre/post-consult: check + reset freshness
│   └── .valid            # present = cache is fresh
├── monitoring-impact/
│   ├── kord.md
│   └── hydrate-cache.sh
└── default-deployer/
    ├── kord.md
    └── hydrate-cache.sh
```

---

??? note "Related commands"

    | Command | Purpose |
    |---------|---------|
    | `/consult pattern-review "prompt"` | Consult via explicit kord |
    | `/consult designer "prompt"` | Consult via default kord |
