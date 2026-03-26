---
description: Test Pollution anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Test Pollution

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Tests modifying global state (module-level variables, class attributes, singletons)
- Missing teardown or cleanup (`setUp` without matching `tearDown`)
- `setUpClass` without matching `tearDownClass`
- Shared fixtures mutated between tests (e.g., appending to a list in a shared fixture)
- Database not reset between test cases (previous test data affecting subsequent tests)
- Environment variables set in one test and not restored
- Monkey-patching without restoration (manual `module.func = mock` without cleanup)
- Global registry or cache populated by tests and never cleared

### Confidence

- **high** -- tests pass individually but fail when run together, and the failure depends on which test ran first
- **medium** -- `setUpClass` modifies shared state without `tearDownClass`, or fixtures are mutated across tests
- **low** -- tests use global state but have not yet shown order-dependent failures

## Impact

Test order dependencies and intermittent failures, making the test suite unreliable and hiding real bugs behind environmental noise.

### Symptoms

- Tests pass in isolation (`pytest test_file.py::test_one`) but fail when run as a full suite
- Adding or removing a test causes unrelated tests to start failing
- Test results differ between local runs and CI due to execution order
- Debugging test failures requires understanding which tests ran before the failing one
- Flaky failures disappear when test ordering changes

### Remediation

- Use fresh fixtures per test (`setUp`/`tearDown` or `pytest` function-scoped fixtures)
- Always pair `setUpClass` with `tearDownClass` to restore class-level state
- Use `unittest.mock.patch` or `monkeypatch` (pytest) which auto-restore on test exit
- Reset database state between tests with transactions (rollback after each test) or truncation
- Run tests in random order (`pytest-randomly`) to detect pollution early
