---
description: Chain of Responsibility architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Chain of Responsibility

## Recognition

How to identify this pattern in code.

### Signatures

- Middleware chains: `app.use()`, `next()` calls, ordered handler lists
- Handler objects with `next` or `successor` references
- Pipeline or processor chain: `pipeline.add()`, `chain.add_handler()`
- Express/Koa middleware stacks, Django `MIDDLEWARE` setting, ASP.NET middleware pipeline
- Python: logging `Handler` with `setLevel()` chains, WSGI/ASGI middleware
- Go: `http.Handler` wrapping with `ServeHTTP`, middleware functions returning `http.Handler`
- Java: servlet filters, Spring interceptors

### Confidence

- **high** -- ordered list of handlers where each handler can process or pass to `next`, with explicit chain construction
- **medium** -- middleware registration with `use()`/`add()` and `next()` callback convention
- **low** -- if/else cascade where each branch handles a specific case (degenerate chain)

## Architecture

Look for correct chain traversal: each handler decides to process, pass through, or short-circuit.

### Review Checklist

- Each handler has a single responsibility and clear criteria for when it processes vs passes
- Chain order is intentional and documented (auth before validation before business logic)
- A request that no handler processes is handled explicitly (default/fallback handler at end)
- Handlers do not modify the request in ways that break downstream handlers
- Chain can be reconfigured without modifying individual handlers
- Short-circuit behavior (early return) is well-defined and tested

### Anti-patterns

- Handlers that silently swallow requests without calling next (request disappears)
- Order-dependent handlers with no documentation of required ordering
- Chain with no termination -- request falls through without any handler processing it
- Handlers with circular references causing infinite loops
