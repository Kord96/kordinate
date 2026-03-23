# stop

Scale pods to zero in an environment. Preserves PVCs and data — pods can be restarted later.

## Arguments

`$ARGUMENTS` — Required format: `<project> <env>` (e.g., `<project> test`, `<project> prod`)

Optional flags:
- `--include-infra` — also stop infra pods (kafka, postgres, redis, pgbouncer, schema-registry). Default: app pods only.

## Steps

1. Parse project and env from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster info from `profile/clusters/*.yaml`.

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
