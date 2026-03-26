---
description: Saga architectural pattern
curated: true
scope: global
preloaded: none
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

### Anti-patterns

- Missing compensation for one or more steps (partial rollback)
- Compensating actions that can themselves fail without retry
- Using sagas where a simple two-phase operation would suffice
