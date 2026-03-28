---
description: Dependency Injection/IoC architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
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
- Java: Jakarta/javax `@Inject` (CDI), Quarkus `@ApplicationScoped`/`@RequestScoped`, Micronaut `@Singleton`
- Java: HK2 `@Service`, Weld CDI, constructor injection with `final` fields and no `@Autowired` (implicit in Spring Boot)
- JS/TS: Angular `@Injectable`, NestJS `@Inject`, InversifyJS, tsyringe
- Go: `func New*()` constructors accepting interface parameters (constructor injection). Go rarely uses DI frameworks; `wire` (Google Wire) is the exception. The dominant Go idiom is explicit constructor injection with no container.

### Negative signals (not sufficient for detection)

- Go: bare keyword `inject` in Go code without a DI framework import (`google/wire`, `uber-go/fx`, `uber-go/dig`) is NOT dependency injection -- the word appears in unrelated contexts (SQL injection, header injection, etc.)
- Passing concrete structs to constructors without interface abstraction is configuration, not DI
- TypeScript: The word `inject` in CSS injection, HTML injection, or code injection contexts is not DI. Similarly, `Container` in Docker/OCI contexts, `IoC` mentioned in documentation without implementation, or React `Context.Provider` (which is React's context mechanism, not DI) are not DI
- Python: `Container` or `bind`/`resolve` in non-DI contexts (e.g., UI containers, socket bind, DNS resolve) are not DI. Require explicit DI framework imports or a ServiceContainer/IoC class with interface-to-implementation bindings
- Constructor parameters that accept concrete classes without abstraction (interfaces/protocols) is just parameterization, not dependency injection

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
