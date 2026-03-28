---
description: Metrics Instrumentation — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Monitor the metrics pipeline itself to ensure instrumentation is healthy and scrape targets are reachable.

### Key Metrics

- `scrape_duration_seconds` (histogram) — time Prometheus takes to scrape each target
- `scrape_samples_scraped` (gauge) — number of metric samples returned per scrape
- `up` (gauge) — whether the scrape target is reachable (1=up, 0=down)
- `prometheus_target_interval_length_seconds` (summary) — actual scrape interval vs configured

### Alerts

- Scrape target down (`up == 0`) for longer than two scrape intervals
- Scrape duration approaching the scrape interval (risk of overlap or timeout)
- Sudden drop in scraped sample count (metrics may have been deregistered or endpoint broken)
- High-cardinality label detected (metric sample count growing unboundedly)
