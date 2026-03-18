# stoik — Design Perspective

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
