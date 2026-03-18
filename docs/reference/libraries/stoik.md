# stoik

## Designer Perspective

Stream-to-store pipeline framework. Kafka -> buffer -> batch flush -> DuckDB.

## Pattern

`producer -> buffer -> consumer`

Handles backpressure, retries, and exactly-once delivery.

## Key Classes

| Class | Role |
|-------|------|
| StoicProducer | Kafka producer with delivery callbacks |
| StoicBuffer | In-memory buffer with flush triggers (size/time) |
| StoicConsumer | Kafka consumer with commit tracking |
| StoicServer | FastAPI + FlightSQL server for serving stored data |

## When to Use

- Ingesting data from Kafka into DuckDB or other stores
- Event processing with buffered batch writes
- Stream pipelines that need backpressure and retry logic

## Architecture Review Checklist

- Is the buffer flush configured correctly (size + time triggers)?
- Are delivery callbacks handling errors (dead letter, retry)?
- Is commit tracking aligned with flush (exactly-once semantics)?
- Is FlightSQL server used for query access instead of direct DB reads?

## Install

```
pip install stoik        # core
pip install stoik[all]   # includes flight deps
```

## Deployer Perspective

Stream-to-store pipeline framework. Used by consumer components.

## Install

```
pip install stoik        # core
pip install stoik[all]   # includes flight deps
```

PyPI: `stoik`. Deploy method: `git-branch` (trusted publishing via GitHub Actions OIDC).

## Components

Projects using stoik typically have multiple consumer components (one per data type/topic) plus a FlightSQL server for query access.

Each consumer runs as a separate k8s Deployment, sharing the same base image.

## Deployment Notes

- All consumers use the same Docker image — component selection via entrypoint/args
- FlightSQL server needs the `stoik[all]` extras (flight dependencies)
- Buffer flush depends on DuckDB — ensure PVC is bound before scaling up
- Consumer lag may spike during rollout restarts — expected, recovers after rebalance

## Sauron Perspective

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

