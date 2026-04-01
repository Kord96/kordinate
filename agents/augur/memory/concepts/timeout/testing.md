---
description: Timeout — testing guidance
type: supplementary
---
# Testing

- Test that every external call (HTTP, DB, gRPC, message broker) has an explicit timeout set
- Simulate slow dependencies and verify that calls time out within the configured window
- Test timeout error handling: timeout errors should be caught and handled distinctly from other failures
- Verify deadline propagation across service boundaries — downstream timeout must be shorter than upstream
- Test that connection timeouts and read/write timeouts are configured separately
- Assert that timeout values are configurable, not hardcoded literals in the source
- Test behavior when a deadline expires mid-call: verify cleanup and resource release
- Integration test the interaction between timeouts, retries, and circuit breakers
