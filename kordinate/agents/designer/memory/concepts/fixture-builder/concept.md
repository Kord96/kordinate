---
description: Test Fixture / Data Builder architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [testing]
---
# Test Fixture / Data Builder

## Recognition

How to identify this pattern in code.

### Signatures

- `*Factory` or `*Builder` classes in test directories (`UserFactory`, `OrderBuilder`)
- `factory_boy` with `factory.Factory`, `factory.SubFactory`, `factory.LazyAttribute` in Python
- `faker` or `Faker` library usage for generating realistic test data
- `build()`, `create()`, `make()` methods returning fully constructed test objects
- Test data creation helpers with default values and optional overrides
- `FactoryBot.define` or `FactoryBot.create` in Ruby tests
- Builder pattern with method chaining: `.with_name()`, `.with_status()`, `.build()`

**Not this pattern (Python):** `@pytest.fixture` alone does not indicate the fixture-builder pattern. Every Python test suite using pytest has fixtures -- the pattern is specifically about *builder/factory* classes or functions that construct complex test data with defaults and overrides. A `conftest.py` with simple fixtures returning constants or database connections is standard pytest, not the fixture-builder pattern. Look for `factory_boy`, `Faker`, or custom builder classes with `.create()/.build()` methods in test directories.

### Confidence

- **high** -- Dedicated factory/builder classes with sensible defaults, overrides, and composition of nested objects
- **medium** -- Helper functions that construct test data but without a consistent builder API or factory library
- **low** -- `conftest.py` with parametrized fixtures that return complex objects with default values

## Architecture

Look for centralized, composable test data construction that keeps tests focused on the scenario rather than setup.

### Review Checklist

- Factories provide sensible defaults so tests only override the fields relevant to the scenario
- Complex object graphs use nested factories or sub-builders rather than manual wiring
- Factory definitions live in a shared test utilities module, not duplicated across test files
- Builders support both in-memory objects and persisted records (where applicable)
- Generated data is deterministic or seed-controlled for reproducible tests

### Anti-patterns

- Every test file has its own copy-pasted object construction code instead of using shared factories
- Factories with too many required parameters, forcing callers to specify irrelevant fields
- Builders that silently create side effects (database writes, API calls) when only an in-memory object is needed
- Over-reliance on random data without seeding, causing flaky tests that pass or fail non-deterministically
