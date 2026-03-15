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

2. Read `~/.claude/agents/deployer/deploys/<project>.yaml` to get method, branch mapping, and current state.

3. **Determine direction**: compare source and target against `main < test < prod`.

4. **Gate check** (forward only): verify source environment health before proceeding.
   - Backward rolls: print "Rolling <source> → <target> will overwrite <target>. Proceeding." No gate.

5. **Update target branch** (same for ALL projects):
   - `git fetch origin <source-branch> <target-branch>`
   - Forward: `git checkout <target-branch> && git merge --ff-only origin/<source-branch> && git push origin <target-branch>`
   - Backward: `git checkout <target-branch> && git reset --hard origin/<source-branch> && git push --force-with-lease origin <target-branch>`

6. **Deploy** (method-specific last mile):

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

7. **Apply staged diffs** (if present):
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

8. **Update tracking**: Edit `~/.claude/agents/deployer/deploys/<project>.yaml` — update environment status, last_deployed.

9. Report results: project, direction, source → target, commit hash, health/CI status. Include in report: how many diff files were applied, rows imported, any failures.

## Rules

- Forward rolls cannot skip levels: `main → prod` is not allowed (must go `main → test → prod`).
- Backward rolls can skip levels: `prod → main` is allowed.
- Never force-push to main — only fast-forward merges.
- Use `--force-with-lease` (not `--force`) for backward roll branch resets.
