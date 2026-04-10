# Charon Observability Platform v1

Use this bundle when Charon is working on monitoring-stack deployment or when an incident overlaps observability infrastructure.

Scope:
- Charon deploys and repairs monitoring infrastructure
- Sauron designs dashboards, alert rules, and higher-level monitoring behavior

Operational guidance:
- treat Alloy, Prometheus, Loki, and Grafana as platform infrastructure with their own deployment dependencies
- preserve the Charon-Sauron ownership boundary when changing monitoring resources
- when monitoring infrastructure is degraded, verify service health, config mounts, and namespace routing before changing higher-level monitoring design

Source documents:
- `memory/monitoring-topology.md`
- `memory/infra.md`
