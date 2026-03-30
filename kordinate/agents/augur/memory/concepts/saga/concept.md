---
description: Saga architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [integration, resilience]
---
# Saga

## Recognition

How to identify this pattern in code.

### Signatures

- `Temporal` workflow definitions with activity sequences and compensation logic
- `MassTransit` saga state machines (`MassTransitStateMachine`, `SagaStateMachineInstance`)
- `NServiceBus` saga classes (`Saga<TSagaData>`, `IAmStartedByMessages`)
- Axon saga annotations (`@SagaEventHandler`, `@StartSaga`, `@EndSaga`)
- Compensating transaction methods paired with forward steps
- `SagaStep` classes or interfaces with `execute()` and `compensate()` methods
- Step status tracking (pending, completed, compensating, compensated)
- Saga state persistence to a database or durable store
- Central coordinator class managing a sequence of saga steps (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`)
- Distinct from choreography-based saga -- one service drives the flow, not distributed event reactions

### Confidence

- **high** -- Framework-specific saga imports (Temporal, MassTransit, NServiceBus, Axon) with compensating transaction definitions and step state tracking
- **medium** -- `SagaStep` with `compensate()` methods and saga state persistence, but using a custom coordinator instead of a framework
- **low** -- Multi-step distributed operations with manual rollback logic but no formal saga orchestration or step state tracking

## Architecture

Look for correct compensation logic and failure handling across distributed steps.

### Review Checklist

- Each step has a corresponding compensating action
- Compensation is idempotent (safe to retry on partial failure)
- Saga coordinator tracks step state (pending, completed, compensated)
- Timeout handling exists for steps that may hang

### Orchestration Variant

In the orchestration variant, a central coordinator class (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`) drives the distributed transaction through an explicit sequence of steps. Each step defines a forward action and a compensating action. The orchestrator persists saga state so that recovery can resume or compensate after a crash. Compensation is executed in reverse order of completed steps. This is distinct from choreography-based saga where distributed event reactions drive the flow -- here one service owns the entire sequence.

Key review points for the orchestration variant:
- Saga state is persisted (not in-memory only) so a process crash does not lose transaction progress
- Step execution is idempotent -- retrying a step does not cause duplicate side effects
- The orchestrator handles partial failure without leaving the system in an inconsistent state
- The orchestrator calls steps through interfaces rather than being tightly coupled to implementations

### Anti-patterns

- Missing compensation for one or more steps (partial rollback)
- Compensating actions that can themselves fail without retry
- Using sagas where a simple two-phase operation would suffice
- Saga state kept only in memory -- a process crash loses the transaction progress
- Non-idempotent steps that produce duplicates on retry
- Orchestrator tightly coupled to step implementations instead of calling them through interfaces
