# Plugin Architecture

```
                    ┌──────────────┐
                    │     Core     │
                    │              │
                    │  ┌────────┐  │
  ┌──────────┐     │  │Registry│  │     ┌──────────┐
  │ Plugin A ├────►│  │        │  │◄────┤ Plugin C │
  └──────────┘     │  │ load() │  │     └──────────┘
                    │  │ get()  │  │
  ┌──────────┐     │  └────────┘  │
  │ Plugin B ├────►│              │
  └──────────┘     │  Plugin API  │
                    │ (interface)  │
                    └──────────────┘
```

## Architecture

Look for a stable plugin interface with discovery/registration and no core modifications needed.

### Review Checklist

- Plugin interface is well-defined and versioned — plugins depend on it, not on core internals
- Registration happens at startup via a registry — no hardcoded plugin lists
- Core functions without any plugins loaded (graceful degradation)
- Plugin lifecycle is managed (init, start, stop) — no orphaned resources

### Anti-patterns

- Plugins importing core internals beyond the published API surface
- No versioning on the plugin interface — core changes break all plugins silently
- Plugin registration order creates hidden dependencies between plugins

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
