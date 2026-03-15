# stoik — Monitoring Perspective

Stream-to-store pipeline framework. Key monitoring surface for consumer-based services.

## Metrics

Prefix: `stoik_`

| Metric | Type | What it tells you |
|--------|------|-------------------|
| stoik_messages_consumed_total | counter | Throughput — consumer ingestion rate |
| stoik_messages_produced_total | counter | Throughput — producer output rate |
| stoik_buffer_flush_total | counter | Flush frequency — too low means stale data |
| stoik_buffer_flush_duration_seconds | histogram | Flush performance — spikes indicate DB pressure |
| stoik_errors_total | counter | Error rate — parse failures, flush failures |

## Health Checks

- Consumer lag: is the consumer keeping up with the topic?
- Buffer size: is it growing unbounded (flush failing)?
- Flush duration: is it within acceptable range?
- Dependency reachability: Kafka broker, DuckDB/store

## Dashboard Patterns

- Consumer throughput (messages/sec) per component
- Buffer flush rate and duration (p50, p95)
- Error rate by type (parse, flush, connection)
- Consumer lag trend

## Testing

Config file: `config.py`. Use nokrashi-tools TestSuite. Skip: `test_constants_in_config`.

Verify all stoik_ metrics are exposed and scraped by Alloy.
