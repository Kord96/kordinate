---
kind: concept
name: plugin
signatures: {}
source:
  memory_concept: memory/catalog/concepts/plugin.md
type: pattern
abstraction:
- design
scope: cross-cutting
status: primary
---

# Explanation

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

### Confidence

- **high** -- `PluginManager` with `register_plugin()`/`load_plugins()`, or `pluggy` hook specs with entry points configuration
- **medium** -- Plugin directory scanning at startup with a plugin registry, but without a formal plugin interface
- **low** -- Dynamic module loading or extension directories without explicit registration or lifecycle management

## Architecture

Look for a stable plugin interface with discovery/registration and no core modifications needed.

### Relationship To Other Concepts

- `plugin` describes the extension implementation side.
- `plugin-host` describes the core system that discovers, loads, and governs those plugins.
- Keep both when the codebase clearly contains both roles.

### Review Checklist

- Plugin interface is well-defined and versioned — plugins depend on it, not on core internals
- Registration happens at startup via a registry — no hardcoded plugin lists
- Core functions without any plugins loaded (graceful degradation)
- Plugin lifecycle is managed (init, start, stop) — no orphaned resources

### Anti-patterns

- Plugins importing core internals beyond the published API surface
- No versioning on the plugin interface — core changes break all plugins silently
- Plugin registration order creates hidden dependencies between plugins

### Boundary

Use `plugin` when optional extensions implement a published interface and are loaded into a host system without changing the host’s core code.

Do not use it for ordinary dependency injection or strategy selection unless the extensions are truly pluggable units with an explicit host contract.
