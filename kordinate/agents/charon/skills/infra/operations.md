# roll

Roll a project between environments. Branches are the source of truth — the roll updates the target branch, then deploys via the project's method.

## Arguments

`$ARGUMENTS` — Required format: `<project> <source> <target>` (e.g., `logbd main test`, `stoik test prod`, `logbd prod test`)

## Direction Detection

The environment order is: `main` (dev) → `test` → `prod`

- **Forward** (source is lower than target): roll code up to a higher environment
- **Backward** (source is higher than target): roll a lower environment to match a higher one

## Steps

1. Parse project, source, and target from `$ARGUMENTS`. If missing, show usage and exit.

2. Discover project layout: find manifests at `<project-repo>/manifests/`, get cluster/registry from `profile/config.yaml`, use project name as image name. Use the global branch model (main/test/prod).

3. **Determine direction**: compare source and target against `main < test < prod`.

4. **Gate check** (forward only): verify source environment health before proceeding.
   - Backward rolls: print "Rolling <source> → <target> will overwrite <target>. Proceeding." No gate.

5. **Update target branch** (same for ALL projects):
   - `git fetch origin <source-branch> <target-branch>`
   - Forward: `git checkout <target-branch> && git merge --ff-only origin/<source-branch> && git push origin <target-branch>`
   - Backward: `git checkout <target-branch> && git reset --hard origin/<source-branch> && git push --force-with-lease origin <target-branch>`

6. **Record rollback snapshot** — before deploying, capture current state for potential rollback:
   ```
   kubectl get deploy,sts -n <namespace> -l app=<project> -o json
   ```
   Extract: resource kind, name, namespace, replica count, container images.
   Hash current ConfigMaps and Secrets:
   ```
   kubectl get configmap -n <namespace> -o json | sha256sum
   kubectl get secret -n <namespace> -o json | sha256sum
   ```
   Write snapshot to `~/.kord/agents/charon/memory/dynamic/rollback/<project>-<env>.json`.
   Create the directory if it doesn't exist.

7. **Deploy** (method-specific last mile):

   ### method: kubectl
   - SSH to the target cluster
   - Build image from the target branch: `docker build --cache-from <registry>/<image>:latest ...`
   - Tag and push to registry
   - Apply manifests to the target namespace: `kubectl apply -n <namespace> -R -f <manifest-dir>/`
   - Wait for rollout, verify pods are Running

   ### method: git-branch
   - Branch was already updated in step 5
   - CI detects the push and handles build + publish automatically
   - Wait for CI to pass on the target branch

8. **Apply staged diffs** (if present):
   After deploying, check each target pod for `/tmp/diff/manifest.json`:
   ```
   kubectl exec <pod> -n <target-ns> -- cat /tmp/diff/manifest.json 2>/dev/null
   ```
   If a manifest exists:

   a. **DuckDB deltas**: for each parquet file in the manifest:
      ```
      kubectl exec <pod> -n <target-ns> -- python3 -c "
      import duckdb
      conn = duckdb.connect('<db_path>')
      conn.execute(\"INSERT INTO <table> SELECT * FROM read_parquet('/tmp/diff/<table>_delta.parquet')\")
      conn.close()
      "
      ```

   b. **Postgres deltas**: for each SQL file:
      ```
      kubectl exec <postgres-pod> -n <target-ns> -- psql -U <user> -d <db> -f /tmp/diff/<table>_delta.sql
      ```

   c. **Cleanup diff files**: after successful apply:
      ```
      kubectl exec <pod> -n <target-ns> -- rm -rf /tmp/diff
      ```

   If any diff apply fails, report the error but continue with remaining diffs. Failed diff files are left in place for retry.

9. **Report tracking**: Log the deployment result (project, environment, commit hash, timestamp).

10. Report results: project, direction, source → target, commit hash, health/CI status. Include in report: how many diff files were applied, rows imported, any failures.

## Rules

- Forward rolls cannot skip levels: `main → prod` is not allowed (must go `main → test → prod`).
- Backward rolls can skip levels: `prod → main` is allowed.
- Never force-push to main — only fast-forward merges.
- Use `--force-with-lease` (not `--force`) for backward roll branch resets.

---

# stop

Scale pods to zero in an environment. Preserves PVCs and data — pods can be restarted later.

## Arguments

`$ARGUMENTS` — Required format: `<project> <env>` (e.g., `<project> test`, `<project> prod`)

Optional flags:
- `--include-infra` — also stop infra pods (kafka, postgres, redis, pgbouncer, schema-registry). Default: app pods only.

## Steps

1. Parse project and env from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster info from `profile/config.yaml`.

2. SSH to the cluster. List all deployments/statefulsets in the target namespace for this project:
   ```
   ssh <cluster> "kubectl get deploy,sts -n <namespace> -l app=<project> -o name"
   ```

3. **Classify**: separate app pods from infra pods. Infra components: kafka, postgres, redis, pgbouncer, schema-registry.

4. **Scale down**:
   - App pods: `kubectl scale <resource> --replicas=0 -n <namespace>` for each
   - Infra pods: only if `--include-infra` flag is set

5. **Verify**: `kubectl get pods -n <namespace>` — confirm target pods are terminated.

6. Report: which pods were stopped, which were skipped (infra without flag), current pod count.

## Rules

- Never stop infra without `--include-infra` — apps depend on infra being ready on restart.
- If pods fail to terminate within 60s, report but don't force-kill.

---

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

1. Parse project and env from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster info from `profile/config.yaml`.

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
