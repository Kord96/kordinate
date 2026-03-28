---
description: Pre-deployment readiness check — config, overlays, credentials validated
requester: deployer
mode: stateless
skill: preflight
curated: true
scope: global
---

## Provider Guidelines

Run the preflight check for the specified cluster.
Return READY or NOT READY with specific failures.
This is the gate that deployer should call before `/infra bootstrap` or `/infra roll`.
