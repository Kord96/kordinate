---
name: operational-notes
description: Dashboard audit findings, metric state, and monitoring infrastructure facts
type: user
---

- Grafana unreachable from sandbox — audited d/classifier/ from source JSON at agents/deployer/manifests/master/base/dashboards/vandc/general/classifier.json
- Classifier dashboard has 42 panels: 5 Prometheus (Scheduler Health row) + 37 FlightSQL/DuckDB
- Key issues found: job label mismatch (logbd-scheduler not a real component), namespace filter missing on all PromQL, grid overlaps, timeseries format mismatch
- Alloy dual-write active: raw metrics + pipeline_* coexist during migration
- physical-resources.json Infrastructure Health panels rewired to k8s-native metrics (PVC ratio + Kafka up)
- pipeline_consumer_slots_behind metric does not exist — Consumer Lag panels removed from operational-health and graphdb-health; sentinel code also removed (evaluate_slots_behind function, SLOTS_BEHIND gauge)
- Audited and fixed d/operational-health: removed 7 dead/duplicate panels, added Dependencies row + API Status flag, fixed kubelet→pipeline_pvc metrics, added namespace filters, cleaned up sentinel dead code (slots_behind, tier_g_errors)
