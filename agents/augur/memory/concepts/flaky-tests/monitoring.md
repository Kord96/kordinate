---
description: Flaky Tests — monitoring guidance
type: supplementary
---
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
