# Consultation

Ask an agent a question without transferring full control.

## Usage

```bash
/consult deployer "Is logbd healthy on vandc?"
/consult sauron "what metrics does the enricher expose?"
/consult designer "what are logbd's main components?"
```

## How It Works

```mermaid
flowchart TD
    Q["/consult agent question"] --> CH{cache fresh?}
    CH -->|yes, same question| R[return cached result]
    CH -->|stale or new question| SP[spawn agent]
    SP --> A[agent reads memory, answers]
    A --> W[write result to cache]
    W --> RR[return result]
```

Results are cached per consulter-consultant pair:

- **Cache file**: `agents/shared/memory/dynamic/<consulter>-<consultant>.cache` — the answer
- **Hash file**: `agents/shared/memory/dynamic/.<consulter>-<consultant>.hash` — MD5 of the consultant's source dirs (`instructions/`, `memory/static/`, `memory/dynamic/`)

Staleness is detected by `cache_check` comparing the stored hash against current source files — if sources changed, the cache is stale and the agent is re-consulted.

!!! tip "Force re-consultation"
    ```bash
    /invalidate deployer
    ```
    Removes the `.hash` files where the given agent is the consultant. Cache content files are preserved as fallback — they'll be refreshed on next `/consult`.

## Consultation Matrix

=== "Deployer asks"

    | Consultant | Provides |
    |-----------|----------|
    | designer | Pattern deployment perspective, architecture constraints |
    | sauron | Monitoring impact of infra changes, metric dependencies |

=== "Sauron asks"

    | Consultant | Provides |
    |-----------|----------|
    | designer | Pattern monitoring perspective — what to observe |
    | deployer | Live cluster state, pod health, resource usage |

=== "Designer asks"

    | Consultant | Provides |
    |-----------|----------|
    | deployer | Current infrastructure reality — what's deployed, constraints |
    | sauron | Observability coverage gaps, metric/dashboard inventory |

=== "Scribe asks"

    | Consultant | Provides |
    |-----------|----------|
    | designer | Architecture context for documentation accuracy |
    | sauron | Monitoring context for documentation accuracy |
    | deployer | Infrastructure context for documentation accuracy |

!!! note ""
    The matrix is bidirectional — designer can ground architecture reviews in live cluster state from deployer, sauron can discover monitoring targets from deployer, etc.
