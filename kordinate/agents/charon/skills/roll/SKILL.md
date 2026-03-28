---
name: roll
description: >
  Deploy a service between environments (forward) or revert a deployment (backward).
  Preflight checks run automatically before forward rolls.
argument-hint: "<project> <source> <target> | back <project> <env>"
curated: true
scope: global
---

Roll a project between environments. Forward rolls deploy code to a higher environment. Backward rolls (`/roll back`) revert to a pre-roll snapshot.

## Usage

- `/roll stoik dev prod` — forward: deploy stoik from dev to prod
- `/roll back stoik prod` — backward: revert stoik prod to pre-roll state

## Forward Roll

`/roll <project> <source> <target>`

1. Parse project, source, and target from `$ARGUMENTS`.

2. **Preflight** — run validation checks per [../shared/preflight/preflight.md](../shared/preflight/preflight.md). If preflight fails, report and exit.

3. **Roll** — execute the deployment per [operations.md](operations.md). This handles direction detection, branch updates, image builds, manifest application, staged diff application, and rollout verification. A rollback snapshot is recorded automatically before deploying.

4. **Report** — project, direction, source → target, commit hash, health status, diff files applied.

## Backward Roll (Rollback)

`/roll back <project> <env>`

1. Parse project and env from `$ARGUMENTS`.

2. **Rollback** — revert to the pre-roll snapshot per [rollback.md](rollback.md). This restores images, replicas, and checks for ConfigMap/Secret drift.

3. **Report** — resources reverted, images changed, drift warnings.

## Stop

`/roll stop <project> <env> [--include-infra]`

Scale pods to zero. Preserves PVCs and data. See [operations.md](operations.md) (stop section).

## Clean

`/roll clean <project> <env> [--include-infra] [--diff-only]`

Delete PVCs and data. Destructive. See [../shared/clean/clean.md](../shared/clean/clean.md).

## Rules

- Forward rolls cannot skip levels: `main → prod` is not allowed (must go `main → test → prod`).
- Backward rolls can skip levels: `prod → main` is allowed.
- Authenticate before any operation: use `/authenticate`.
