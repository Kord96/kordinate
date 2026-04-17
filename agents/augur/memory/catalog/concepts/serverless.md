---
description: Serverless / FaaS architectural pattern
type: pattern
graphable: true
abstraction:
- architectural
- deployment
status: primary
scope: cross-cutting
relationships:
  related_to:
  - event-driven
  - scheduler
  - service-manager
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Serverless / FaaS

## Recognition

How to identify this pattern in code.

### Signatures

- Lambda handler functions: `handler(event, context)`, `exports.handler`, `def lambda_handler`
- Cloud Functions entry points: `@functions_framework.http`, `@app.route` with Lambda integration
- Infrastructure-as-code: `serverless.yml`, `template.yaml` (SAM), `cdk.Stack` with Lambda constructs
- Cold start mitigation: provisioned concurrency config, connection pooling outside handler, lazy initialization
- Stateless request handlers with no local filesystem or in-memory state between invocations
- API Gateway + Lambda integration patterns, event source mappings (SQS, S3, DynamoDB Streams)
- Step Functions or Durable Functions for orchestrating multi-step workflows

### Confidence

- **high** -- `serverless.yml` or SAM template with Lambda function definitions and API Gateway triggers
- **medium** -- Stateless handler functions with event/context signatures and cloud provider SDK usage
- **low** -- Small isolated functions invoked by HTTP with no persistent process, but no explicit FaaS framework

## Architecture

Look for stateless, event-driven handlers with external state management and awareness of cold start and execution limits.

### Review Checklist

- Handlers are stateless -- no in-memory state carried between invocations
- Connections to databases and external services are initialized outside the handler (reused across warm invocations)
- Cold start impact is understood and mitigated for latency-sensitive paths
- Function timeout, memory, and concurrency limits are explicitly configured per function
- Idempotency is handled for event-driven triggers (SQS, streams) since at-least-once delivery is the norm
- Observability is in place: structured logging, distributed tracing with X-Ray or equivalent

### Anti-patterns

- Storing state in global variables expecting it to persist reliably across invocations
- Long-running functions approaching the execution timeout limit instead of decomposing into steps
- Ignoring cold start latency for synchronous user-facing endpoints
- Deploying monolithic handlers that bundle unrelated logic into a single function

### Relationship To Other Concepts

- Related to [event-driven](/concepts/event-driven) because serverless functions are often triggered by events rather than long-lived request servers.
- Related to [scheduler](/concepts/scheduler) when functions are invoked on time-based triggers.
- Related to [service-manager](/concepts/service-manager) as a contrast: serverless hides most service lifecycle ownership from the application team.

### Boundary

Use `serverless` when computation is packaged into platform-managed functions or services with ephemeral execution and platform-owned lifecycle concerns.

Do not use it for any containerized or autoscaled service. The key signal is platform-managed function-style execution.
