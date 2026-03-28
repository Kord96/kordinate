---
description: stoik library reference
curated: true
scope: global
preloaded: none
---
# stoik

Stream-to-store pipeline framework. Kafka → buffer → batch flush → DuckDB. `pip install stoik` (or `stoik[all]` for FlightSQL).

## Architecture

Pattern: `producer -> buffer -> consumer`. Handles backpressure, retries, exactly-once delivery.

| Class | Role |
|-------|------|
| StoicProducer | Kafka producer with delivery callbacks |
| StoicBuffer | In-memory buffer with flush triggers (size/time) |
| StoicConsumer | Kafka consumer with commit tracking |
| StoicServer | FastAPI + FlightSQL server for serving stored data |

Review: buffer flush configured (size + time)? Delivery callbacks handle errors? Commit tracking aligned with flush? FlightSQL for query access?

## Monitoring

Prefix: `stoik_`

| Metric | Type | Meaning |
|--------|------|---------|
| stoik_messages_consumed_total | counter | Consumer ingestion rate |
| stoik_messages_produced_total | counter | Producer output rate |
| stoik_buffer_flush_total | counter | Flush frequency (too low = stale data) |
| stoik_buffer_flush_duration_seconds | histogram | Flush performance (spikes = DB pressure) |
| stoik_errors_total | counter | Error rate (parse, flush failures) |

Health: consumer lag, buffer size growth, flush duration, dependency reachability (Kafka, DuckDB). Dashboard: throughput per component, flush rate/duration, error rate by type, lag trend.

## Deployment

All consumers use same Docker image — component selection via entrypoint/args. FlightSQL needs `stoik[all]`. PVC must be bound before scaling (DuckDB). Consumer lag spikes during rollout — expected, recovers after rebalance.

Deploy method: git-branch (trusted publishing via GitHub Actions OIDC).

## Testing

Config file: `config.py`. Use nokrashi-tools TestSuite. Skip: `test_constants_in_config`. Verify all stoik_* metrics exposed and scraped.
