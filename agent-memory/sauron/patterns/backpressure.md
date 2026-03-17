# Backpressure — Monitoring Perspective

Track producer-consumer imbalance and resource exhaustion signals.

## Key Metrics

- `queue_depth` (gauge) — pending items between producer and consumer
- `consumer_lag` (gauge) — how far behind the consumer is (Kafka offset lag)
- `memory_pressure_bytes` (gauge) — buffer memory usage approaching limits
- `dropped_messages_total` (counter) — messages shed under load

## Alerts

- Queue depth growing monotonically (consumer not keeping up)
- Consumer lag exceeding SLA threshold
- Memory usage approaching configured buffer limits
- Non-zero drop rate when drops are not expected
