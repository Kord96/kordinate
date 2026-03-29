---
description: Timeout — monitoring guidance
type: supplementary
---
# Monitoring

- Track timeout error rates per dependency (HTTP, DB, gRPC) to identify degrading services
- Alert on timeout rate spikes — a sudden increase signals upstream latency or capacity issues
- Monitor latency percentiles (p50, p95, p99) relative to configured timeout values
- Track deadline propagation: log remaining deadline at each hop to detect tight or expired deadlines
- Alert when connection timeout and read/write timeout errors are conflated — they indicate different issues
- Dashboard showing timeout rates per dependency with configured timeout values overlaid
- Monitor for calls with no explicit timeout configured (silent hangs that never surface as errors)
