---
description: Choreography architectural pattern
curated: true
scope: global
---
# Choreography


## Architecture

Look for clear event contracts and no hidden coupling between services.

### Review Checklist

- Event schemas are versioned and documented — consumers know what to expect
- Each service can be deployed independently without breaking the chain
- Event flows are traceable end-to-end (correlation IDs in every event)
- Failure in one service does not silently stall the entire workflow

### Anti-patterns

- Implicit ordering assumptions — Service B assumes A always fires first
- Event ping-pong — two services triggering each other in a loop
- No observability — impossible to reconstruct what happened from logs alone
- Choreography used where a saga/orchestrator would be clearer (too many steps)

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
