# Infra Team: Infrastructure

How the system is deployed, accessed, and observed -- plus the deployer agent that manages it all.

## Deployer

The deployer agent owns all infrastructure operations. It is the only agent authorized to write to clusters.

| | |
|---|---|
| **Triggers** | `roll`, `roll forward`, `roll backward`, `publish`, `migrate` |
| **Authority** | kubectl writes, container registry, Redis |
| **Exclusive Tools** | postgres.py, Redis MCP |
| **Style** | Reactive -- executes on request |

### Commands

| Command | Description |
|---------|-------------|
| `/deployer:roll` | Roll between environments |
| `/deployer:stop` | Scale down an environment |
| `/deployer:clean` | Clean up environment data |
| `/deployer:diff` | Stage incremental data changes |
| `/deployer:bootstrap` | Bootstrap cluster infrastructure |

### Memory

| | Static | Dynamic |
|---|---|---|
| **Global** | infra.md, migration.md, troubleshooting.md | auto-managed |
| **Project** | `deployer/static/` -- k8s manifests | `deployer/dynamic/` -- operational notes |

### Hooks

Two guard hooks enforce deployer-only access to dangerous operations:

| Hook | What it guards |
|------|---------------|
| `guard-kubectl.sh` | kubectl writes via SSH (`apply`, `delete`, `scale`, `rollout`, etc.) + `docker build/push/tag`. Hard-blocks workstation resources and master namespace writes without bootstrap auth. |
| `guard-redis.sh` | Redis MCP access -- only deployer may use Redis tools. |

Both hooks use the profile lock authentication flow: the deployer copies `profile/locks/deployer` to `/tmp/.deployer-auth`, the hook compares the files, and the deployer removes the temp file when done.

