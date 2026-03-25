---
name: infra
description: Manage cluster infrastructure and deployments — bootstrap, roll, stop, clean, diff, migrate.
curated: true
scope: global
---

`/deploy <subcommand> [args]`

| Subcommand | Purpose | Reference |
|-----------|---------|-----------|
| `bootstrap <cluster>` | Setup namespaces, storage, deploy stacks | [bootstrap.md](bootstrap.md) + [deploy-cluster.md](deploy-cluster.md) |
| `generate-overlays <cluster>` | Generate kustomize overlays from config | [generate-overlays.md](generate-overlays.md) |
| `roll <project> <source> <target>` | Roll between environments | [operations.md](operations.md) |
| `stop <project> <env>` | Scale down an environment | [operations.md](operations.md) |
| `clean <project> <env>` | Delete PVCs and data | [operations.md](operations.md) |
| `diff <project> <source> <target>` | Stage incremental data changes | [diff.md](diff.md) |
| `migrate [cluster]` | Prepare workstation migration | [migrate.md](migrate.md) |

Authenticate before any operation: use `/authenticate`.

All subcommands are idempotent. Topology at [topology.yaml](topology.yaml).
