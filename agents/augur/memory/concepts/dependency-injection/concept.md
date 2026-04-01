---
description: Dependency Injection/IoC architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [design, architectural]
---
# Dependency Injection

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
