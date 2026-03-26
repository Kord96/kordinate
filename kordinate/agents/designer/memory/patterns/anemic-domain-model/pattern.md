---
description: Anemic Domain Model anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Anemic Domain Model

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Model or entity classes containing only getters and setters with no behavior or business logic methods
- All domain logic lives in `*Service` or `*Manager` classes that operate on passive data objects
- DTOs and data bags are passed everywhere with transformation logic external to the objects
- Domain objects have no validation, invariant enforcement, or state transition methods
- `*Service` classes with hundreds of methods that each manipulate the same entity types

### Confidence

- **high** -- entity classes have zero methods beyond getters/setters and all business rules are in separate service classes that accept those entities as parameters
- **medium** -- domain objects expose all fields publicly and service classes contain validation logic that belongs on the objects themselves
- **low** -- some business logic is on domain objects but key invariants (state transitions, validation) are enforced only by external services

## Impact

Business rules are scattered across service classes, making invariants impossible to enforce consistently and domain knowledge hard to locate.

### Symptoms

- The same validation logic is duplicated in multiple service classes that handle the same entity
- Invariant violations (invalid state transitions, negative balances) slip through because enforcement depends on which service method was called
- New developers cannot find business rules because they are spread across dozens of service files instead of living on the domain objects
- Unit testing requires instantiating heavyweight service classes instead of testing small domain methods in isolation
- Refactoring is risky because moving logic between services may break invariants that were implicitly maintained by call order

### Remediation

- Move business rules onto the domain objects themselves: validation in constructors, state transitions as methods
- Make domain object fields private and expose behavior through intention-revealing methods (`order.cancel()` instead of `order.setStatus("cancelled")`)
- Push invariant enforcement into the domain layer so invalid states are unrepresentable
- Use service classes only for orchestration (coordinating multiple aggregates, calling infrastructure) not for business logic
- Apply the "Tell, Don't Ask" principle: tell objects to perform actions rather than extracting data and computing externally

See also: ddd pattern (remediation)
