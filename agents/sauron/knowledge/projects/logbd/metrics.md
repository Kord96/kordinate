# logBD — Metrics

> **Maintain this document when metrics are added, removed, or renamed in the logBD codebase.**

## Prometheus Metrics

Every consumer exposes metrics via HTTP on its own port (`--metrics-port`).

### Metric Tiers

**Tier 1 — All consumers (automatic):**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_messages_consumed_total` | Counter | Messages consumed from Kafka |
| `pipeline_messages_failed_total` | Counter | Messages that failed to parse |
| `pipeline_flush_duration_seconds` | Histogram | Time spent in flush callback |
| `pipeline_flush_entities_total` | Counter | Entities flushed to storage |
| `pipeline_buffer_size` | Gauge | Current buffered message count |
| `pipeline_latest_event_ts` | Gauge | Timestamp of latest Kafka message |

**Tier 2 — Entity consumers:**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_entities_new_total` | Counter | First-time entities |
| `pipeline_entities_known_total` | Counter | Known entities (update only) |
| `pipeline_entity_count` | Gauge | Total rows in DuckDB table |
| `pipeline_granular_entities_total` | Counter | Raw entities before aggregation |

**Tier 3 — Domain enrichment:**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_enrichment_total` | Counter | Entities enriched (by type) |
| `pipeline_enrichment_duration_seconds` | Histogram | Enrichment latency |
| `pipeline_enrichment_errors_total` | Counter | Enrichment failures |
| `pipeline_enrichment_backlog` | Gauge | Stale domains needing re-enrichment |
| `pipeline_domain_enrichment_coverage` | Gauge | Coverage counts by status |

**Tier 4 — Download pipeline:**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_download_total` | Counter | Download attempts by status |
| `pipeline_download_queue_depth` | Gauge | URIs waiting in queue |

**Tier 5 — Message producer:**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_rawlog_files_total` | Gauge | rawLog files discovered |
| `pipeline_slots_processed_total` | Counter | Slots fully processed |
| `pipeline_slot_duration_seconds` | Histogram | Time per slot |
| `pipeline_slots_discovered_total` | Counter | Total slots discovered in rawLog inventory scans |
| `pipeline_producer_slot_processing_start_unixtime` | Gauge | Unix time when current slot processing started, 0=idle |
| `pipeline_observed_earliest_slot` | Gauge | Earliest slot ID observed in rawLog inventory |
| `pipeline_observed_latest_slot` | Gauge | Latest slot ID observed in rawLog inventory |
| `pipeline_processed_earliest_slot` | Gauge | Earliest slot ID in the processed set |

**Tier 6 — Entity extraction:**

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_extracted_entities_total` | Counter | Entities extracted by type |

Plus `process_*` metrics (RSS, CPU, FDs) from `prometheus_client` automatically.

### Port Assignments

| Consumer | Port |
|----------|------|
| message-producer | 9100 |
| entity-extraction | 9101 |
| metadata-archiver | 9102 |
| graph-subnet | 9110 |
| graph-domain | 9111 |
| graph-uri | 9112 |
| graph-text | 9113 |
| graph-image | 9114 |
| graph-template | 9115 |
| graph-host | 9116 |
| graph-email-address | 9117 |
| graph-edge-ew | 9118 |
| graph-edge-assoc | 9125 |
| graph-edge-cluster | 9127 |
| graph-cluster | 9122 |
| graph-score | 9133 |
| uri-download | 9119 |
| js-render | 9120 |
| domain-uclt | 9134 |
| domain-whois | 9135 |
| derived-refresh | 9140 |
| sentinel | 9131 |

## Grafana Dashboards

Seven dashboards organized into three folders:

### Pipeline/

| Dashboard | Content |
|-----------|---------|
| **Pipeline Overview** | Ingestion rate, consumer throughput, Kafka lag, entity counts, flush durations, enrichment health, download pipeline |
| **Business Metrics** | Message volume trends, spam ratios, entity growth, enrichment coverage |
| **ML Classifier** | Release list counts per entity type, score distributions, list churn, release history |

### Infrastructure/

| Dashboard | Content |
|-----------|---------|
| **Health Status** | System overview flags, per-consumer status grid, slots behind, ETA, infrastructure checks |
| **Physical Resources** | Per-process CPU/RSS, disk I/O, network, DuckDB file sizes |

### Explore/

| Dashboard | Content |
|-----------|---------|
| **Data Layer** | DuckDB table row counts, entity type breakdowns, retention stats |
| **URI Template Detail** | Per-URI-template drill-down (traffic, redirects, downloads) |
| **Cluster Detail** | Per-cluster drill-down (members, spam ratio, freeze status) |

## Label Mapping

The local Prometheus relabel config (`deploy/graphdb/monitoring/prometheus-config.yaml`) maps the k8s pod label `component` to `job`. However, Grafana queries the **gateway Prometheus** via federation, which assigns `job=prometheus.scrape.pods` to all federated metrics and preserves `component` as a separate label.

- **Dashboard PromQL**: use `component=` (e.g., `component="sentinel"`)
- **Loki stream selectors**: use `component=` (Promtail preserves k8s pod labels)
- **Do NOT use** `job=` to filter by component name — `job` is always `prometheus.scrape.pods` in the gateway
