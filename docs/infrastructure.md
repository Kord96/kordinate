# Infrastructure

How the system is deployed, accessed, and observed.

## Overview

```mermaid
flowchart LR
    U([You]) -->|Tailscale SSH| WP

    subgraph WP[Workstation Pod]
        T[tmux] --> CC[Claude Code]
        CC --> AG[Agents]
        AG <-->|every tool call| HK[Hooks]
    end

    AG -->|SSH + kubectl| C1[cluster-a]
    AG -->|SSH + kubectl| C2[cluster-b]
```

??? abstract "Worktree sessions"

    Each tmux window runs its own Claude Code instance with isolated agents and hooks. Windows create isolated git worktrees + branches via `bin/claude-session`. On exit: push + PR if changes, cleanup if not. The `auto-merge-to-dev.sh` hook then tries to fast-forward main — if it fails, run `/merge`.

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
        PUSH --> FF{fast-forward main?}
        FF -->|yes| CLOSE[close PR]
        FF -->|no| MERGE[run /merge]
    ```

    Branch flow: `session/*` → `main` → `test` → `prod`

??? abstract "Cluster architecture"

    Each k3s cluster is standalone with its own control plane, worker nodes, and observability stack. Clusters connect over Tailscale but operate independently.

    App namespaces (`dev`, `test`, `prod`) run workloads only. The `gateway` namespace (called `monitor` in k8s) runs a single Alloy instance that scrapes all namespaces, with local Prom + Loki buffers. The `master` namespace pulls from all gateways. In practice, master runs on one of the clusters but is logically independent.

    ```mermaid
    flowchart TB
        subgraph CA[cluster-a]
            A1[dev apps] & A2[test apps] & A3[prod apps]

            subgraph gw-a[gateway namespace]
                GA[gateway alloy<br/>scrapes all namespaces] --> PA[prom + loki<br/>3h buffer]
            end

            A1 & A2 & A3 -.->|/metrics + stdout| GA
        end

        subgraph M[master namespace]
            MA[master alloy] --> MP[master prom<br/>30d retention]
            MA --> ML[master loki<br/>30d retention]
            MP --> G[Grafana]
            ML --> G
        end

        PA -->|pull via tailscale| MA

        CB[cluster-b<br/>same structure]

        CB -->|pull via tailscale| MA
    ```

    !!! note "Namespace model"
        App namespaces run workloads only — no observability components. Apps emit structured JSON to stdout and expose `/metrics`. The gateway namespace runs a single Alloy that scrapes all app pods (via annotations), kubelet (cAdvisor), KSM, and tails logs via K8s API. It writes to namespace-local Prom + Loki with 3h retention. Master pulls from each cluster's gateway.

## Data Flow

All observability is **pull-based**. Each cluster's gateway namespace is the single collection and federation point.

```mermaid
flowchart LR
    subgraph cluster[Each cluster — gateway namespace]
        AL[Alloy] --> P[Prom<br/>3h] & L[Loki<br/>3h]
        P & L --- GW[Gateway<br/>Tailscale]
    end

    Apps[app pods] -.->|/metrics + stdout| AL
    GW -->|:9090 /federate| MA
    GW -->|:6443 K8s API| MA

    subgraph master[Master namespace]
        MA[Master Alloy] --> MP[Prom<br/>30d] & ML[Loki<br/>30d]
        MP & ML --> G[Grafana]
    end
```

Gateway Tailscale exposes three ports on the tailnet: `:9090` (Prometheus), `:3100` (Loki), `:6443` (K8s API). Master Alloy connects to these — it never reaches cluster internals directly.

??? abstract "Inside the gateway namespace"

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

    Master Alloy pulls metrics via `/federate` from each gateway's Prometheus (`:9090`), and tails pod logs via each gateway's K8s API (`:6443`). Both exposed through Gateway Tailscale.

    ```mermaid
    flowchart TB
        subgraph GW1[cluster-a gateway tailscale]
            GP1[:9090 Prom]
            GK1[:6443 K8s API]
        end

        subgraph GW2[cluster-b gateway tailscale]
            GP2[:9090 Prom]
            GK2[:6443 K8s API]
        end

        GP1 & GK1 -->|tailnet| MA
        GP2 & GK2 -->|tailnet| MA

        MA[Master Alloy] --> MP[Master Prom<br/>30d retention]
        MA --> ML[Master Loki<br/>30d retention]

        MP --> G[Grafana]
        ML --> G
    ```

    !!! warning "Loki limitation"
        Prometheus has `/federate` for pulling metrics. Loki has no equivalent. Workaround: Master Alloy tails pod logs on each cluster via the K8s API, exposed through Gateway Tailscale. Logs are tailed twice (once locally, once by master) — acceptable for resilience.

## Key Principles

!!! info "Collection"
    - App namespaces run workloads only — no observability components
    - One gateway namespace per cluster collects all signals (metrics, logs, cluster state)
    - Apps write structured JSON to stdout — gateway tails via K8s API
    - Apps expose `/metrics` — gateway discovers and scrapes via pod annotations

!!! info "Federation"
    - Master pulls from each cluster's gateway — clusters are unaware of master
    - Both clusters are treated identically by master (symmetric design)
    - Grafana queries only master's local stores — single datasource per signal

!!! info "Resilience"
    - If master goes down, clusters keep collecting locally (3h buffer)
    - If a cluster goes down, master retains historical data (30d)
