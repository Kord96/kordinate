# Bulkhead

```
  ┌──────────────────────────────────────────────┐
  │                  Service                     │
  │                                              │
  │  ┌──────────────┐  ┌──────────────┐         │
  │  │  Pool: DB    │  │ Pool: Cache  │         │
  │  │  max: 20     │  │  max: 10     │         │
  │  │  ┌────────┐  │  │  ┌────────┐  │  ┌────────────┐  │
  │  │  │ conn   │  │  │  │ conn   │  │  │Pool: Ext API│  │
  │  │  │ conn   │  │  │  │ conn   │  │  │  max: 5     │  │
  │  │  │ conn   │  │  │  └────────┘  │  │  ┌────────┐ │  │
  │  │  └────────┘  │  └──────────────┘  │  │ conn   │ │  │
  │  └──────────────┘                     │  └────────┘ │  │
  │                                       └────────────┘  │
  │  Failure in one pool does not drain the others.       │
  └──────────────────────────────────────────────────────┘
```

## Architecture

Look for isolated resource pools per dependency — one failing dependency must not exhaust all resources.

### Review Checklist

- Each external dependency has its own bounded resource pool (threads, connections)
- Pool sizes are configured per dependency based on expected load
- Pool exhaustion triggers rejection (fast fail), not unbounded queuing
- Metrics exposed per pool: active, idle, waiting, rejected counts

### Anti-patterns

- Single shared connection/thread pool across all dependencies
- No pool size limits — one slow dependency consumes all available resources
- Bulkhead without monitoring — pool exhaustion goes unnoticed until outage

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
