---
description: Workflow Engine architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [lifecycle, integration]
---
# Workflow Engine

## Recognition

How to identify this pattern in code.

### Signatures

- `@task`, `@dag`, `@workflow`, `@step` decorators defining workflow steps
- DAG (directed acyclic graph) definitions with explicit step dependencies
- State machine implementations tracking workflow progress (`pending`, `running`, `completed`, `failed`)
- Libraries: Airflow, Temporal, AWS Step Functions, Prefect, Celery chains/chords, Argo Workflows
- Workflow definition files (YAML/JSON DAGs, state machine definitions)
- Step retry policies, timeout configuration, and conditional branching
- `workflow_id` or `run_id` used for tracking execution instances

### Confidence

- **high** -- DAG definitions with explicit dependencies, a workflow engine library, and step state tracking with retry policies
- **medium** -- Sequential task chains with dependency ordering and basic state tracking, but no formal DAG library
- **low** -- Chained function calls with manual error handling that loosely resembles a workflow but has no formal orchestration

## Architecture

Look for DAG-based task orchestration with explicit step dependencies, state tracking, and failure handling.

### Review Checklist

- Each step is idempotent and safe to retry on failure
- Step dependencies form a valid DAG (no circular dependencies)
- Workflow state is persisted so execution can resume after a crash
- Timeout and retry policies are defined per step, not globally
- Failed workflows can be manually retried from the point of failure
- Workflow execution is observable (step-level status, duration, and logs)

### Anti-patterns

- Workflows defined in imperative code with no visible dependency graph
- Steps that cannot be retried because they produce side effects without idempotency keys
- Monolithic workflow with dozens of tightly coupled steps instead of composed sub-workflows
- No persistent state -- a process crash loses all progress and requires full restart

See also: saga (for distributed transactions with compensation)
