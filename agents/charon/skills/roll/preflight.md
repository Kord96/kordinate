# preflight

Pre-deployment validation. Run before `/infra roll` to catch issues early.

## Arguments

`$ARGUMENTS` — Required format: `<project> <env>` (e.g., `logbd test`, `stoik prod`)

Optional flags:
- `--strict` — treat WARNINGs as errors (non-zero exit)

## Prerequisites

Authenticate before running: use `/authenticate`.

## Steps

1. Parse project and env from `$ARGUMENTS`. Discover manifests at `<project-repo>/manifests/` and get cluster/registry from `shared/runtime/profile/config.yaml`.

2. **Manifest validation** — dry-run all manifests:
   ```
   kubectl apply --dry-run=client -f <manifest-dir>/ 2>&1
   ```
   ERROR if any manifest fails to parse.

3. **Image existence** — for each container image referenced in manifests, verify it exists in the registry:
   ```
   docker manifest inspect <registry>/<image>:<tag> 2>&1
   ```
   ERROR if image not found.

4. **Resource requests/limits** — check every container spec in manifests:
   - `resources.requests.memory` must be set → ERROR if missing
   - `resources.limits.memory` must be set → ERROR if missing
   - `resources.requests.cpu` should be set → WARN if missing
   - `limits >= requests` for both cpu and memory → ERROR if violated

5. **Required labels** — every Deployment/StatefulSet must have:
   - `metadata.labels.app` → ERROR if missing
   - `spec.template.metadata.labels.app` → ERROR if missing

6. **Prometheus annotations** — check pod template metadata for:
   - `prometheus.io/scrape: "true"` → WARN if missing
   - `prometheus.io/port` → WARN if missing when scrape is true

7. **Readiness/liveness probes** — check every container spec:
   - `readinessProbe` → WARN if missing
   - `livenessProbe` → WARN if missing

8. **PVC bindings** — for each PVC referenced in manifests, verify it exists and is bound in the target namespace:
   ```
   kubectl get pvc <name> -n <namespace> -o jsonpath='{.status.phase}'
   ```
   ERROR if PVC doesn't exist or is not Bound. Skip for new deployments (PVC will be created).

9. **Secrets existence** — for each Secret referenced in manifests (secretKeyRef, secretName), verify it exists:
   ```
   kubectl get secret <name> -n <namespace> 2>&1
   ```
   ERROR if secret not found.

10. **ConfigMaps existence** — for each ConfigMap referenced in manifests, verify it exists:
    ```
    kubectl get configmap <name> -n <namespace> 2>&1
    ```
    ERROR if configmap not found.

## Output

Structured findings table:

```
| # | Severity | Check | Resource | Detail |
|---|----------|-------|----------|--------|
| 1 | ERROR | manifest-parse | deployment/foo | invalid YAML at line 42 |
| 2 | WARN | probes | deployment/bar | missing readinessProbe |
```

Summary line: `Preflight: X errors, Y warnings. <PASS|FAIL>`

Exit behavior:
- Any ERROR → FAIL
- `--strict` + any WARN → FAIL
- Otherwise → PASS

## Rules

- Read-only — preflight never creates or modifies cluster resources
- Always run with the target environment's kubeconfig context
- Report ALL findings, don't stop at first error
- Skip PVC/Secret/ConfigMap checks if kubectl is not available (report as SKIP)
