---
kind: concept
name: time-series
signatures: {}
source:
  memory_concept: memory/catalog/concepts/time-series.md
type: pattern
abstraction:
- data
- temporal
scope: domain
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `timestamp` as the primary or leading index column in tables or collections
- `retention_policy` configuration for automatic data expiry
- `downsample` or `rollup` functions aggregating high-frequency data into coarser buckets
- InfluxDB client: `influxdb_client`, `write_api`, `query_api`, Flux query language
- TimescaleDB: `create_hypertable`, `time_bucket()`, `add_retention_policy()`
- Prometheus: `prometheus_client`, `Counter`, `Gauge`, `Histogram`, `Summary` metric types
- Python: `pandas.DatetimeIndex`, `resample()`, `rolling()` window operations
- JS/TS: `@influxdata/influxdb-client`, timeseries-specific ORMs
- Go: `prometheus/client_golang`, `influxdb-client-go`, custom `TimeBucket` aggregation
- Rust: `influxdb`, `prometheus` crate, timestamp-indexed data structures

### Confidence

- **high** -- TimescaleDB hypertable or InfluxDB bucket with retention policies, time_bucket aggregation, and downsampling jobs
- **medium** -- Prometheus metrics with histogram/summary types and recording rules for pre-aggregation
- **low** -- Regular table with a timestamp column and ad-hoc time-range queries without specialized time-series tooling

## Architecture

### When to use
- Metrics, monitoring, and observability data with high write throughput and time-range queries
- IoT sensor data, financial tick data, or any append-heavy temporal stream
- Workloads where data naturally ages and older data can be downsampled or expired

### Anti-patterns
- Querying raw high-frequency data for dashboards instead of using pre-aggregated rollups
- No retention policy, causing unbounded storage growth as time-series data accumulates
- Using a general-purpose RDBMS for time-series workloads without partitioning or hypertables

### Complements
- [metrics-instrumentation](/concepts/metrics-instrumentation) — time-series storage backs metrics pipelines
- [materialized-view](/concepts/materialized-view) — rollups and pre-aggregations are materialized views over time
- [stream-to-store](/concepts/stream-to-store) — streaming ingestion feeds time-series stores

## Impact

Time-series data drives monitoring, alerting, and capacity planning. Retention policies and downsampling directly affect storage costs and query performance, so missing configurations silently degrade both operational visibility and infrastructure budgets.

### Relationship To Other Concepts

- Related to [metrics-instrumentation](/concepts/metrics-instrumentation) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [materialized-view](/concepts/materialized-view) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [stream-to-store](/concepts/stream-to-store) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `time-series` when the important observation is this specific architectural concern within a domain-modeling or product-domain concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
