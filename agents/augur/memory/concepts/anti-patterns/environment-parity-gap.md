---
kind: concept
name: environment-parity-gap
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

- Different databases in dev vs prod: SQLite in development, PostgreSQL in production
- Different runtimes or runtime versions across environments
- `if env == "development"` or `if ENV['RAILS_ENV'] == 'test'` blocks with substantially different behavior
- Docker Compose for local dev but Kubernetes in production with no configuration overlap
- In-memory fakes replacing real services in dev (in-memory queue instead of Kafka, local filesystem instead of S3)
- Test suites that pass locally but fail in CI due to environment differences

### Confidence

- **high** -- the project uses SQLite in dev and PostgreSQL in production, or uses an in-memory substitute for a critical infrastructure dependency
- **medium** -- environment-conditional code paths exist that change business logic, not just configuration values
- **low** -- minor version differences between dev and prod runtimes, or different OS distributions

## Impact

Bugs that only appear in production because dev and prod environments behave differently in ways that matter.

### Symptoms

- "Works on my machine" is a recurring phrase during incident postmortems
- SQL queries succeed in dev (SQLite) but fail in prod (Postgres) due to syntax or type differences
- Performance issues only surface in production because dev uses simplified infrastructure
- Race conditions and concurrency bugs invisible in single-threaded dev but devastating in prod
- Deployments that passed all local tests fail immediately in staging or production

### Remediation

- Use the same database engine, message broker, and cache in all environments (Docker makes this trivial)
- Replace environment-conditional logic with configuration injection: same code paths, different config values
- Use Docker Compose profiles or Tilt to replicate production topology locally
- Run CI tests against real dependencies (not mocks) using containers or testcontainers
- Maintain a parity checklist: for every production dependency, verify the dev equivalent is the same technology

### Relationship To Other Concepts

- Related to [flaky-tests](/concepts/flaky-tests) because environment drift often shows up first as tests that pass locally but fail elsewhere.
- Related to [config-management](/concepts/config-management) because mismatched configuration and dependency wiring are common sources of parity gaps.
- Related to [infrastructure-as-code](/concepts/infrastructure-as-code) because reproducible environment definitions are one major remediation.

### Boundary

Use `environment-parity-gap` when development, test, staging, and production meaningfully differ in ways that change behavior, correctness, or performance.

Do not use it for minor environment differences that do not materially affect system behavior.
