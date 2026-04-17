---
description: "Plugin host structure \u2014 core system with pluggable extensions via\
  \ defined interfaces"
type: structure-shape
abstraction:
- architectural
- design
status: specialized
scope: cross-cutting
relationships:
  related_to:
  - plugin
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Plugin Host

`plugin-host` is the host-side companion to [plugin](/concepts/plugin).

Use it when the codebase owns the extension surface itself: discovery, lifecycle, compatibility policy, and plugin execution boundaries.

## Recognition

### Signatures

- Plugin interface or abstract base class that extensions implement
- Plugin discovery: scanning directories, entry points, or registries
- Python `entry_points` in `pyproject.toml` or `setup.py`
- VS Code extension API: `vscode.extensions`, `activate()` function
- WordPress hooks: `add_action()`, `add_filter()`
- Webpack plugins implementing `apply(compiler)` interface
- Babel/ESLint plugin config arrays
- Dynamic import/loading of plugin modules at runtime
- Plugin lifecycle: register → initialize → activate → deactivate
- Configuration-driven feature enablement

### Confidence

- **high** — defined plugin interface with discovery mechanism, lifecycle management, and multiple third-party plugins
- **medium** — extension points via interfaces/hooks but plugins are internal, not third-party
- **low** — configurable behavior via strategy pattern or dependency injection but no formal plugin system

### Relationship To Other Concepts

- Related to [plugin](/concepts/plugin) because the host defines the extension points and lifecycle that plugins attach to.

### Boundary

Use `plugin-host` when the important observation is the core system that discovers, loads, and coordinates pluggable extensions.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
