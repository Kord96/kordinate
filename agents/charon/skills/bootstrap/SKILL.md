---
name: bootstrap
description: >
  Set up a cluster from scratch — namespaces, storage, overlays, and deploy all stacks.
  Use for initial cluster setup or full rebuild.
argument-hint: "<cluster>"
---

Set up a cluster from scratch. Generates kustomize overlays, creates namespaces, provisions storage, and deploys all service stacks.

## Usage

`/bootstrap <cluster>`

## Steps

1. **Generate overlays** — create cluster-specific kustomize patches per [generate-overlays.md](generate-overlays.md).

2. **Preflight** — validate the generated overlays and manifests per [../shared/preflight/preflight.md](../shared/preflight/preflight.md).

3. **Deploy cluster** — execute the full bootstrap sequence per [deploy-cluster.md](deploy-cluster.md). This handles: namespace creation, storage provisioning, Longhorn setup, stack deployment, and verification.

4. **Report** — namespaces created, stacks deployed, storage provisioned, any warnings.

## Subcommands

| Subcommand | Purpose | Reference |
|-----------|---------|-----------|
| `<cluster>` | Full bootstrap | [deploy-cluster.md](deploy-cluster.md) |
| `generate-overlays <cluster>` | Generate kustomize overlays only | [generate-overlays.md](generate-overlays.md) |
| `upgrade-storage <pvc> <namespace>` | Upgrade a PVC to Longhorn RWX | [upgrade-storage.md](upgrade-storage.md) |

## Key Resources

- [topology.yaml](topology.yaml) — what manifests go to which namespaces
- [manifests/](manifests/) — flat k8s yaml (namespace-prefixed)
- [images/](images/) — container build contexts
- [dashboards/](dashboards/) — Grafana dashboard JSON
- `agents/alfred/profile/config.yaml` — Alfred-owned cluster IPs, domains, services source
- `shared/runtime/profile/config.yaml` — published runtime config projection for deploy/bootstrap consumers
- `agents/alfred/profile/overlays/<cluster>/` — Alfred-owned generated overlay source
- `shared/runtime/profile/overlays/<cluster>/` — published runtime overlay projection

## Rules

- Authenticate before any operation: use `/authenticate`.
- Bootstrap requires both `.charon-auth` and `.bootstrap-auth`.
- All subcommands are idempotent.