---

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

    Each tmux window runs its own Claude Code instance with isolated agents and hooks. Windows create isolated git worktrees + branches via `bin/claude-session`. On exit: push + PR if changes, cleanup if not. The `auto-merge-to-dev.sh` hook then tries to fast-forward main -- if it fails, run `/merge`.

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

    App namespaces (`dev`, `test`, `prod`) run workloads only. Each cluster has three infrastructure namespaces:

    | Namespace | What runs there |
    |-----------|----------------|
    | `gateway` | Gateway Tailscale (cluster's external interface) + Workstation (if interactive cluster) |
    | `monitor` | Alloy, Prom (local), Loki (local), KSM, node-exporter |
    | `master` | Master Alloy, Prom (30d), Loki (30d), Grafana -- one cluster only |

    ```mermaid
    flowchart TB
        subgraph CA[cluster-a]
            A1[dev apps] & A2[test apps] & A3[prod apps]

            subgraph mon-a[monitor]
                GA[alloy] --> PA[prom + loki<br/>local]
            end

            subgraph gw-a[gateway]
                GWT[tailscale]
                WS[workstation]
            end

            A1 & A2 & A3 -.->|/metrics + stdout| GA
        end

        subgraph M[master]
            MA[master alloy] --> MP[prom<br/>30d] & ML[loki<br/>30d]
            MP & ML --> G[Grafana]
        end

        GWT -->|tailnet| MA

        CB[cluster-b<br/>same structure]

        CB -->|tailnet| MA
    ```

    The `gateway` namespace is the cluster's front door -- either a full workstation (for interactive clusters) or just the Tailscale pod (for headless clusters). Master runs on one cluster but is logically independent.

## Data Flow

All observability is **pull-based**. Apps follow the [observability contract](../reference/observability-contract.md) -- Gateway Alloy collects everything into local Prom + Loki. Gateway Tailscale federates to master.

```mermaid
flowchart TB
    subgraph cluster[Each cluster]
        subgraph env[env namespace — dev/test/prod]
            subgraph myapp["app: my-app"]
                P1[pod 1]
                PN[pod N]
                VIT[Vitals]
                P1 ~~~ PN ~~~ VIT
            end
            subgraph infra["app: infra"]
                KF[Kafka]
                RD[Redis]
                PG[Postgres]
                KF ~~~ RD ~~~ PG
            end
        end

        subgraph nodes[per-node]
            NE[node-exporter]
            CA[cAdvisor]
            KL[kubelet]
            NE ~~~ CA ~~~ KL
        end

        subgraph mon[monitor]
            AL[Alloy] --> LK[Loki<br/>local] & PR[Prom<br/>local]
        end

        subgraph gw[gateway]
            GWT[TS sidecar<br/>or Workstation]
            MIO[MinIO]
        end

        myapp -->|uses| infra
        myapp & infra -->|/metrics + logs| AL
        nodes -->|host + container metrics| AL
        PR -->|:9090| GWT
        LK -->|sidecar writes<br/>JSON Lines| MIO
        MIO -->|:9000| GWT
        myapp -.->|app ports| GWT
    end

    GWT -->|:9090 /federate| MA
    GWT -->|:9000 MinIO| MA
    GWT -.->|app ports| EXT[external access]

    subgraph master[master]
        MA[Master Alloy] --> ML[Loki<br/>30d] & MP[Prom<br/>30d]
        MP & ML --> G[Grafana]
    end
```

**Collection:** Alloy scrapes app pods and infra services (via `prometheus.io/scrape` annotations), node-exporter, cAdvisor, kubelet, and KSM. Tails pod stdout via K8s API. Writes to local Prom + Loki with local retention.

**Federation:** Gateway Tailscale forwards `:9090` (Prom /federate), `:9000` (MinIO), and app ports on the tailnet. Master Alloy pulls metrics via Prom `/federate`. For logs, a puller sidecar on master fetches JSON Lines from each gateway's MinIO bucket via Tailscale `:9000`, writes to local emptyDir, and master Alloy tails the files with `loki.source.file` -- pull-based, master reads at its own pace.

!!! note "Loki federation sidecar"
    Loki does not support pull-based federation natively. A sidecar in the Loki pod queries `localhost:3100` every 60s and writes JSON Lines files to a MinIO bucket in the gateway namespace (1 hour retention, auto-cleaned). Gateway Tailscale exposes MinIO on `:9000`. A puller sidecar on master fetches from each gateway's MinIO via Tailscale `:9000`, writes to a local emptyDir volume, and master Alloy tails the files with `loki.source.file`. Labels are preserved in the JSON Lines format and re-extracted by master Alloy's `loki.process` pipeline.

??? abstract "What Alloy normalizes"

    Alloy drops raw infrastructure metric prefixes and re-exports them under `pipeline_*` so dashboards and vitals use a consistent namespace.

    | Source | Raw metric | Normalized to |
    |--------|-----------|---------------|
    | Kubelet | `kubelet_volume_stats_used_bytes` | `pipeline_pvc_used_bytes` |
    | Kubelet | `kubelet_volume_stats_capacity_bytes` | `pipeline_pvc_capacity_bytes` |
    | KSM | `kube_pod_container_status_restarts_total` | `pipeline_container_restarts_total` |
    | KSM | `kube_cronjob_spec_suspend` | `pipeline_cronjob_suspended` |
    | KSM | `kube_cronjob_next_schedule_time` | `pipeline_cronjob_next_schedule_time` |
    | KSM | `kube_pod_container_resource_limits` | `pipeline_container_resource_limits` |
    | Kafka JMX | `kafka_log_log_size` | `pipeline_kafka_topic_size_bytes` |

    All other `kube_*` and `kafka_*` metrics are dropped. App metrics and `node_*` metrics pass through unchanged.

## Key Principles

!!! info "Collection"
    - App namespaces run workloads only -- no observability components
    - `monitor` namespace collects all signals (metrics, logs, cluster state)
    - `gateway` namespace exposes the cluster on the tailnet (Tailscale + workstation)
    - Apps follow the [observability contract](../reference/observability-contract.md) -- JSON stdout, `/metrics` endpoint, vitals health pod

!!! info "Federation"
    - Master pulls from each cluster's gateway -- clusters are unaware of master
    - Both clusters are treated identically by master (symmetric design)
    - Grafana queries only master's local stores -- single datasource per signal

!!! info "Resilience"
    - If master goes down, clusters keep collecting locally
    - If a cluster goes down, master retains historical data (30d)

---

## Consultation Matrix

When the deployer or sauron need information outside their domain, they consult other agents.

=== "Deployer asks"

    | Consultant | Provides |
    |-----------|----------|
    | designer | Pattern deployment perspective, architecture constraints |
    | sauron | Monitoring impact of infra changes, metric dependencies |

=== "Sauron asks"

    | Consultant | Provides |
    |-----------|----------|
    | designer | Pattern monitoring perspective -- what to observe |
    | deployer | Live cluster state, pod health, resource usage |
