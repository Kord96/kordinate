---
description: General deployment and cluster questions
requester: any
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Answer with specific names, versions, and states.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Current state (pods, versions, resources) | yes |
| Relevant configuration (services, ingresses) | if applicable |
| Recent changes | if applicable |

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/manifests/`
- `$KORDINATE_HOME/profile/config.yaml`
- `$KORDINATE_HOME/profile/overlays/`
