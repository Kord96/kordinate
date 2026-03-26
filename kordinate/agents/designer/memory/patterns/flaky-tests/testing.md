---
description: Flaky Tests — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
