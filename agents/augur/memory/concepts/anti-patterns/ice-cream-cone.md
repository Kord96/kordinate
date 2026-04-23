---
kind: concept
name: ice-cream-cone
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `test/e2e` or `tests/integration` directory much larger than `test/unit` or `tests/unit`
- Many Selenium, Playwright, or Cypress tests with few corresponding unit tests
- Test runtime dominated by integration or end-to-end tests (CI taking 30+ minutes)
- Inverted test pyramid: more high-level tests than low-level tests
- Test configuration heavily focused on browser setup, Docker Compose, or service orchestration
- Minimal use of mocks or stubs; most tests hit real databases or services
- `conftest.py` or test fixtures primarily spinning up full application stacks

### Confidence

- **high** -- e2e test count exceeds unit test count by 2x or more, and CI runtime is dominated by integration tests
- **medium** -- test/e2e directory has more files than test/unit, or CI regularly exceeds 20 minutes due to integration tests
- **low** -- the project has integration tests but few unit tests, though the codebase may be small enough that this is intentional

## Impact

Slow CI, flaky tests, and poor fault isolation because the test suite is top-heavy with expensive, broad-scoped tests.

### Symptoms

- CI pipelines take 30+ minutes, slowing development feedback loops
- Flaky test failures are common because end-to-end tests are sensitive to timing and environment
- When a test fails, it is difficult to pinpoint the exact module or function at fault
- Developers skip running tests locally because they are too slow
- Test maintenance burden is high due to brittle UI or integration test selectors

### Remediation

- Adopt the test pyramid: many unit tests, fewer integration tests, fewest end-to-end tests
- Convert broad integration tests to focused unit tests with mocks at service boundaries
- Reserve end-to-end tests for critical user journeys only (login, checkout, core workflows)
- Set CI time budgets and track test-level timing to identify slow tests for conversion
- Introduce contract tests (Pact, Schemathesis) to replace service-to-service integration tests

### Relationship To Other Concepts

- Related to [flaky-tests](/concepts/flaky-tests) because top-heavy integration suites often become timing- and environment-sensitive.
- Related to [contract-testing](/concepts/contract-testing) as one way to replace some broad end-to-end coverage with narrower interface checks.
- Related to [fixture-builder](/concepts/fixture-builder) because stronger low-level test utilities often help teams shift effort back toward unit and component tests.

### Boundary

Use `ice-cream-cone` when the test portfolio is inverted, with too much reliance on end-to-end or integration tests and too little low-level coverage.

Do not use it for any suite that merely includes integration tests; the issue is the inverted balance.
