---
kind: concept
name: gitops
signatures: {}
type: pattern
abstraction:
- deployment
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Git repository as the single source of truth for infrastructure and application state
- ArgoCD `Application` CRDs pointing to git repo paths with `syncPolicy`
- Flux `GitRepository`, `Kustomization`, and `HelmRelease` CRDs
- Kustomize overlays directory structure (`base/`, `overlays/staging/`, `overlays/production/`)
- Reconciliation loop configurations (sync intervals, auto-sync, self-heal, prune)
- Declarative desired state in YAML manifests committed to git
- PR-based change workflow for infrastructure modifications

### Confidence

- **high** -- ArgoCD/Flux CRDs with auto-sync enabled, git repo structure with environment overlays, reconciliation loop actively running
- **medium** -- declarative manifests in a git repo with CI/CD applying them, but no continuous reconciliation agent
- **low** -- infrastructure YAML in git but applied manually via `kubectl apply` or scripts

## Architecture

Look for a reconciliation loop that continuously converges actual cluster state toward the desired state declared in git.

### Review Checklist

- Drift detection is active (the controller detects and corrects manual changes)
- Sync policy includes pruning of resources removed from git
- Secrets are not stored in plaintext in git (use SealedSecrets, SOPS, or external-secrets)
- Environment promotion follows a git-based workflow (PR from staging overlay to production overlay)
- Sync status and health are monitored with alerts on degraded or out-of-sync applications

### Anti-patterns

- Mixing imperative `kubectl` commands with GitOps-managed resources (causing drift fights)
- Storing secrets in plaintext in the git repository
- No sync status monitoring -- the reconciliation loop fails silently
- Single environment overlay for all stages (no separation between staging and production)

### Relationship To Other Concepts

- Related to [infrastructure-as-code](/concepts/infrastructure-as-code) because GitOps usually applies declarative infra manifests from version control through reconciliation.
- Related to [immutable-infra](/concepts/immutable-infra) when rollout artifacts are treated as immutable desired state rather than patched live.
- Related to [config-management](/concepts/config-management) because GitOps repositories often become the source of truth for deployment configuration overlays.

### Boundary

Use `gitops` when Git is the declared source of truth for deployment state and an automated reconciler applies that state continuously.

Do not use it for any infra repo or CI deploy pipeline. The defining feature is reconciliation from Git rather than one-shot imperative deployment.
