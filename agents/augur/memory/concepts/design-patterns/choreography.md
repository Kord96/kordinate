---
kind: concept
name: choreography
signatures: {}
type: pattern
abstraction:
- integration
- architectural
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Event-based service communication without a central orchestrator or saga coordinator
- `EventBus` usage (Guava, Vert.x, or custom) for in-process event dispatch
- `@EventListener` annotations (Spring) for reacting to published domain events
- SNS/SQS fan-out topology where services publish events and others subscribe independently
- Kafka topic-to-topic chaining where each service consumes from one topic and produces to another
- NATS subjects used for decoupled pub/sub communication between services
- Absence of `Saga`, `Orchestrator`, or `Workflow` classes coordinating multi-service flows

### Confidence

- **high** -- multiple services communicating exclusively through events with no orchestrator, correlation IDs propagated, and event schemas versioned
- **medium** -- event-driven communication present but some services also use synchronous calls, or event flow is partially orchestrated
- **low** -- pub/sub infrastructure in use but event contracts are implicit and no correlation ID tracing exists

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

### Relationship To Other Concepts

- Related to [saga](/concepts/saga) because sagas can be implemented through choreography rather than a central coordinator.
- Related to [event-driven](/concepts/event-driven) because choreography usually relies on event-based reactions between participating services.
- Related to [orchestration](/concepts/orchestration) as the main alternative where a central coordinator controls workflow progress.

### Boundary

Use `choreography` when a multi-step cross-service flow emerges from peers reacting to events without one central controller.

Do not use it for any event-driven system. The defining feature is decentralized workflow coordination.
