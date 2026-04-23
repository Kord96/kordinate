---
kind: concept
name: orchestration
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

- Central coordinator service or module directing multi-step workflows
- `Orchestrator`, `Coordinator`, or `WorkflowService` types issuing commands to participants
- Explicit step sequencing, branching, retries, or compensation logic in one place
- Workflow state persisted outside individual participants
- Participants exposing task-style APIs while one controller advances the whole flow

### Confidence

- **high** -- one central coordinator owns step order, retries, and state for a multi-service or multi-component flow
- **medium** -- a service coordinates several downstream calls and transitions, but workflow state is only partially explicit
- **low** -- imperative glue code invokes several operations in sequence without durable workflow ownership

## Architecture

Look for one authority controlling workflow progress rather than peers reacting independently.

### Review Checklist

- One coordinator owns workflow progression and error handling
- Participant services remain simpler than the orchestrator and avoid hidden coupling
- Workflow state is durable enough to survive retries or restarts
- Compensation or rollback behavior is explicit where partial failure matters

### Anti-patterns

- Central coordinator that also owns every participant's domain logic
- Hidden orchestration spread across many handlers despite claiming a central workflow
- No durable state, forcing full restart after coordinator failure

### Relationship To Other Concepts

- Related to [choreography](/concepts/choreography) as the main alternative where peers coordinate indirectly through events instead of one controller.
- Related to [workflow-engine](/concepts/workflow-engine) when orchestration is implemented with durable task graphs, retries, and execution state.
- Related to [saga-orchestrator](/concepts/saga-orchestrator) when orchestration specifically coordinates compensating transactions across services.

### Boundary

Use `orchestration` when one component explicitly directs multi-step progress across participants or tasks.

Do not use it for any sequential code path. The defining signal is centralized workflow control.
