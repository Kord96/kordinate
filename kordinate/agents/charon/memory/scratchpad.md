---
description: Deployer working notes and observations
curated: false
scope: global
preloaded: deployer
---

- git-crypt in detached worktree requires: (1) create with --no-checkout, (2) copy symmetric key from existing worktree's git-crypt/keys/default, (3) git reset HEAD, (4) git checkout . — avoids smudge filter failures
- git-crypt rebase workaround: disable smudge/clean filters (set to 'cat', required=false) before rebase, use -X theirs for encrypted file conflicts, then unset filters after
- For future RWX PVC expansions in Longhorn: must restart the share-manager pod in longhorn-system after patching PVC size, then patch PVC status subresource to clear FileSystemResizePending condition
- SSH to clusters: use kkord@ user, not claude@. Tailscale IPs: vandc=100.95.237.24, home=100.71.90.43
- No rsync on workstation pod — use scp for manifest sync
- Gateway consolidated into single pod (alloy, prometheus, loki, tailscale). Gateway Tailscale IPs: gateway-home=100.79.204.119, gateway-vandc=100.93.174.24
- For project-specific notes, use the `write_memory` tool to save memories.
