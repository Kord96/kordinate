---
description: General deployment and cluster questions
requester: any
provider: deployer
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

## Provider State Invalidation

Invalidate when:
- Cluster manifests are modified
- New deployments are applied
- Service endpoints or configuration changes
