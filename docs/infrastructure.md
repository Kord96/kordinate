# Infrastructure

How the system is deployed, accessed, and observed.

## Client → Workstation

You connect to a workstation pod running inside Kubernetes via Tailscale SSH. Claude Code runs inside tmux with agents as subprocesses.

```
              ┌────────┐
              │  You   │
              └───┬────┘
                  │ Tailscale SSH
    ┌─────────────▼──────────────────┐
    │        Workstation Pod         │
    │                                │
    │  tmux ─► Claude Code           │
    │               │                │
    │        ┌──────┴──────┐         │
    │        │   Agents    │         │
    │        │  deployer   │────┐    │
    │        │  sauron     │    │    │
    │        │  designer   │  hooks  │
    │        │  scribe     │  check  │
    │        └─────────────┘  every  │
    │                         tool   │
    │                         call   │
    └─────────────────────────┼──────┘
                              │
                      SSH + kubectl
                 ┌────────┼────────┐
                 │        │        │
           ┌─────▼──┐ ┌──▼─────┐  │
           │cluster-a│ │cluster-b│ ...
           │ dev     │ │ dev     │
           │ test    │ │ test    │
           │ prod    │ │ prod    │
           └─────────┘ └────────┘
```

## Worktree Sessions

Each tmux window creates an isolated git worktree + branch. On exit: push + PR if changes, cleanup if not.

```
tmux
├── kordinate (session)
│   ├── window 0 → main branch (no worktree)
│   ├── window 1 → session/w1-kordinate (worktree)
│   └── window 2 → session/w2-kordinate (worktree)
└── your-project (session)
    ├── window 0 → main branch
    └── window 1 → session/w1-your-project (worktree)
```

Branch flow: `session/*` → `main` → `test` → `prod`

## Cluster Architecture

Each k3s cluster is standalone with its own control plane, worker nodes, and observability stack. Clusters connect over Tailscale but operate independently.

The `master` namespace provides a unified cross-cluster view. It lives on one cluster but is logically separate — it pulls data from clusters, clusters don't push to it.

```
┌─ cluster-a ─────────────────────────────────┐
│                                              │
│  Apps ──▶ Gateway Alloy ──▶ Gateway Prom/Loki│
│   │           ▲                              │
│   └─ stdout ──┘ via K8s API                  │
│                                              │
└──────────────────────────────────────────────┘
                   ▲
                   │ pull (via Gateway Tailscale)
                   │
┌──────────────────┴───────────────────────────┐
│                                     master   │
│                                              │
│  Master Alloy ──▶ Master Prom/Loki           │
│                          │                   │
│                          ▼                   │
│                       Grafana                │
│                                              │
└──────────────────┬───────────────────────────┘
                   │ pull (via Gateway Tailscale)
                   ▼
┌──────────────────────────────────────────────┐
│                             cluster-b        │
│                                              │
│  Apps ──▶ Gateway Alloy ──▶ Gateway Prom/Loki│
│   │           ▲                              │
│   └─ stdout ──┘ via K8s API                  │
│                                              │
└──────────────────────────────────────────────┘
```

## Data Flow

All observability is **pull-based**. The gateway is the cluster's single external interface.

??? abstract "Inside each cluster"

    ```
    ┌────────────────────────────── inside each cluster ──────────────────────────────┐
    │                                                                                 │
    │  ┌── App pods ──────┐  ┌── Kubelet ─────────┐  ┌── KSM ──────────┐             │
    │  │ stdout (JSON)    │  │ /metrics/cadvisor   │  │ :8080/metrics   │             │
    │  │ /metrics         │  │ volume stats        │  │                 │             │
    │  └────────┬─────────┘  └─────────┬───────────┘  └────────┬────────┘             │
    │           │ pull                 │ pull                   │ pull                 │
    │           ▼                      ▼                       ▼                      │
    │  ┌─────────────────────────────────────────────────────────────────────────┐     │
    │  │ Gateway Alloy                                                          │     │
    │  │  metrics ◀── scrapes /metrics from pods, kubelet, KSM                  │     │
    │  │  logs    ◀── tails pod stdout via K8s API                              │     │
    │  │  normalize ── drops raw kube_*/kafka_*, keeps pipeline_* + app metrics │     │
    │  └──────────┬──────────────────────┬──────────────────────────────────────┘     │
    │             ▼                      ▼                                            │
    │  ┌──────────────────┐  ┌──────────────────┐                                     │
    │  │ Gateway Prom     │  │ Gateway Loki     │                                     │
    │  │ (3h buffer)      │  │ (3h buffer)      │                                     │
    │  └──────────────────┘  └──────────────────┘                                     │
    └─────────────────────────────────────────────────────────────────────────────────┘
    ```

??? abstract "Master federation"

    ```
    ┌──────────────────────────────────────────────────────────────────────┐
    │ Master Alloy                                                        │
    │  metrics ◀── pulls Gateway Prom /federate (all series)              │
    │  logs    ◀── tails pods via K8s API (through Gateway Tailscale)     │
    └──────────┬──────────────────────┬───────────────────────────────────┘
               ▼                      ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Master Prom      │  │ Master Loki      │
    │ (30d retention)  │  │ (30d retention)  │
    └────────┬─────────┘  └────────┬─────────┘
             └────────────┬────────┘
                          ▼
                   ┌───────────┐
                   │  Grafana  │
                   └───────────┘
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
