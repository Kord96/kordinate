# rollback

Revert a deployment to its pre-roll state using a snapshot recorded during `/infra roll`.

## Arguments

`$ARGUMENTS` — Required format: `<project> <env>` (e.g., `logbd test`, `stoik prod`)

Optional flags:
- `--dry-run` — show what would be reverted without making changes

## Prerequisites

- A rollback snapshot must exist at `~/.kord/agents/deployer/memory/dynamic/rollback/<project>-<env>.json`
- Authenticate before running: use `/authenticate`

## Snapshot Format

Recorded automatically by `/infra roll` (step 6 in operations.md):

```json
{
  "project": "<project>",
  "env": "<env>",
  "timestamp": "<ISO 8601>",
  "commit": "<git commit hash before roll>",
  "resources": [
    {
      "kind": "Deployment|StatefulSet",
      "name": "<name>",
      "namespace": "<namespace>",
      "replicas": "<count>",
      "containers": [
        {"name": "<container>", "image": "<image:tag>"}
      ]
    }
  ],
  "configmap_hashes": {
    "<name>": "<sha256>"
  },
  "secret_hashes": {
    "<name>": "<sha256>"
  }
}
```

Note: ConfigMap/Secret content is NOT stored (credentials protocol — hashes only for drift detection).

## Steps

1. Parse project and env from `$ARGUMENTS`.

2. **Load snapshot** — read `~/.kord/agents/deployer/memory/dynamic/rollback/<project>-<env>.json`. If no snapshot exists, report error: "No rollback snapshot found. Rollback is only available after a /infra roll." and exit.

3. **Validate snapshot** — check timestamp is recent (within 7 days). If older, warn but allow proceeding.

4. **Dry-run display** (if `--dry-run`): for each resource in the snapshot, show:
   - Current image vs snapshot image
   - Current replicas vs snapshot replicas
   - ConfigMap/Secret hash drift
   Then exit without making changes.

5. **Revert images** — for each Deployment/StatefulSet in the snapshot:
   ```
   kubectl set image <kind>/<name> <container>=<snapshot-image> -n <namespace>
   ```

6. **Revert replicas** — for each resource where current replicas differ from snapshot:
   ```
   kubectl scale <kind>/<name> --replicas=<snapshot-replicas> -n <namespace>
   ```

7. **Check ConfigMap/Secret drift** — for each hash in the snapshot, compare against current:
   ```
   kubectl get configmap <name> -n <namespace> -o json | sha256sum
   ```
   If hashes differ, report: "ConfigMap/Secret `<name>` has changed since snapshot. Manual review required." Do NOT revert ConfigMaps or Secrets automatically.

8. **Wait for rollout** — for each Deployment/StatefulSet:
   ```
   kubectl rollout status <kind>/<name> -n <namespace> --timeout=300s
   ```

9. **Health check** — verify pods are Running:
   ```
   kubectl get pods -n <namespace> -l app=<project> --field-selector=status.phase=Running
   ```

10. **Archive snapshot** — move the snapshot file to prevent double-rollback:
    ```
    mv <snapshot>.json <snapshot>.json.used-<timestamp>
    ```
    This file is kept for audit trail but cannot be used for another rollback.

11. **Report** — summarize: resources reverted, images changed, replica adjustments, ConfigMap/Secret drift warnings.

## Rules

- One level of rollback only — no rollback history or chain
- PVC data is NOT reverted — that's destructive and a separate concern
- Git branch is NOT reverted — kubectl-level only. Use `git revert` separately if needed
- ConfigMaps and Secrets are never automatically reverted — flag for manual review
- Snapshot files live in dynamic memory (`~/.kord/agents/deployer/memory/dynamic/rollback/`) — survives pod restarts
- Used snapshots are archived (`.used-<timestamp>`) — never deleted
