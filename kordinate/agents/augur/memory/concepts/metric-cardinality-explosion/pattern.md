---
description: Metric Cardinality Explosion anti-pattern
type: anti-pattern
observable: true
graphable: false
---
# Metric Cardinality Explosion

## Recognition

How to identify this anti-pattern in code.

### Signatures

- User ID, request ID, URL path, or email used as Prometheus label values
- Unbounded label cardinality on Counter, Histogram, or Gauge metrics
- `labels=["user_id"]` or `labels=["request_id"]` on metric definitions
- Metric names generated dynamically (`f"request_{endpoint}_total"`)
- Labels derived from user input, query parameters, or request paths without normalization
- Prometheus scrape duration increasing over time

### Confidence

- **high** -- a metric label is populated from user-supplied or request-specific data (user ID, session ID, full URL path), confirmed by `prometheus_tsdb_head_series` growing unboundedly
- **medium** -- label values come from a set that grows with traffic (e.g., raw URL paths, email addresses) rather than a fixed enumeration
- **low** -- metric definition includes a label whose cardinality is not documented or bounded, or dynamic string formatting is used in metric names

## Impact

Prometheus runs out of memory, queries time out, and storage costs explode from millions of unique time series.

### Symptoms

- Prometheus OOM kills or restarts under normal traffic
- `prometheus_tsdb_head_series` count grows without bound
- PromQL queries on affected metrics time out or return partial results
- Grafana dashboards using high-cardinality metrics fail to load
- TSDB compaction takes progressively longer

### Remediation

- Use only bounded, low-cardinality values as metric labels (HTTP method, status code, service name)
- Replace user/request IDs in labels with bucketed or hashed groupings if segmentation is needed
- Add a linting rule or CI check that rejects metric definitions with known high-cardinality label names
- Use recording rules to pre-aggregate high-cardinality metrics into lower-cardinality summaries
- Audit existing metrics with `topk` by label value count and remediate any exceeding a threshold (e.g., 1000 unique values)
