---
name: platform
description: >
  Deploy and manage the agent runtime platform — agents, curators, kafka, job-router, KEDA scaling.
  Use for platform deploys, scaling changes, status checks, and component restarts.
argument-hint: "deploy <env> | status [env] | scale <agent> <min> <max> [env] | restart <component> [env]"
---

Deploy and manage the agent runtime platform. Applies kustomize overlays for platform components (agents, curators, kafka, job-router, KEDA) to target environments.

## Usage

- `/platform deploy dev` — apply platform manifests to dev
- `/platform status` — show platform pod status in dev (default)
- `/platform scale alfred 1 3 prod` — set KEDA scaling for alfred in prod
- `/platform restart curator dev` — rollout restart curators in dev

## Subcommands

| Subcommand | Purpose |
|------------|---------|
| `deploy <env>` | Apply platform manifests for an environment |
| `status [env]` | Show platform pod status, KEDA scaling, Kafka topic lag |
| `scale <agent> <min> <max> [env]` | Update KEDA scaling for an agent and re-apply |
| `restart <agent\|curator\|all> [env]` | Rollout restart specific components |

Default environment is `dev` if not specified.

## Deploy

`/platform deploy <env>`

1. Parse env from `$ARGUMENTS`.

2. **Preflight** — verify the overlay exists at `$KORDINATE_HOME/profile/overlays/platform/<env>/`. If alfred is available, run alfred `/preflight` for additional validation. If preflight fails, report and exit.

3. **Apply** — execute `kubectl apply -k $KORDINATE_HOME/profile/overlays/platform/<env>/ -n <env>`.

4. **Verify** — check rollout status for all platform deployments in the namespace. If any deployment fails to roll out, report clearly with pod logs.

5. **Report** — components deployed, pod counts, ready state, any warnings.

## Status

`/platform status [env]`

1. Parse env from `$ARGUMENTS` (default: `dev`).

2. **Gather** — collect:
   - Pod counts and ready state for agents, curators, kafka, job-router
   - KEDA ScaledObject configuration (min/max replicas, triggers)
   - Kafka consumer group lag for agent topics

3. **Report** — formatted summary of platform health.

## Scale

`/platform scale <agent> <min> <max> [env]`

1. Parse agent, min, max, and env from `$ARGUMENTS` (default env: `dev`).

2. **Patch** — update the KEDA scaling configuration in the overlay's `scaling.yaml` at `$KORDINATE_HOME/profile/overlays/platform/<env>/scaling.yaml`.

3. **Apply** — re-apply the overlay: `kubectl apply -k $KORDINATE_HOME/profile/overlays/platform/<env>/ -n <env>`.

4. **Verify** — confirm the ScaledObject reflects the new min/max values.

5. **Report** — agent, old scaling, new scaling, verification result.

## Restart

`/platform restart <agent|curator|all> [env]`

1. Parse component and env from `$ARGUMENTS` (default env: `dev`).

2. **Restart** — execute `kubectl rollout restart` for the target deployment(s) in the namespace. If `all`, restart all platform deployments.

3. **Verify** — wait for rollout status to confirm pods are ready.

4. **Report** — components restarted, pod ready state.

## Key Resources

- [manifests/base/](manifests/base/) — base platform kustomize manifests
- `profile/overlays/platform/<env>/` — environment-specific overlays (managed by alfred)
- `profile/config.yaml` — cluster IPs, domains, services

## Rules

- Authenticate before any operation: use `/authenticate`.
- Never patch Dockerfiles — use cluster registry for images.
- If deployment fails, report clearly with error context and pod logs.
- Consult sauron before modifying monitoring-related config.
- All subcommands are idempotent.
