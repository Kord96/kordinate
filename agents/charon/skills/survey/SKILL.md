---
name: survey
description: >
  Produce infra-atlas.json — a structured snapshot of cluster infrastructure.
  Consumed by augur (project design), sauron (monitoring design), and all agents
  for general cluster awareness. Run when infrastructure changes or on demand.
argument-hint: "[--full]"
context: inherit
---

Produce `infra-atlas.json` — the shared source of truth about what's running, what's available, and what a new workload must look like to work in this cluster.

## Arguments

`$ARGUMENTS` — Optional: `[--full]` to force a full survey even if preflight says no changes.

## Output

Write to `$AGENT_PROJECT_DIR/memory/global/infra-atlas.json`.

This file is in charon's global memory — all agents can read it.

## Schema

```json
{
  "version": "1",
  "metadata": {
    "generated": "<ISO timestamp>",
    "generated_by": "charon /survey",
    "cluster_hash": "<hash of kubectl state used to generate this>",
    "analyzed_at": "<ISO timestamp>"
  },

  "cluster": {
    "name": "<cluster name>",
    "provider": "k3s",
    "version": "<k3s version>",
    "nodes": [
      {
        "name": "<node>",
        "roles": ["control-plane"],
        "status": "Ready|NotReady|SchedulingDisabled",
        "capacity": { "cpu": "<cores>", "memory": "<size>" },
        "allocatable": { "cpu": "<cores>", "memory": "<size>" },
        "taints": []
      }
    ]
  },

  "environments": {
    "dev": {
      "namespace": "dev",
      "purpose": "Development — all agents and workstation operate here",
      "services": {
        "<service-name>": {
          "kind": "Deployment|StatefulSet|Kafka|etc",
          "endpoint": "<svc>.<ns>.svc.cluster.local:<port>",
          "external": "<public URL if any>",
          "auth": "none|secret|oauth",
          "status": "running|degraded|stopped",
          "metadata": {}
        }
      },
      "topics": ["<kafka topics if kafka exists>"],
      "pvcs": [
        { "name": "<pvc>", "class": "<storageClass>", "size": "<size>", "access": "RWO|RWX" }
      ]
    },
    "test": { "managed_by": "charon", "deploy_via": "/roll", "promote_from": "dev" },
    "prod": { "managed_by": "charon", "deploy_via": "/roll", "promote_from": "test" }
  },

  "platform": {
    "namespace": "kord",
    "agents": {
      "<name>": {
        "model": "opus|sonnet|haiku",
        "scaling": { "min": 0, "max": 10, "cooldown": 300 },
        "status": "running|stopped"
      }
    },
    "job_router": {
      "endpoint": "job-router.kord.svc.cluster.local:3100",
      "delegate": "POST /api/delegate {agent, prompt, project?, repo?}"
    },
    "kafka": {
      "endpoint": "kafka-kafka-bootstrap.dev.svc.cluster.local:9092",
      "topics": {
        "jobs": ["jobs.augur", "jobs.charon", "jobs.warden", "jobs.sauron", "jobs.alfred"],
        "results": ["jobs.result", "jobs.dlq"],
        "memory": ["memory.updates.augur", "memory.updates.charon", "memory.updates.warden", "memory.updates.sauron", "memory.updates.alfred"]
      }
    },
    "scribes": {
      "model": "haiku",
      "dedup_via": "Anthropic Haiku API"
    }
  },

  "observability": {
    "metrics": {
      "collector": "Alloy (per cluster)",
      "store": "Prometheus",
      "master_endpoint": "prometheus.master.svc.cluster.local:9191",
      "retention": "30d",
      "scrape_discovery": "annotation-based (prometheus.io/scrape=true)"
    },
    "logs": {
      "collector": "Alloy (per cluster)",
      "store": "Loki",
      "master_endpoint": "loki.master.svc.cluster.local:3100",
      "retention": "30d",
      "format": "Structured JSON to stdout"
    },
    "dashboards": {
      "grafana": "grafana.master.svc.cluster.local:3000",
      "external": "grafana.khaledkord.com"
    }
  },

  "networking": {
    "internal": "ClusterIP services, DNS: <svc>.<ns>.svc.cluster.local",
    "mesh": "Tailscale between clusters",
    "external": "Cloudflare tunnels for public endpoints",
    "registry": "REGISTRY (resolved from cluster config/overlay)"
  },

  "storage": {
    "default_class": "longhorn",
    "access_modes": ["ReadWriteOnce", "ReadWriteMany"],
    "pvcs": []
  },

  "new_workload_contract": {
    "observability": {
      "metrics": {
        "endpoint": "/metrics",
        "format": "prometheus",
        "required_metrics": [
          "http_requests_total{method, path, status}",
          "http_request_duration_seconds{method, path}"
        ],
        "annotations": {
          "prometheus.io/scrape": "true",
          "prometheus.io/port": "<metrics_port>"
        }
      },
      "logging": {
        "output": "stdout",
        "format": "json",
        "required_fields": ["level", "component", "event", "timestamp"],
        "levels": ["debug", "info", "warn", "error"]
      },
      "health": {
        "readiness": "GET /health → 200 when ready to serve",
        "liveness": "GET /health → 200 when process is alive",
        "startup_grace": "30s"
      },
      "vitals": {
        "model": "standalone deployment (one per app, not sidecar)",
        "port": 9131,
        "health_gauges": "vitals_<section>{check} — tri-state 0=FAIL, 1=WARNING, 2=OK",
        "derived_metrics": "App-level aggregations computed from pod-level data",
        "required_evaluations": ["process", "deps"],
        "env": {
          "PROMETHEUS_URL": "http://prometheus.master.svc.cluster.local:9191",
          "LOKI_URL": "http://loki.master.svc.cluster.local:3100",
          "APP_NAME": "<app label value>"
        },
        "meta_alert": "VitalsMissing: absent(vitals_process{app='<name>'}) for 5m"
      }
    },
    "packaging": {
      "container": "Dockerfile at repo root or /docker/",
      "image_registry": "REGISTRY/<name>:latest",
      "build": "kaniko Job in master namespace",
      "manifests": "kustomize base (namespace-agnostic) + env overlays",
      "labels": {
        "app": "required — used by Alloy for metrics/log discovery"
      },
      "secrets": "k8s Secrets managed by alfred, never in code or manifests"
    },
    "resilience": {
      "graceful_shutdown": "Handle SIGTERM, drain connections within 30s",
      "resource_limits": "Must declare requests and limits",
      "resource_defaults": {
        "requests": { "cpu": "100m", "memory": "256Mi" },
        "limits": { "memory": "1Gi" }
      },
      "restart_policy": "Always",
      "probes": "readinessProbe + livenessProbe required"
    }
  }
}
```

