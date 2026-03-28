---
description: Graceful Degradation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [resilience, lifecycle]
---
# Graceful Degradation

## Recognition

How to identify this pattern in code.

### Signatures

- Explicit fallback responses returned when a named dependency is unavailable, with degraded but functional behavior
- Reduced functionality mode toggled by health state or feature flags, with user-visible indicator
- Cached responses served as stale fallback when the live source is unavailable (`stale-while-revalidate`, `stale-if-error`)
- Circuit breaker fallback handlers providing alternative responses (see also: circuit-breaker)
- Feature flags disabling non-essential features under load to preserve core functionality
- Service mesh retry + fallback configuration (Istio `retries` + `fault.abort`)
- Java: `@HystrixCommand(fallbackMethod=)`, Resilience4j `Decorators.ofSupplier().withFallback()`, Spring Cloud `@CircuitBreaker(fallback=)`
- Go: explicit secondary data source or cached-result return on primary failure with health-based switching

### Negative signals (not sufficient for detection)

- The word `fallback` alone is NOT graceful degradation. Many contexts use "fallback" without degradation intent: encoding fallbacks, TLS protocol negotiation, default configuration values, test fallback names, font fallbacks, DNS fallback servers.
- `getFallbackName()`, `fallbackMockController`, `fallback to previous` in data recovery are not this pattern.
- Graceful *shutdown* (signal handling, drain-and-stop) is service-manager, not degradation.
- Default values in configuration (`orElse`, `getOrDefault`) are standard programming, not degradation.

**Not this pattern:** Standard `try/catch` error handling that returns an error response or default value is not graceful degradation. The pattern requires intentional design of degraded functionality modes -- the system continues to serve users with reduced but meaningful capability, not just catching errors. A catch block that returns `null` or logs and rethrows is error handling, not degradation.

**Not this pattern:** Graceful *shutdown* (signal handling, `server.Shutdown()`, drain-and-stop) is the service-manager pattern, not graceful degradation. Degradation means the service stays running with reduced functionality, not that it shuts down cleanly.

**Not this pattern:** The word "fallback" appearing in SSL/TLS negotiation (protocol fallback), encoding fallback, font fallback, locale fallback, or default configuration values is not graceful degradation. Look for fallback in the context of service-to-service calls or user-facing functionality degradation. Python: `except` blocks returning a default value or falling back to a simpler algorithm do not qualify unless there is an intentional degraded mode with multiple dependencies having independent fallback paths.

### Confidence

- **high** -- explicit fallback paths defined per dependency with documented degraded behavior and user notification
- **medium** -- some fallback logic exists with cached/stale data served during outages
- **low** -- catch-and-return-default logic that provides partial functionality but without intentional degradation design

## Architecture

Look for intentional fallback paths that keep the system usable when dependencies fail.

### Review Checklist

- Each non-critical dependency has a defined fallback behavior (cache, default, omit)
- Critical vs non-critical dependencies are explicitly classified
- Degraded mode is observable -- logs and metrics indicate when fallbacks activate
- Fallback responses are clearly distinguishable from normal responses (e.g., staleness indicators)
- System recovers automatically when the dependency comes back

### Anti-patterns

- All-or-nothing failure -- one dependency down takes the entire service offline
- Silent degradation where clients receive stale data without any indication
- Fallback logic that itself depends on the failing service
- No testing of degraded paths -- fallback code rots and fails when actually needed
