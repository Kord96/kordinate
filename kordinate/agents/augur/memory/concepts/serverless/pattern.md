---
description: Serverless / FaaS architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural, deployment]
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
