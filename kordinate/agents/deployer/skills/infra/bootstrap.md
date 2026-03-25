---
name: bootstrap
description: Manage cluster infrastructure — setup, deploy, generate overlays, manage secrets.
curated: true
scope: global
---

Bootstrap and manage cluster infrastructure.

`/bootstrap <subcommand> [args]`

| Subcommand | Purpose | Reference |
|-----------|---------|-----------|
| `generate-overlays <cluster>` | Generate kustomize overlays from profile/config.yaml | [generate-overlays.md](generate-overlays.md) |
| `setup-namespaces <cluster>` | Create namespaces and apply RBAC | [deploy-cluster.md](deploy-cluster.md) |
| `setup-storage <cluster>` | Install Longhorn and configure storage classes | [deploy-cluster.md](deploy-cluster.md) |
| `deploy-master <cluster>` | Deploy master namespace infrastructure | [deploy-cluster.md](deploy-cluster.md) |
| `deploy-gateway <cluster>` | Deploy observability gateway stack | [deploy-cluster.md](deploy-cluster.md) |
| `add-node <cluster> <node-ip>` | Add a worker node to a cluster | [deploy-cluster.md](deploy-cluster.md) |
| `add-cluster <name> <node-ip>` | Bootstrap a new k3s cluster | [deploy-cluster.md](deploy-cluster.md) |

Authenticate before any operation: use `/authenticate`.

All subcommands are idempotent — safe to re-run. All SSH operations use deployer auth flow.
