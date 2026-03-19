# Infrastructure

How the system is deployed, accessed, and observed.

## Client → Workstation

You connect to a workstation pod running inside Kubernetes via Tailscale SSH. Claude Code runs inside tmux with agents as subprocesses.

```mermaid
flowchart TB
    U([You]) -->|Tailscale SSH| T

    subgraph WP[Workstation Pod]
        T[tmux] -->|window 0| CC0[Claude Code<br/>main branch]
        T -->|window 1| CC1[Claude Code<br/>worktree]
        T -->|window 2| CC2[Claude Code<br/>worktree]
        CC1 --> AG[Agents]
        AG <-->|every tool call| HK[Hooks]
    end

    AG -->|SSH + kubectl| C1[cluster-a]
    AG -->|SSH + kubectl| C2[cluster-b]
```

## Cluster Architecture

Each k3s cluster is standalone with its own control plane, worker nodes, and observability stack. Clusters connect over Tailscale but operate independently.

Every application namespace has the same structure — apps, a gateway alloy, and local prom/loki buffers. The `monitor` namespace provides cluster-wide metrics (kubelet, KSM). The `master` namespace lives on one cluster and pulls from all others.

```mermaid
flowchart TB
    subgraph CA[cluster-a]
        subgraph dev-a[dev namespace]
            A1[apps] --> GA1[gateway alloy] --> S1[prom + loki<br/>3h buffer]
        end
        subgraph test-a[test namespace]
            A2[apps] --> GA2[gateway alloy] --> S2[prom + loki<br/>3h buffer]
        end
        subgraph prod-a[prod namespace]
            A3[apps] --> GA3[gateway alloy] --> S3[prom + loki<br/>3h buffer]
        end
        subgraph mon-a[monitor namespace]
            GA4[gateway alloy<br/>cluster-wide metrics] --> S4[prom + loki<br/>3h buffer]
        end
    end

    subgraph M[master namespace — one cluster only]
        MA[master alloy] --> MP[master prom<br/>30d retention]
        MA --> ML[master loki<br/>30d retention]
        MP --> G[Grafana]
        ML --> G
    end

    S1 & S2 & S3 & S4 -->|pull via tailscale| MA

    subgraph CB[cluster-b]
        subgraph dev-b[dev namespace]
            B1[apps] --> GB1[gateway alloy] --> SB1[prom + loki<br/>3h buffer]
        end
        subgraph prod-b[prod namespace]
            B2[apps] --> GB2[gateway alloy] --> SB2[prom + loki<br/>3h buffer]
        end
        subgraph mon-b[monitor namespace]
            GB3[gateway alloy<br/>cluster-wide metrics] --> SB3[prom + loki<br/>3h buffer]
        end
    end

    SB1 & SB2 & SB3 -->|pull via tailscale| MA
```

!!! note "Namespace model"
    Each namespace is self-contained: apps emit stdout (JSON) and expose `/metrics`, the local gateway alloy scrapes both, and writes to namespace-local prom/loki with 3h retention. The `monitor` namespace doesn't run apps — it collects cluster-wide signals (kubelet, kube-state-metrics). Master pulls from all namespaces' gateways across all clusters.

## Worktree Sessions

Each tmux window creates an isolated git worktree + branch. On exit: push + PR if changes, cleanup if not.

```mermaid
flowchart TB
    subgraph tmux
        direction TB
        subgraph ks[kordinate session]
            W0[window 0 — main branch<br/>no worktree]
            W1[window 1 — session/w1-kordinate<br/>isolated worktree]
            W2[window 2 — session/w2-kordinate<br/>isolated worktree]
        end
        subgraph ps[your-project session]
            PW0[window 0 — main branch]
            PW1[window 1 — session/w1-project<br/>isolated worktree]
        end
    end

    W1 & W2 & PW1 -->|on exit| PR{changes?}
    PR -->|yes| PUSH[push + create PR]
    PR -->|no| CLEAN[cleanup worktree]
```

Branch flow: `session/*` → `main` → `test` → `prod`

## Data Flow

All observability is **pull-based**. The gateway is each namespace's single collection point.

??? abstract "Inside each namespace"

    ```mermaid
    flowchart TB
        subgraph sources[Data Sources]
            AP[App pods<br/>stdout JSON + /metrics]
            KU[Kubelet<br/>/metrics/cadvisor]
            KSM[KSM<br/>:8080/metrics]
        end

        sources -->|pull| GA

        subgraph GA[Gateway Alloy]
            SM[scrape metrics]
            TL[tail logs via K8s API]
            NM[normalize — drop raw kube_*/kafka_*<br/>keep pipeline_* + app metrics]
        end

        GA --> GP[Gateway Prom<br/>3h buffer]
        GA --> GL[Gateway Loki<br/>3h buffer]
    ```

??? abstract "Master federation"

    ```mermaid
    flowchart TB
        MA[Master Alloy] -->|pull /federate| GP[Gateway Prom]
        MA -.->|tail via K8s API| GL[Gateway Loki]

        MA --> MP[Master Prom<br/>30d retention]
        MA --> ML[Master Loki<br/>30d retention]

        MP --> G[Grafana]
        ML --> G
    ```

## Key Principles

!!! info ""
    - Each namespace is self-contained with its own gateway, prom, and loki
    - Gateway is the namespace's single external interface
    - Master pulls from all namespace gateways — clusters are unaware of master
    - Both clusters are treated identically by master (symmetric design)
    - Apps write structured JSON to stdout — gateway alloy tails via K8s API
    - Apps expose `/metrics` — gateway alloy discovers and scrapes via pod annotations
    - If master goes down, clusters keep collecting locally
    - If a cluster goes down, master retains historical data
    - Grafana queries only master's local stores — single datasource per signal

## Log Shipping

!!! warning "Loki limitation"
    Prometheus has `/federate` for pulling metrics. Loki has no equivalent.

    Workaround: Master Alloy tails pod logs on each cluster via the K8s API, exposed through Gateway Tailscale. Each cluster's Gateway Alloy independently tails the same pods — the two collectors are unaware of each other.

    Logs are tailed twice (once locally, once by master). Acceptable: clusters remain self-contained, master is independently resilient, K8s API log endpoint is lightweight.
