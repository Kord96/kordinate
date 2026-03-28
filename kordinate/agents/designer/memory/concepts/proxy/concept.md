---
description: Proxy architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Proxy

## Recognition

How to identify this pattern in code.

### Signatures

- Class implementing the same interface as the real object but controlling access to it
- Lazy loading proxies that defer object creation until first use
- Caching proxies that return stored results for repeated calls
- Protection proxies that check permissions before delegating
- Classes named `*Proxy`, `Virtual*`, `Remote*`, `Lazy*`
- Virtual proxy for expensive objects (large images, database connections)
- Remote proxies hiding network communication behind a local interface
- Go: `httputil.ReverseProxy` for HTTP reverse proxying
- Go: struct implementing the same interface as the real object, holding a reference and adding cross-cutting behavior (logging, caching, auth checking)
- Java: `java.lang.reflect.Proxy` dynamic proxy, Spring AOP proxies

**Not this pattern:** JavaScript's `new Proxy()` used for reactive state tracking (Vue, MobX), property access interception for API ergonomics, or meta-programming (e.g., creating fluent APIs via `Proxy` handler traps) is not the GoF Proxy pattern. The GoF Proxy specifically requires a proxy class that implements the same interface as the real subject and controls access to it. A JavaScript `Proxy` used to intercept property gets/sets for reactivity or validation is closer to the observer or decorator pattern.

**Not this pattern:** `__getattr__` in Python used to delegate attribute access to an inner object is not sufficient for the Proxy pattern unless the class implements the same interface as the delegated object and adds access control, caching, or lazy loading. A simple `__getattr__` delegation is just attribute forwarding.

### Confidence

- **high** -- Class with the same interface as the subject that holds a reference to the real object and conditionally delegates calls
- **medium** -- Lazy initialization wrapper or access-control gate that defers to an underlying implementation
- **low** -- Simple wrapper that delegates all calls without adding any access control, caching, or lazy behavior

## Architecture

Look for the proxy providing transparent access control without leaking its presence to the client.

### Review Checklist

- Proxy implements the exact same interface as the real subject
- Client code is unaware whether it holds a proxy or the real object
- Proxy responsibility is singular: access control, lazy loading, caching, or remote access -- not all at once
- Lazy proxies handle initialization thread-safely in concurrent environments
- Caching proxies define clear invalidation strategy

### Anti-patterns

- Proxy that exposes additional methods not on the real subject's interface (breaks substitutability)
- Caching proxy with no invalidation -- stale data served indefinitely
- Protection proxy that duplicates authorization logic already handled elsewhere
- Proxy chains where multiple proxies wrap each other without clear purpose

See also: decorator
