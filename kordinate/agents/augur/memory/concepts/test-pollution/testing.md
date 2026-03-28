---
description: Test Pollution — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Run tests in random order (`pytest-randomly`, `--randomize-order`) to detect order-dependent failures
- Verify that every `setUp`/`setUpClass` has a matching `tearDown`/`tearDownClass` restoring state
- Test each test case in isolation and as part of the full suite to detect pollution
- Use function-scoped fixtures by default — class or module scope only when explicitly justified
- Assert that global state (singletons, registries, environment variables) is restored after each test
- Use `unittest.mock.patch` or `monkeypatch` which auto-restore on test exit instead of manual patching
- Reset database state between tests via transaction rollback or truncation, not shared data
- Monitor CI for flaky tests and investigate as potential pollution before dismissing as intermittent