## Procedure

### Step 0 — Preflight

The daemon's preflight script handles this. If `infra-atlas.json` exists and the cluster state hash hasn't changed, the job is skipped without invoking Claude.

If `--full` is in the prompt, skip preflight and proceed.

### Step 1 — Gather cluster state

Run these commands and collect output:

```bash
kubectl get nodes -o json
kubectl get namespaces -o json
kubectl get deployments,statefulsets,services,pvcs --all-namespaces -o json
kubectl get kafkatopics -n dev -o json 2>/dev/null
kubectl get scaledobjects -n kord -o json 2>/dev/null
```

### Step 2 — Build the atlas

Assemble the JSON from the gathered state:

1. **cluster** — from `kubectl get nodes`
2. **environments.dev** — scan dev namespace for services, deployments, PVCs, Kafka topics
3. **environments.test/prod** — stub entries only
4. **platform** — from kord namespace: agents, job-router, scribes, KEDA config
5. **observability** — from master/monitor namespaces: Prometheus, Loki, Grafana, Alloy
6. **networking** — from services, Tailscale status
7. **storage** — from PVCs across namespaces
8. **new_workload_contract** — static, updated manually when conventions change

### Step 3 — Compute state hash

Hash the raw kubectl output used to build the atlas. Store in `metadata.cluster_hash`. This is what the preflight compares against.

```bash
echo "$RAW_STATE" | sha256sum | cut -d' ' -f1
```

### Step 4 — Write

Write to `$AGENT_PROJECT_DIR/memory/global/infra-atlas.json`.

### Step 5 — Report

```
## Infrastructure Survey

**Cluster**: <name> (<version>)
**Nodes**: <count> (<status summary>)
**Environments**: dev (N services), test (stub), prod (stub)
**Platform**: <agent count> agents, job-router, <scribe count> scribes
**Services**: <list>
**Contract**: <N> requirements across observability, packaging, resilience
**Hash**: <cluster_hash>

Written to: <path>
```
