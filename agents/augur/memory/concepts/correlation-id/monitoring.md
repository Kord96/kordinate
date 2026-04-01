---
description: Correlation ID — monitoring guidance
type: supplementary
---
## Monitoring

Track correlation ID propagation completeness and use them to trace request flows.

### Key Metrics

- `requests_without_correlation_id_total` (counter) — requests missing a correlation ID (propagation gap)
- `correlation_hop_count` (histogram) — number of services a correlation ID traverses
- `trace_completeness_ratio` (gauge) — percentage of requests with full end-to-end correlation

### Alerts

- Correlation ID missing rate exceeding threshold (broken propagation in a service)
- Orphaned correlation IDs (started but no terminal service recorded completion)
- Duplicate correlation IDs generated (collision in ID generation)
