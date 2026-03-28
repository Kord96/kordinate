---
description: Create Kubernetes secrets from pass store for a specific cluster
requester: alfred
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - profile/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Accept a cluster name.
Read pass store entries and create corresponding Kubernetes Secrets.
Report what was created or updated.
This is part of the deployment pipeline — alfred validates prerequisites, then asks charon to provision secrets.

### Response Format

| Field | Required |
|-------|----------|
| Cluster name | yes |
| Secrets created/updated | yes |
| Errors or warnings | if applicable |
