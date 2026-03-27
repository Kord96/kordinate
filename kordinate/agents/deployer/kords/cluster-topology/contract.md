---
description: Cluster topology, service endpoints, and networking
requester: any
mode: stateful
curated: true
scope: global
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

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/manifests/`
- `$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/topology.yaml`
- `$KORDINATE_HOME/profile/config.yaml`
- `$KORDINATE_HOME/profile/overlays/`
