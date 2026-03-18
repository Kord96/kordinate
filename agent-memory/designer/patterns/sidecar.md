# Sidecar — Design Perspective

```
  ┌───────────────────────────────────────┐
  │              Pod / Host               │
  │                                       │
  │  ┌───────────────┐ ┌──────────────┐  │
  │  │  Main         │ │   Sidecar    │  │
  │  │  Container    │ │              │  │
  │  │               │ │ • log ship   │  │
  │  │  app logic    │ │ • proxy      │  │
  │  │               │ │ • auth       │  │
  │  │               │ │ • metrics    │  │
  │  └───────┬───────┘ └──────┬───────┘  │
  │          │   shared       │          │
  │          └── network ─────┘          │
  │          └── volume ──────┘          │
  └───────────────────────────────────────┘
```

Look for the sidecar handling only cross-cutting concerns with no business logic.

## Review Checklist

- Sidecar handles a single cross-cutting concern (logging, proxy, auth — not all three)
- Communication with main container uses localhost/shared volume — no network hops
- Sidecar lifecycle is tied to the main container (starts before, stops after)
- Main container functions (possibly degraded) if the sidecar is temporarily unavailable

## Anti-patterns

- Business logic in the sidecar — it should be infrastructure only
- Sidecar and main container with mismatched lifecycle (sidecar outlives the app)
- Too many sidecars per pod — resource overhead exceeds the benefit
- Tight version coupling between sidecar and main container deployments
