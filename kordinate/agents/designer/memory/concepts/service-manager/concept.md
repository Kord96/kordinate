---
description: Service Manager architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [lifecycle]
---
# Service Manager

## Recognition

How to identify this pattern in code.

### Signatures

- Signal handlers registering for graceful shutdown (`signal.signal(signal.SIGTERM, handler)`)
- Health endpoints exposed at `/healthz` and `/readyz` paths
- `livenessProbe` and `readinessProbe` configuration in Kubernetes pod specs
- `ServiceManager` class coordinating startup, readiness, and shutdown phases
- `orchestrator` imports or orchestration-layer integration for lifecycle reporting
- Process lifecycle management with explicit state transitions (starting, ready, draining, stopped)
- Graceful shutdown logic draining in-flight requests and flushing buffers before exit
- `terminationGracePeriodSeconds` configuration in pod specs
- Go: goroutine lifecycle management with `sync.WaitGroup` and stop channel (`wg.Add(1)`, `defer wg.Done()`, `close(stopCh)` shutdown signaling)
- Go: `signal.Notify(ch, syscall.SIGINT, syscall.SIGTERM)` with `context.WithCancel` for coordinated shutdown
- Go: `http.Server.Shutdown(ctx)` for graceful HTTP server shutdown with in-flight request draining

### Confidence

- **high** -- `ServiceManager` class with SIGTERM signal handlers, `/healthz`+`/readyz` endpoints, and `livenessProbe`/`readinessProbe` in K8s specs
- **medium** -- Signal handlers with graceful shutdown drain logic and health endpoints, but without a dedicated manager class
- **low** -- Health check endpoints or liveness probes present without explicit shutdown handling or lifecycle state management

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
