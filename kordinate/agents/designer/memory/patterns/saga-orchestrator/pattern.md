---
description: Saga Orchestrator architectural pattern
curated: true
scope: global
preloaded: none
graphable: true
---
# Saga Orchestrator

## Recognition

How to identify this pattern in code.

### Signatures

- Central coordinator class managing a sequence of saga steps (`SagaOrchestrator`, `SagaManager`, `SagaCoordinator`)
- Step sequence definition with forward action and compensating action per step
- Compensating actions that undo completed steps on failure
- Step status tracking (pending, completed, failed, compensated)
- Saga state machine persisted to a database or event store
- Distinct from choreography-based saga -- one service drives the flow, not distributed event reactions

### Confidence

- **high** -- dedicated orchestrator class with step definitions, compensation logic, and persisted saga state
- **medium** -- sequential service calls with rollback logic but no formal saga abstraction or state tracking
- **low** -- multi-service workflow with some error handling but no compensating actions or saga terminology

## Architecture

Look for a central coordinator driving distributed transactions through explicit steps with compensations.

### Review Checklist

- Every forward step has a corresponding compensating action defined
- Saga state is persisted so that recovery can resume or compensate after a crash
- Step execution is idempotent -- retrying a step does not cause duplicate side effects
- Compensation is executed in reverse order of completed steps
- The orchestrator handles partial failure -- it does not leave the system in an inconsistent state
- Timeouts are defined per step to prevent indefinite blocking

### Anti-patterns

- Missing compensation for one or more steps -- partial failure leaves inconsistent state
- Saga state kept only in memory -- a process crash loses the transaction progress
- Non-idempotent steps that produce duplicates on retry
- Orchestrator tightly coupled to step implementations instead of calling them through interfaces
