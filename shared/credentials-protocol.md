---
description: All credentials managed through pass store — never hardcoded in manifests or config
---

All credentials go through the `pass` store under `kordinate/`.

- Never hardcode credentials in manifests, overlays, or config files
- Kubernetes Secrets are created from `pass` at deploy time
- New credentials: `pass insert kordinate/<service>/<key>`
- Reference in manifests as `secretKeyRef`, never as inline `value`
