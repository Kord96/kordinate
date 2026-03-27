---
description: Route a config value to profile/config.yaml with validation
requester: warden
mode: stateless
skill: config
curated: true
scope: global
---

## Provider Guidelines

Accept a config path and value (e.g., `clusters.vandc.tailscale_ip 100.x.x.x`).
Validate against schema before writing.
Report what was written and warn about downstream effects (overlays, hydration).
