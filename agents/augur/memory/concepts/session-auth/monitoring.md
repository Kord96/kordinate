---
description: Session-Based Authentication — monitoring guidance
type: supplementary
---
# Monitoring

- Track active session count and session store size — unbounded growth indicates missing TTL or cleanup
- Alert on session creation rate spikes that may indicate brute-force or session fixation attacks
- Monitor session store latency (Redis/DB lookup time) as it is on the critical path for every request
- Track CSRF validation failure rates — elevated failures may indicate an attack or misconfiguration
- Alert on session store availability — store outage blocks all authenticated requests
- Monitor session duration distribution to detect sessions that far exceed the configured TTL
- Dashboard showing login rate, active sessions, and session expiry events over time
