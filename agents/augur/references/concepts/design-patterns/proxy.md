---
kind: concept
name: proxy
signatures: {}
source:
  memory_concept: memory/catalog/concepts/proxy.md
type: pattern
abstraction:
- design
scope: backend
status: primary
---

# Explanation

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

### Relationship To Other Concepts

- Related to [decorator](/concepts/decorator) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `proxy` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
