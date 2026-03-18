# Circuit Breaker — Design Perspective

```
        success           threshold            timeout
          │                exceeded               │
          ▼                   │                    ▼
      ┌────────┐         ┌───┴───┐         ┌───────────┐
      │ CLOSED │──fail──►│ OPEN  │──wait───►│ HALF-OPEN │
      │        │         │       │         │           │
      │ normal │         │reject │         │  1 probe  │
      │  flow  │         │  all  │         │  request  │
      └────────┘         └───────┘         └─────┬─────┘
          ▲                                      │
          └──────── probe succeeds ──────────────┘
```

Look for correct state machine implementation: closed -> open -> half-open.

## Review Checklist

- Failure threshold and recovery timeout are configurable, not hardcoded
- Half-open state allows a limited number of probe requests
- Circuit state is observable (logging or metrics on state transitions)
- Fallback behavior is explicitly defined (not silent swallowing)

## Anti-patterns

- Wrapping every call in a circuit breaker (only external dependencies need them)
- No fallback — circuit opens and the caller gets raw exceptions
- Shared circuit state across unrelated dependencies
