---
description: Create Kubernetes secrets from pass store for a specific cluster
requester: alfred
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Accept a cluster name.
Read pass store entries and create corresponding Kubernetes Secrets.
Report what was created or updated.
This is part of the deployment pipeline — alfred validates prerequisites, then asks deployer to provision secrets.

### Response Format

| Field | Required |
|-------|----------|
| Cluster name | yes |
| Secrets created/updated | yes |
| Errors or warnings | if applicable |

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/profile/`
