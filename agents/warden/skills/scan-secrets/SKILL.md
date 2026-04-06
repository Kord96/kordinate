---
name: audit-secrets
description: Reconcile cluster Kubernetes secrets against the pass store
---

Compare what secrets exist on Kubernetes clusters against what is stored in the local `pass` store. Identify gaps in both directions.

## Arguments

`$ARGUMENTS` — Optional: `<cluster-name>` (from config.yaml). If omitted, audit all clusters.

## Procedure

1. **Load cluster config** — read `$KORDINATE_HOME/shared/runtime/profile/config.yaml` for cluster IPs and namespaces.
2. **List pass store** — run `pass ls kordinate/` to get all local credential entries.
3. **List cluster secrets** — SSH to each cluster node and run `kubectl get secrets --all-namespaces`. Parse namespace, name, and key count.
4. **Cross-reference cluster vs pass** — for each cluster secret, check if a corresponding `pass` entry exists under `kordinate/<service>/`. For each `pass` entry, check if a matching cluster secret exists.
5. **Check manifest references** — scan manifests for `secretKeyRef` entries that use a `MUST_BE_SET` placeholder (meaning the value is expected to come from pass). Verify each referenced secret has a `pass` entry.
6. **Report** findings in four categories (see Output Format below).

## Output Format

```
Secrets audit: <cluster> (<date>)

IN CLUSTER, NOT IN PASS (action needed):
  x <namespace>/<secret-name> (<n> keys)
    Suggested: pass insert kordinate/<service>/<key>

IN PASS, NOT ON CLUSTER (stale or not yet deployed):
  ? kordinate/<path>

MANIFEST REFERENCES WITHOUT PASS ENTRY:
  ! <manifest>:<line> references <secret>/<key> — no pass entry found

VERIFIED (in sync):
  ok kordinate/<path> ↔ <namespace>/<secret-name>

Summary: n missing from pass, n stale in pass, n manifest gaps, n verified
```
