---
description: Test Doubles (Mock/Stub/Fake/Spy) architectural pattern
type: pattern
testable: true
graphable: false
abstraction:
- testing
status: primary
scope: backend
relationships:
  related_to:
  - fixture-builder
  - property-testing
  - snapshot-testing
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Test Doubles (Mock/Stub/Fake/Spy)

## Recognition

How to identify this pattern in code.

### Signatures

- `unittest.mock`, `MagicMock`, `patch()` decorators in Python test files
- `jest.fn()`, `jest.spyOn()` in JavaScript/TypeScript tests
- `sinon.stub()`, `sinon.spy()`, `sinon.fake()` in Node.js tests
- `gomock.NewController`, `mockgen` generated files in Go
- `mockito`, `@Mock`, `@InjectMocks`, `when().thenReturn()` in Java tests
- `Fake*` or `Mock*` or `Stub*` classes in test directories
- Spy assertions on `.call_count`, `.called_with`, `.toHaveBeenCalledTimes()`

### Confidence

- **high** — Mock/stub/fake classes implementing production interfaces found in test directories, with explicit verification of call behavior
- **medium** — `patch()` or `jest.fn()` usage in tests without dedicated fake implementations
- **low** — Test helper functions that return hardcoded values but are not explicitly named as doubles

## Architecture

Look for clear separation between the type of double (mock, stub, fake, spy) and appropriate use of each.

### Review Checklist

- Mocks verify behavior (was this method called?), stubs provide canned answers, fakes have working implementations -- each is used for its intended purpose
- Doubles implement the same interface/protocol as the real dependency
- Test doubles live in test directories, never imported by production code
- Spy assertions check meaningful interactions, not implementation details
- Fakes for external services (databases, APIs) are maintained alongside their real counterparts
- Double setup is extracted into helpers or fixtures to avoid repetition across tests

### Anti-patterns

- Mocking everything including the unit under test, leaving nothing real to verify
- Asserting on internal call order rather than observable outcomes
- Stubs that silently return success for every input, hiding real failure paths
- Production code importing from test double modules

### Relationship To Other Concepts

- Related to [fixture-builder](/concepts/fixture-builder) because stable test data and dependency substitution often appear together in focused tests.
- Related to [property-testing](/concepts/property-testing) when doubles help constrain one side of a system while generated inputs exercise another.
- Related to [snapshot-testing](/concepts/snapshot-testing) because both are testing techniques that trade different forms of test isolation and reviewability.

### Boundary

Use `test-doubles` when tests replace real collaborators with mocks, stubs, fakes, or spies that mimic the same interface.

Do not use it for every helper object in tests or for real in-memory implementations that are actually part of the production architecture.
