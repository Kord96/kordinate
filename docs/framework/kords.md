# Kords

## Problem

Khaled is building a stock prediction engine — twenty microservices reading financial APIs into Kafka, ETL consumers writing to S3, and an ML model on top. He's deploying a new service that integrates yfinance as a data source, but monitoring is missing. He asks Sauron to set it up.

To recommend the right metrics and wire them into the existing stack, Sauron needs information from other agents:

```
[sauron] → consult designer "what design pattern does the yfinance service use?"
        ← stream-to-store

[sauron] good — that means we monitor message throughput and storage growth

[sauron] → consult deployer "where is our monitoring stack?"
        ← grafana at 226.247.55.77:8080, access token: xxxx
```

Each consultation invokes an agent. Sauron will need this same information next time it sets up monitoring — the design pattern won't change, the Grafana endpoint rarely moves. But when they do change, stale answers lead to wrong configurations.

## Solution

A **kord** caches information one agent repeatedly needs from another, with invalidation rules maintained by the provider.

| Concept | What it is | Where it lives | Analogy |
|---------|-----------|----------------|---------|
| **Kord** | Protocol definition | `agents/root/kords/<name>/kord.md` | class |
| **Consultation** | Cached result | `agents/<requester>/memory/dynamic/consultations/<kord>.md` | instance |

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

## Cache Rehydration

Each kord has a `.valid` marker. Two hooks control it:

- **Before consulting** — if `.valid` exists, return the cached result. Otherwise invoke the provider.
- **After provider changes** — when the provider's domain changes (files edited, deployments applied), delete `.valid` to force a fresh invocation next time.

```mermaid
flowchart TB
    C["/consult"] --> G{".valid exists?"}
    G -->|yes| M[Return cached result]
    G -->|no| K[Invoke provider with guidelines]
    K --> W[Cache result + create .valid]

    E[Provider's domain changes] --> P["Invalidation hook"]
    P -->|deletes| V[.valid]
```

## Creating Kords

Just describe what you need. The `.md` guard delegates kord creation to scribe, which asks for any missing details (name, requester, provider) and enforces the standard structure.

```
"create a kord between deployer and sauron for pre-deployment health checks"
```

## Structure

Root owns all kord definitions. Each kord is a directory containing the protocol and a freshness script.

```
agents/root/kords/
├── pattern-review/
│   ├── kord.md           # protocol: requester, provider, guidelines, format
│   ├── freshness.sh      # checks .valid marker
│   └── .valid            # present = cache is fresh
├── monitoring-impact/
│   ├── kord.md
│   └── freshness.sh
└── default-deployer/
    ├── kord.md
    └── freshness.sh
```

Each `kord.md` contains:

| Field | Description |
|-------|-------------|
| **Requester** | Agent(s) that can invoke this kord |
| **Provider** | Agent that answers |
| **Provider Guidelines** | How to respond + response format |

---

??? note "Related commands"

    | Command | Purpose |
    |---------|---------|
    | `/consult pattern-review "prompt"` | Consult via explicit kord |
    | `/consult designer "prompt"` | Consult via default kord |
