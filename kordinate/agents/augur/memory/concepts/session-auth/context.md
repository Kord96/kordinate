# Testing

- Test session creation on login and destruction on logout (server-side deletion, not just cookie removal)
- Verify session regeneration on login to prevent session fixation attacks
- Test cookie attributes: assert `HttpOnly`, `Secure`, and `SameSite` flags are set correctly
- Test session expiry by advancing time past the TTL and verifying the session is rejected
- Verify CSRF protection by submitting state-changing requests without the CSRF token and expecting rejection
- Test concurrent sessions: verify behavior when the same user logs in from multiple clients
- Test session store failover — verify graceful degradation when the session backend is unavailable
- Assert that sensitive data (passwords, tokens) is never stored in the session object

# Monitoring

- Track active session count and session store size — unbounded growth indicates missing TTL or cleanup
- Alert on session creation rate spikes that may indicate brute-force or session fixation attacks
- Monitor session store latency (Redis/DB lookup time) as it is on the critical path for every request
- Track CSRF validation failure rates — elevated failures may indicate an attack or misconfiguration
- Alert on session store availability — store outage blocks all authenticated requests
- Monitor session duration distribution to detect sessions that far exceed the configured TTL
- Dashboard showing login rate, active sessions, and session expiry events over time

