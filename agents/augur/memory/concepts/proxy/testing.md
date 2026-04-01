---
description: Proxy — testing guidance
type: supplementary
---
## Testing

Verify the proxy is transparent to callers, correctly delegates to the real subject, and enforces its specific concern (access control, caching, or lazy loading).

### Unit Tests

- Call every method on the proxy and verify it delegates to the real subject with identical arguments and return values
- Test the proxy's specific concern: lazy proxy defers creation until first use, caching proxy returns cached value on repeat calls, protection proxy rejects unauthorized access
- Verify the proxy implements the exact same interface as the real subject (no extra methods, no missing methods)
- Test cache invalidation (caching proxy) or permission changes (protection proxy) take effect on subsequent calls

### Substitutability Tests

- Run the same test suite against both the proxy and the real subject and verify identical behavior for the common interface
- Inject the proxy where the real subject is expected and verify client code functions without modification
- Verify type checks and isinstance calls (if used) accept the proxy as a valid implementation

### Concurrency Tests

- For lazy proxies: initialize from multiple threads simultaneously and verify the real subject is created exactly once
- For caching proxies: verify thread-safe cache reads and writes under concurrent access
