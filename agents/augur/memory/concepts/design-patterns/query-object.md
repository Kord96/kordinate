---
kind: concept
name: query-object
signatures: {}
type: pattern
abstraction:
- design
- data
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Dedicated read-side classes such as `UserQuery`, `OrderSearch`, or `FindInvoicesQuery`
- Filtering, sorting, projection, and pagination logic encapsulated outside domain entities
- Query handlers or repository methods accepting structured query parameter objects
- Read models or DTO projections assembled separately from write logic
- Search or reporting paths built from composable predicates and projections

### Confidence

- **high** -- dedicated query types or handlers encapsulate read filtering, projection, and pagination independently of write logic
- **medium** -- repository or service layer contains clearly separated read-only query builders, but no formal query object type exists
- **low** -- ad hoc filtering code appears in controllers or handlers with only light extraction

## Architecture

Look for explicit read-side objects that keep query intent separate from mutation logic and entity behavior.

### Review Checklist

- Read concerns are isolated from mutation flows
- Query objects express filters, sort order, projection, and pagination cleanly
- Query logic does not leak transport-layer concerns into persistence code
- Expensive query composition stays out of entities and generic service classes

### Anti-patterns

- Controllers constructing raw SQL or ORM chains inline for every endpoint
- Domain entities accumulating reporting and filtering responsibilities
- One generic query object with dozens of optional flags and ambiguous semantics

### Relationship To Other Concepts

- Related to [specification](/concepts/specification) when composable predicates feed read-side filtering logic.
- Related to [repository](/concepts/repository) because repositories often execute or expose query objects at the data boundary.
- Related to [cqrs](/concepts/cqrs) when dedicated read-side models and handlers give query objects a more explicit architectural role.

### Boundary

Use `query-object` when read behavior is intentionally encapsulated in dedicated query types, handlers, or builders.

Do not use it for any repository method with parameters. The key signal is explicit read-side object modeling.
