## Testing

Identify, isolate, and eliminate flakiness through deterministic test design and root cause analysis.

### Detection

- Run suspect tests in a loop (50-100 iterations) in isolation to confirm flakiness without other test interference
- Check for time-dependent logic: tests that pass or fail near midnight, DST boundaries, or CI timezone differences
- Look for shared mutable state: tests that fail only when run after a specific other test indicate leaking state
- Identify network or filesystem dependencies that introduce nondeterminism

### Remediation

- Replace sleeps and timeouts with explicit wait conditions or polling with bounded retries
- Inject clocks and random seeds to make time-dependent and random-dependent tests deterministic
- Isolate database state per test using transactions that roll back, not shared fixtures
- Mock external services rather than relying on their availability in CI

### Prevention

- Quarantine flaky tests immediately — run them in a separate suite that does not block the main pipeline
- Require flaky tests to be fixed or deleted within a bounded time window (e.g., two sprints)
- Add flake detection to CI: automatically flag tests whose pass/fail status changes without a code diff

## Monitoring

Track test flakiness rates to quantify CI reliability and prioritize stabilization efforts.

### Key Metrics

- `test_flake_rate` (gauge) — percentage of test runs that flip between pass and fail without code changes, per test
- `ci_retry_total` (counter) — number of CI job retries triggered by flaky failures
- `flaky_test_count` (gauge) — total number of tests currently flagged as flaky
- `ci_wall_time_wasted_seconds` (counter) — cumulative CI time spent on retries caused by flaky tests

### Alerts

- Flaky test count exceeding team threshold (flakiness is eroding CI trust)
- A previously stable test becoming flaky (regression in test isolation or environment)
- CI retry rate trending upward over a rolling window (systemic flakiness problem)

