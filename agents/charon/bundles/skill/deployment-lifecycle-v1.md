# Charon Deployment Lifecycle v1

Use this bundle for rollout, rollback, migration, or cleanup tasks.

Normal sequence:
1. identify the project or platform component and current environment
2. run or simulate the relevant preflight checks
3. determine whether the request is forward rollout, rollback, stop, clean, or migrate
4. preserve rollback or drift context before mutating live resources
5. apply changes incrementally and verify rollout health
6. report exact images, manifests, resources, and warnings

Guardrails:
- forward rolls do not skip environment levels
- destructive cleanup requires explicit caller intent
- schema changes must not bypass migration and drift handling
- if deployment fails, prefer rollback plus a concise diagnosis over blind retries
