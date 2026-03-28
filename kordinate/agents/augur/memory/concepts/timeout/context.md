# Testing

- Test that every external call (HTTP, DB, gRPC, message broker) has an explicit timeout set
- Simulate slow dependencies and verify that calls time out within the configured window
- Test timeout error handling: timeout errors should be caught and handled distinctly from other failures
- Verify deadline propagation across service boundaries — downstream timeout must be shorter than upstream
- Test that connection timeouts and read/write timeouts are configured separately
- Assert that timeout values are configurable, not hardcoded literals in the source
- Test behavior when a deadline expires mid-call: verify cleanup and resource release
- Integration test the interaction between timeouts, retries, and circuit breakers

# Monitoring

- Track timeout error rates per dependency (HTTP, DB, gRPC) to identify degrading services
- Alert on timeout rate spikes — a sudden increase signals upstream latency or capacity issues
- Monitor latency percentiles (p50, p95, p99) relative to configured timeout values
- Track deadline propagation: log remaining deadline at each hop to detect tight or expired deadlines
- Alert when connection timeout and read/write timeout errors are conflated — they indicate different issues
- Dashboard showing timeout rates per dependency with configured timeout values overlaid
- Monitor for calls with no explicit timeout configured (silent hangs that never surface as errors)

# Deployment

- Review timeout values when deploying new dependencies or changing network topology
- Ensure downstream service timeouts are shorter than the upstream caller's timeout after each deployment
- Deploy timeout configuration changes independently from feature changes to isolate impact
- Verify that timeout values are configurable via environment or config, not requiring a code deploy to change
- Test timeout behavior in staging under realistic latency conditions before production release
- Coordinate timeout changes with circuit breaker and retry configurations to avoid compounding failures
- Monitor timeout error rates during and after deployment to catch misconfigured values early

