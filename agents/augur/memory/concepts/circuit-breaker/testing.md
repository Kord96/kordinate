---
description: Circuit Breaker — testing guidance
---
## Testing

Test the full state machine lifecycle and verify fallback behavior activates correctly at each transition.

### Unit Tests

- Verify closed-to-open transition: inject failures up to the threshold and assert the circuit opens on the next failure
- Test half-open behavior: after recovery timeout, assert exactly the configured number of probe requests are allowed through
- Verify open-to-closed transition: successful probes in half-open state return the circuit to closed
- Assert fallback is invoked when the circuit is open — callers receive the fallback response, not an exception

### Integration Tests

- Wire a circuit breaker around a real dependency, degrade the dependency, and verify the breaker opens and closes as expected
- Test that circuit state is per-dependency — degrading one dependency does not open the breaker for another
- Verify metrics emission: state transitions, failure counts, and recovery probes all emit correct metric values

### Failure Injection

- Simulate a flapping dependency (alternating success/failure) and verify the circuit does not oscillate rapidly between states
- Inject total dependency failure and verify the circuit opens, then restore the dependency and confirm recovery through half-open probes
- Introduce latency exceeding the timeout threshold and verify slow responses count as failures toward the breaker threshold
