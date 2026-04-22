---
kind: concept
name: dependency-injection
signatures:
  concept: dependency-injection
  positive:
    strong:
    - framework DI decorators or dependency providers
    - constructor-injected collaborators with centralized wiring
    medium:
    - manual constructor injection without formal container
    weak:
    - generic helper receiving collaborators as args
  negative:
  - service locator calls scattered in business logic
  - classes constructing concrete dependencies inline
  notes:
  - Strong matches should still check for service-locator anti-patterns.
source:
  memory_concept: memory/catalog/concepts/dependency-injection.md
type: pattern
abstraction:
- design
- architectural
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: di-constructor-or-container
    prompt: Are collaborators provided through constructors, framework DI, or a composition
      root rather than instantiated inline?
    weight: 3
    signals:
    - Depends(
    - '@Injectable'
    - '@Autowired'
  - id: di-no-service-locator
    prompt: Is the pattern true DI rather than arbitrary runtime service-location
      calls?
    weight: 3
    signals:
    - container.get
    - injector.get
monitoring:
  applies_to:
  - component
  health_signals: []
  business_metrics: []
  gaps:
  - Dependency injection itself is not a runtime health signal; monitor the injected
    collaborators instead.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Constructor parameters that are interfaces/protocols, not concrete classes
- Decorators: `@inject`, `@Autowired`, `@Injectable`, `@Provides`
- DI container or service registry: `Container`, `Injector`, `ServiceProvider`, `Registry`
- Python: `dependency-injector` library (`providers`, `containers`), `injector` library, `fastapi.Depends`
- Java/Kotlin: Spring `@Autowired`/`@Component`, Dagger `@Inject`/`@Module`, Guice
- JS/TS: Angular `@Injectable`, NestJS `@Inject`, InversifyJS, tsyringe

### Confidence

- **high** -- DI container with explicit bindings (interface to implementation), constructor injection throughout
- **medium** -- constructor accepts interfaces and callers pass implementations, but no formal container
- **low** -- functions receiving collaborators as parameters (manual poor-man's DI)

## Architecture

Look for inversion of control: high-level modules define interfaces, low-level modules implement them, and a container wires them together.

### Relationship To Other Concepts

- `dependency-injection` is the composition mechanism: who constructs collaborators and how bindings are supplied.
- It often appears inside `layered` and `hexagonal` systems but does not by itself define the architecture shape.

### Review Checklist

- Dependencies are injected, not constructed internally (no `new ConcreteClass()` inside business logic)
- Binding configuration is centralized (composition root), not scattered
- Scopes are correct (singleton vs request vs transient) and documented
- Circular dependencies are absent or explicitly broken with lazy injection
- Test configuration can substitute real dependencies with fakes without code changes
- Container is initialized once at startup, not resolved dynamically at runtime

### Anti-patterns

- Service locator disguised as DI (classes calling `container.get()` at arbitrary points)
- Over-injection: dozens of constructor parameters indicating a god class
- Registering concrete classes directly instead of binding interface to implementation
- Runtime resolution scattered throughout business logic instead of at composition root

### Boundary

Do not use `dependency-injection` for any parameter passing. Prefer it only when construction and binding are intentionally inverted away from business code.
