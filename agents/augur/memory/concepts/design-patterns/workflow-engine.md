---
kind: concept
name: workflow-engine
signatures: {}
type: pattern
abstraction:
- lifecycle
- integration
scope: backend
status: primary
review_questions:
  threshold: 6
  entries:
  - id: workflow-engine-explicit-orchestration
    prompt: Does the code orchestrate multi-step execution with explicit step or stage
      boundaries rather than one flat handler path?
    weight: 3
    signals:
    - workflow
    - stage
    - step
    - execute
  - id: workflow-engine-retries-or-timeouts
    prompt: Are retries, timeouts, or resumable execution part of the workflow runtime
      rather than generic helper logic?
    weight: 2
    signals:
    - retry
    - timeout
    - resume
  - id: workflow-engine-observable-progress
    prompt: Is workflow progress visible through run ids, stage status, queue depth,
      or step-level reporting?
    weight: 2
    signals:
    - run_id
    - status
    - queue
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: workflow.active.count
    description: Number of in-flight workflow runs or orchestration instances.
  - name: workflow.step.timeout.rate
    description: Rate of workflow stages or steps timing out before completion.
  - name: workflow.retry.rate
    description: Frequency of workflow retries or re-dispatch for failed stages.
  business_metrics:
  - name: workflow.completion.rate
    description: Fraction of workflow runs that reach successful completion over time.
  - name: workflow.time_to_completion
    description: End-to-end duration from workflow start to successful completion.
  - name: workflow.failure.by_stage
    description: Distribution of failed workflow runs grouped by the stage or step
      where they stop.
  gaps:
  - Without completion and stage-failure visibility, workflow health can look normal
    while real work stalls or degrades.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- `workflow-engine` is the orchestration concept: task graphs, retries, persistence, compensation, and long-running execution.
- `state-machine` is the more fundamental transition-model concept.
- If the code is only modeling entity states and transitions, prefer `state-machine`.
- If the code is orchestrating multi-step execution across tasks, workers, or services, prefer `workflow-engine`.

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

### Boundary

Use `workflow-engine` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use a nearby alternative label when this concept more precisely matches the code and intent.
