# Charon Operations Core v1

Use this bundle when the task is primarily about deployment execution, rollback safety, migration, or incident handling.

Execution doctrine:
- forward rolls verify source health, run preflight checks, and preserve rollback state before deployment
- backward rolls warn before overwriting newer state and restore the recorded pre-roll snapshot
- stop operations preserve data unless the caller explicitly asked for destructive cleanup
- schema-affecting changes require migration detection and drift checks before rollout

Incident-handling defaults:
- identify the failing workload, namespace, and rollout boundary first
- check rollout status, pod status, recent events, and relevant logs before changing manifests
- distinguish build failures, registry/image failures, configuration drift, PVC readiness, and dependency readiness
- rollback when a deployment is unhealthy and the safest next move is restoration rather than continued mutation

Useful deeper references:
- `memory/migration.md`
- `memory/troubleshooting.md`
- `skills/roll/operations.md`
- `skills/roll/rollback.md`
