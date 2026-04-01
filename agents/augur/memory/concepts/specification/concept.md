---
description: Specification Pattern architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design]
---
# Specification Pattern

## Recognition

How to identify this pattern in code.

### Signatures

- `is_satisfied_by()` or `isSatisfiedBy()` methods on business rule objects
- `and_spec()`, `or_spec()`, `not_spec()` combinators for composing specifications
- Classes named `*Specification`, `*Spec`, `*Rule`, `*Criteria`
- Chainable query filters that compose boolean predicates: `.where()`, `.and()`, `.or()`
- Predicate objects passed to repository or collection filtering methods
- Specification interface with a single `is_satisfied_by(candidate)` method

### Confidence

- **high** — Dedicated specification classes with `is_satisfied_by()`, composed via `and`/`or`/`not` combinators, used for domain validation or query building
- **medium** — Predicate functions or lambda chains used for filtering, but without formal specification classes or combinators
- **low** — Boolean methods on domain objects (`is_active()`, `is_eligible()`) that encode business rules but are not composable

## Architecture

Look for reusable, composable business rule objects that can be combined and applied to validation, filtering, and querying.

### Review Checklist

- Each specification encapsulates a single business rule and is named after that rule in domain language
- Specifications compose via `and`, `or`, `not` without the caller building ad-hoc boolean expressions
- The same specification works for both in-memory filtering and query generation (dual-purpose specs)
- Specifications are unit tested independently before being composed
- Complex business rules are expressed as named compositions, not deeply nested anonymous predicates
- Specifications accept the candidate as a parameter and have no hidden dependencies

### Anti-patterns

- Specifications that access databases, APIs, or other services inside `is_satisfied_by()` (side effects in predicates)
- Monolithic specification classes that encode multiple unrelated business rules
- Composing specifications but never testing the individual components in isolation
- Using specifications for trivial checks where a simple boolean expression would be clearer
