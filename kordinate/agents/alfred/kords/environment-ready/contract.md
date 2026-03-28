---
description: Deployment preflight check — is a cluster environment ready?
requester: deployer
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - profile/config.yaml
    - profile/overlays/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Run a quick preflight check for the target cluster. Verify profile config, overlay validity, and pass store credential existence. Return ready/not-ready with a list of issues. Keep under 30 lines.

### Response Format

| Field | Required |
|-------|----------|
| Status (ready / not-ready) | yes |
| Issues list | if not ready |
| Missing credentials | if any |
| Stale overlays | if any |
