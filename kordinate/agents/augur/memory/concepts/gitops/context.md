## Deployment

All deployments flow through git commits — the repository is the single source of truth for desired cluster state.

### Rollout Implications

- Every deployment is a git commit: changes to manifests are reviewed via PR, merged, and automatically reconciled by the GitOps controller
- Rollback is a git revert — no imperative kubectl commands against the cluster
- Drift detection should alert when cluster state diverges from the git-declared state (manual changes bypassing git)
- Multi-environment promotion follows a branch or directory-per-environment strategy — changes propagate through environments via PR merges

### Pre-deploy Checklist

- Verify the GitOps controller (Flux, ArgoCD) is healthy and syncing in the target cluster
- Confirm the target branch/directory contains the correct manifests and no unmerged conflicts
- Check that image tags or digests in the manifests point to images that exist in the registry
- Ensure secrets referenced by manifests are present in the cluster (managed via sealed-secrets or external-secrets, not committed to git)

