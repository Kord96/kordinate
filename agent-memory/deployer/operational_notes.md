---
name: operational-notes
description: Stable workarounds, constraints, and infrastructure facts for deployments
type: user
---

- git-crypt in detached worktree requires: (1) create with --no-checkout, (2) copy symmetric key from existing worktree's git-crypt/keys/default, (3) git reset HEAD, (4) git checkout . -- this avoids smudge filter failures
- For future RWX PVC expansions in Longhorn: must restart the share-manager pod in longhorn-system after patching PVC size, then patch PVC status subresource to clear FileSystemResizePending condition.
- SSH to clusters: use kkord@ user, not claude@. Tailscale IPs: vandc=100.95.237.24, home=100.71.90.43.
- No rsync on workstation pod -- use scp for manifest sync.
- Gateway consolidated into single 4-container pod (alloy, prometheus, loki, tailscale). Gateway Tailscale IPs: gateway-home=100.79.204.119, gateway-vandc=100.93.174.24.
- master-alloy serviceAccountName must be "default" (not "master-alloy") since SA was removed.
- kubectl apply won't remove absent fields — use patch to clear stale serviceAccountName.
- git-crypt rebase workaround: disable smudge/clean filters (set to 'cat', required=false) before rebase, use -X theirs for encrypted file conflicts, then unset filters after.
