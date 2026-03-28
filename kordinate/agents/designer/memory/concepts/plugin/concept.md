---
description: Plugin architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Plugin Architecture

## Recognition

How to identify this pattern in code.

### Signatures

- Plugin registry classes or dictionaries mapping plugin names to implementations
- Dynamic registration at startup via discovery or scanning
- `register_plugin()` / `load_plugins()` functions managing plugin lifecycle
- Python `setup.cfg` or `pyproject.toml` `entry_points` defining plugin hooks
- `pluggy` hook specifications and implementations (`@hookimpl`, `@hookspec`)
- Plugin directories scanned at startup for auto-discovery (`plugins/`, `extensions/`)
- `PluginManager` class coordinating plugin registration, initialization, and teardown
- Plugin interface or base class that all plugins must implement
- Framework `use_*()` methods that register services and add middleware to extend core functionality (e.g., `app.use_cors()`, `app.use_authentication()`, `app.use_openapi()`) -- each call plugs a capability into the application without modifying core code
- TypeScript: `app.use()` or `assistant()` methods that register extension objects adding entire behavioral modules (e.g., Slack `App.assistant()` plugging conversational AI into the app)
- Config-driven plugin loading: `config.plugins` array of paths scanned at startup, loading initializers/actions from each plugin directory

### Confidence

- **high** -- `PluginManager` with `register_plugin()`/`load_plugins()`, or `pluggy` hook specs with entry points configuration
- **medium** -- Plugin directory scanning at startup with a plugin registry, but without a formal plugin interface
- **low** -- Dynamic module loading or extension directories without explicit registration or lifecycle management

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
