# Hexagonal (Ports & Adapters)

```
                  ┌───────────────────┐
HTTP ──► Adapter ─┤                   ├─ Adapter ──► Postgres
                  │   Domain Logic    │
 CLI ──► Adapter ─┤                   ├─ Adapter ──► Redis
                  │ (no infra imports)│
Test ──► Adapter ─┤                   ├─ Adapter ──► S3
                  └───────────────────┘
                   Ports (interfaces)    Ports (interfaces)
                   ◄── driving side      driven side ──►
```

## Architecture

Look for clean separation between domain logic and infrastructure.

### Review Checklist

- Ports are defined as interfaces/protocols, not concrete classes
- Adapters implement exactly one port — no multi-port adapters
- Domain layer has zero imports from infrastructure packages
- Tests use in-memory adapters, not mocks of concrete classes

### Anti-patterns

- Domain code importing `requests`, `boto3`, or DB drivers directly
- "Port" interfaces that leak infrastructure details (SQL, HTTP headers)
- Adapter logic bleeding into domain services

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
