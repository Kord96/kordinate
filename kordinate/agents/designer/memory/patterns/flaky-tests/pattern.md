---
description: Flaky Tests anti-pattern
type: anti-pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
---
# Flaky Tests

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `sleep()` or `time.sleep()` in test code to wait for conditions
- `time.time()` assertions comparing wall-clock timestamps
- Shared mutable test state (class-level variables modified across test methods)
- Tests depending on execution order (passing in sequence, failing in isolation)
- Network calls in unit tests (HTTP requests to external services without mocking)
- `@retry` or retry decorators on test methods
- Assertions on floating-point equality without tolerance
- Tests depending on file system ordering or locale settings
- Race conditions from multithreaded test fixtures

### Confidence

- **high** -- `sleep()` calls in tests combined with intermittent CI failures on the same test, or `@retry` decorators on test methods
- **medium** -- tests make real network calls or depend on shared mutable state, and CI shows occasional failures
- **low** -- tests use `time.time()` or depend on execution order, but failures have not yet been observed

## Impact

Eroded trust in CI, leading teams to ignore failures, disable tests, or merge despite red builds.

### Symptoms

- The same test passes and fails on consecutive CI runs with no code change
- Developers re-run CI pipelines hoping for green without investigating failures
- A growing list of tests marked `@skip`, `@xfail`, or `@flaky`
- CI failure notifications are routinely ignored by the team
- Test suite reliability metrics show less than 99% pass rate on unchanged code

### Remediation

- Replace `sleep()` with explicit waits or polling with timeout (e.g., `wait_for_condition()`)
- Mock all external network calls in unit tests; use contract tests for service integration
- Isolate test state: each test creates and tears down its own data, no shared mutables
- Run tests in random order (`pytest-randomly`) to surface order dependencies
- Track flaky tests with a quarantine system and fix or delete them within a sprint
