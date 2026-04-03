---
description: Session-Based Authentication — monitoring guidance
---
## Monitoring

Track session store health, session lifecycle events, and security-relevant anomalies.

### Key Metrics

- `session_active_count` (gauge) — number of active sessions in the session store
- `session_store_size_bytes` (gauge) — total session store size, detects unbounded growth from missing TTL
- `session_store_latency_seconds` (histogram) — session lookup time (Redis/DB), on the critical path of every request
- `session_creation_rate` (counter) — new sessions created per interval, partitioned by source
- `session_csrf_validation_failures_total` (counter) — CSRF token mismatches, may indicate attack or misconfiguration
- `session_duration_seconds` (histogram) — distribution of session lifetimes before expiry or logout

### Alerts

- Session creation rate spike (potential brute-force or session fixation attack)
- Session store unavailable (blocks all authenticated requests)
- Sessions exceeding configured TTL (cleanup mechanism broken)
- CSRF validation failure rate elevated beyond baseline
- Session store latency degraded (impacts every authenticated request)
