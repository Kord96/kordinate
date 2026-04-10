# Charon Bootstrap v1

Use this bundle when the task is cluster bootstrap or storage/bootstrap repair.

Execution focus:
- generate overlays before deployment
- validate generated overlays and manifests before applying them
- deploy namespaces, storage, and stack resources in the expected order
- treat bootstrap as idempotent, but still verify preconditions and resulting health

Important source-of-truth paths:
- `skills/bootstrap/topology.yaml`
- `skills/bootstrap/deploy-cluster.md`
- `skills/bootstrap/generate-overlays.md`
- `skills/bootstrap/upgrade-storage.md`

Boundary reminders:
- bootstrap still depends on Alfred-owned overlay source data
- bootstrap writes require the writable k3s kubeconfig path when operating over SSH
