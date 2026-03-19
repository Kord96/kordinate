# Infrastructure

How the system is deployed, accessed, and observed.

## Client → Workstation

You connect to a workstation pod running inside Kubernetes via Tailscale SSH. Claude Code runs inside tmux with agents as subprocesses.

```mermaid
flowchart TB
    U([You]) -->|Tailscale SSH| WP

    subgraph WP[Workstation Pod]
        T[tmux] --> CC[Claude Code]
        CC --> AG[Agents<br/>deployer · sauron · designer · scribe]
        AG <-->|every tool call| HK[Hooks]
    end

    WP -->|SSH + kubectl| C1
    WP -->|SSH + kubectl| C2

    subgraph C1[cluster-a]
        D1[dev] ~~~ T1[test] ~~~ P1[prod]
    end

    subgraph C2[cluster-b]
        D2[dev] ~~~ T2[test] ~~~ P2[prod]
    end
```

## Worktree Sessions

Each tmux window creates an isolated git worktree + branch. On exit: push + PR if changes, cleanup if not.

```mermaid
flowchart LR
    subgraph kordinate[kordinate session]
        W0[window 0<br/>main branch] ~~~ W1[window 1<br/>session/w1] ~~~ W2[window 2<br/>session/w2]
    end

    subgraph project[your-project session]
        PW0[window 0<br/>main branch] ~~~ PW1[window 1<br/>session/w1]
    end
```

Branch flow: `session/*` → `main` → `test` → `prod`

## Cluster Architecture

Each k3s cluster is standalone with its own control plane, worker nodes, and observability stack. Clusters connect over Tailscale but operate independently.

The `master` namespace provides a unified cross-cluster view. It lives on one cluster but is logically separate — it pulls data from clusters, clusters don't push to it.

```mermaid
flowchart TB
    subgraph CA[cluster-a]
        A1[Apps] -->|stdout + /metrics| GA1[Gateway Alloy]
        GA1 --> GP1[Gateway Prom<br/>3h buffer]
        GA1 --> GL1[Gateway Loki<br/>3h buffer]
    end

    subgraph M[master namespace]
        MA[Master Alloy] --> MP[Master Prom<br/>30d retention]
        MA --> ML[Master Loki<br/>30d retention]
        MP --> G[Grafana]
        ML --> G
    end

    subgraph CB[cluster-b]
        A2[Apps] -->|stdout + /metrics| GA2[Gateway Alloy]
        GA2 --> GP2[Gateway Prom<br/>3h buffer]
        GA2 --> GL2[Gateway Loki<br/>3h buffer]
    end

    GP1 -->|"/federate (pull)"| MA
    GL1 -.->|"K8s API (pull)"| MA
    GP2 -->|"/federate (pull)"| MA
    GL2 -.->|"K8s API (pull)"| MA
```

## Data Flow

All observability is **pull-based**. The gateway is the cluster's single external interface.

??? abstract "Inside each cluster"

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
    - Gateway is the cluster's single external interface — all external access goes through Gateway Tailscale
    - Master pulls from gateways — clusters are unaware of master
    - Both clusters are treated identically by master (symmetric design)
    - Apps write structured JSON to stdout — Gateway Alloy tails via K8s API
    - Apps expose `/metrics` — Gateway Alloy discovers and scrapes via pod annotations
    - If master goes down, clusters keep collecting
    - If a cluster goes down, master retains historical data
    - Grafana queries only master's local stores — single datasource per signal

## Log Shipping

!!! warning "Loki limitation"
    Prometheus has `/federate` for pulling metrics. Loki has no equivalent.

    Workaround: Master Alloy tails pod logs on each cluster via the K8s API, exposed through Gateway Tailscale. Each cluster's Gateway Alloy independently tails the same pods — the two collectors are unaware of each other.

    Logs are tailed twice (once locally, once by master). Acceptable: clusters remain self-contained, master is independently resilient, K8s API log endpoint is lightweight.
