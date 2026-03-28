---
description: Cluster topology, service endpoints, and networking
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/charon/skills/infra/manifests/
    - kordinate/agents/charon/skills/infra/topology.yaml
    - profile/config.yaml
    - profile/overlays/
  threshold: 0.05
  stale_threshold: 0.25
  max_age: 5d
---

## Provider Guidelines

Return the current cluster layout: namespaces, services, ports, and networking topology. Draw from manifests and overlays, not live state. Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Namespace layout | yes |
| Service names and ports | yes |
| Ingress / endpoint routes | yes |
| Inter-service dependencies | if applicable |
