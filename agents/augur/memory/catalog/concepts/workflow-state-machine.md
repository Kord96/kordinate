---
description: Workflow state modeling note; prefer workflow-engine or state-machine as the primary concept
type: domain-model
abstraction: [data, lifecycle]
status: compatibility
scope: backend
relationships:
  related_to: [workflow-engine, state-machine]
---
# Workflow / State Machine

This concept is retained as a compatibility note, but Augur should usually prefer one of:

- [workflow-engine](/concepts/workflow-engine) for multi-step orchestration
- [state-machine](/concepts/state-machine) for explicit states, transitions, and guards

Use this page only when the code intentionally blurs both concerns and the distinction is genuinely unclear.

## Recognition

### Signatures

- State enum or constants: `PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`, `CANCELLED`
- Transition functions that validate current state before allowing change
- Guard conditions on transitions (e.g., "can only approve if all reviewers signed off")
- State machine libraries: XState (JS), transitions (Python), statesman (Ruby), Spring Statemachine
- Workflow engines: Temporal, Airflow, Prefect, Step Functions, Camunda
- Status columns with CHECK constraints limiting valid values
- Event handlers triggered on state entry/exit
- State history tables recording every transition with timestamp and actor

### Confidence

- **high** — explicit state machine library or workflow engine with defined states, transitions, and guards
- **medium** — status field with transition validation logic but no formal state machine
- **low** — status field updated directly without transition validation
