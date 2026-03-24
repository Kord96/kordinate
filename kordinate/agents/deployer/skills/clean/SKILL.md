# clean

Delete PVCs and data in an environment. Destructive — data cannot be recovered.

## Arguments

`$ARGUMENTS` — Required format: `<project> <env>` (e.g., `logbd test`)

Optional flags:
- `--include-infra` — also delete infra PVCs (kafka, postgres, redis). Default: app PVCs only.
- `--diff-only` — only remove staged diff files (`/tmp/diff/`) from pods. Does not delete PVCs or stop checks. Safe to run anytime.

## Prerequisites

Pods must be stopped first (`/deployer:stop`). This command will refuse to run if pods are still active in the target namespace.

## Steps

1. Parse project and env from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster info from `profile/clusters/*.yaml`.

2. SSH to the cluster. **Verify pods are stopped**:
   ```
   ssh <cluster> "kubectl get pods -n <namespace> -l app=<project> --field-selector=status.phase=Running"
   ```
   If any app pods are running (or infra pods when `--include-infra`), refuse and report: "Stop pods first with /deployer:stop".

3. **If `--diff-only`**: clean up staged diff files on all pods in the namespace:
   ```
   for pod in $(kubectl get pods -n <namespace> -l app=<project> -o name); do
     kubectl exec $pod -n <namespace> -- rm -rf /tmp/diff 2>/dev/null || true
   done
   ```
   Report how many pods had diff files cleaned, then exit. No PVC deletion.

4. **List PVCs** in the namespace:
   ```
   ssh <cluster> "kubectl get pvc -n <namespace> -o custom-columns=NAME:.metadata.name,SIZE:.status.capacity.storage,BOUND:.status.phase"
   ```

5. **Classify**: separate app PVCs from infra PVCs (kafka-*, postgres-*, redis-*).

6. **Confirm**: print the list of PVCs to be deleted and their sizes. This is destructive — state clearly: "This will permanently delete the following PVCs and all data."

7. **Delete**:
   - App PVCs: `kubectl delete pvc <name> -n <namespace>` for each
   - Infra PVCs: only if `--include-infra`

8. **Verify**: confirm PVCs are deleted.

9. Report: which PVCs were deleted, total storage reclaimed, which were skipped.

## Rules

- NEVER run clean without verifying pods are stopped first.
- Always list PVCs and sizes before deleting — the caller should see what's being destroyed.
- Infra PVCs require `--include-infra` — no exceptions.
