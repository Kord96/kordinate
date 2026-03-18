# Service Manager


## Architecture

Look for clean lifecycle phases: startup completes before serving, shutdown drains before closing.

### Review Checklist

- Startup validates config and dependencies before marking ready
- Health checks run periodically and report to orchestrator (liveness + readiness)
- Shutdown handles SIGTERM gracefully — drains in-flight requests, flushes buffers
- Startup failures produce clear error messages and exit with non-zero code
- No traffic served until readiness is explicitly signaled

### Anti-patterns

- Serving traffic before dependencies are connected (premature readiness)
- Shutdown kills in-flight requests without draining (data loss)
- Health check always returns healthy regardless of actual state
- No distinction between liveness and readiness probes

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
