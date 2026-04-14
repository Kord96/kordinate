---
description: Plugin host structure — core system with pluggable extensions via defined interfaces
type: structure-shape
abstraction: [architectural, design]
status: specialized
scope: cross-cutting
relationships:
  related_to: [plugin]
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
