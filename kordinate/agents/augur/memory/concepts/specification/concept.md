---
description: Specification Pattern architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Specification Pattern

## Recognition

How to identify this pattern in code.

### Signatures

- `is_satisfied_by()` or `isSatisfiedBy()` methods on dedicated business rule objects
- `and_spec()`, `or_spec()`, `not_spec()` combinators for composing specifications
- Classes explicitly named `*Specification`, `*Spec` implementing a specification interface
- Specification interface with a single `is_satisfied_by(candidate)` method and boolean composition
- DDD-style composable predicates used across repository queries and domain validation
- Transition guard conditions: list of predicate callables evaluated with `all()` / `any()` to gate operations (e.g., `conditions_met` checking `all(cond(instance) for cond in conditions)`)
- Python: `conditions` list where each element is a callable predicate, combined via `all(map(lambda c: c(instance), conditions))` for transition or operation guards
- Workflow/pipeline step preconditions: ordered list of boolean checks that must all pass before execution proceeds

**Not this pattern:** Generic `.where().and().or()` query builder chains are the builder pattern (SQL query construction), not the specification pattern. The specification pattern is specifically about domain-level composable business rule objects, not database query conditions. Also, simple boolean methods (`isActive()`, `isValid()`) on entities are not specifications unless they are standalone composable objects.

### Confidence

- **high** -- Dedicated specification classes with `is_satisfied_by()`, composed via `and`/`or`/`not` combinators, used for domain validation or query building
- **medium** -- Predicate objects implementing a common interface, passed to filtering/validation methods
- **low** -- Boolean methods on domain objects (`is_active()`, `is_eligible()`) used as reusable predicates but not formally composable

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
