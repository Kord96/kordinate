---
name: infra
description: Manage cluster infrastructure and deployments — bootstrap, roll, stop, clean, diff, migrate, preflight, rollback.
curated: true
scope: global
---

`/infra <subcommand> [args]`

| Subcommand | Purpose | Reference |
|-----------|---------|-----------|
| `bootstrap <cluster>` | Setup namespaces, storage, deploy stacks | [deploy-cluster.md](deploy-cluster.md) |
| `generate-overlays <cluster>` | Generate kustomize overlays from config | [generate-overlays.md](generate-overlays.md) |
| `roll <project> <source> <target>` | Roll between environments | [operations.md](operations.md) |
| `stop <project> <env>` | Scale down an environment | [operations.md](operations.md) |
| `clean <project> <env>` | Delete PVCs and data | [operations.md](operations.md) |
| `diff <project> <source> <target>` | Stage incremental data changes | [diff.md](diff.md) |
| `migrate [cluster]` | Execute workstation migration (build, PVC, data, deploy) | [migrate.md](migrate.md) |
| `migrate-cleanup` | Post-migration verification and cleanup (run from new pod) | [migrate-cleanup.md](migrate-cleanup.md) |
| `preflight <project> <env>` | Pre-deployment validation checks | [preflight.md](preflight.md) |
| `rollback <project> <env>` | Revert deployment to pre-roll state | [rollback.md](rollback.md) |

Authenticate before any operation: use `/authenticate`.

All subcommands are idempotent.

## Key Resources

- [topology.yaml](topology.yaml) — what manifests go to which namespaces
- [manifests/](manifests/) — flat k8s yaml (namespace-prefixed)
- [images/](images/) — container build contexts (workstation, log-puller, loki-federate)
- [dashboards/](dashboards/) — Grafana dashboard JSON
- `profile/config.yaml` — cluster IPs, domains, services (source of truth)
- `profile/overlays/<cluster>/` — generated kustomize overlays (cluster-specific patches)
