# Augur Repo Label Schema

Defines the compact per-repo benchmark label shape used for scoring.

## Goal

Repo labels exist to explain benchmark results, not to decorate the dataset.

They should make it possible to answer:

- which repo classes need broader preload?
- which repo classes benefit most from Augur?
- which repo classes remain weak?

## Schema

```json
{
  "repo": "owner/name",
  "local_slug": "owner--name",
  "bucket": "production | adversarial | separation | local-pilot",
  "primary_languages": ["Go", "TypeScript"],
  "size_class": "small | medium | large | very-large",
  "topology": [
    "service",
    "monolith",
    "plugin-host",
    "library",
    "worker-system",
    "cli",
    "desktop",
    "mobile",
    "data-platform",
    "polyglot-app"
  ],
  "framework_density": "low | medium | high",
  "state_complexity": "low | medium | high",
  "integration_complexity": "low | medium | high",
  "extensibility": "low | medium | high",
  "ambiguity_risk": "low | medium | high",
  "notes": "Short explanation of why this repo is in the set."
}
```

## Field Guidance

### `bucket`

High-level benchmark grouping:

- `production`
  - real-world repos meant to represent likely customer inputs
- `adversarial`
  - fair but unusually difficult repos
- `separation`
  - repos chosen to separate model or preload behavior
- `local-pilot`
  - curated repos available in the current environment for repeated benchmarking

### `size_class`

Use repo and architecture complexity, not only LOC:

- `small`
- `medium`
- `large`
- `very-large`

### `topology`

Use multiple tags when needed. These tags matter for preload policy.

Examples:

- `service`
- `worker-system`
- `plugin-host`
- `data-platform`
- `polyglot-app`
- `library`
- `cli`

### `framework_density`

How much repo understanding depends on framework-specific reading:

- `low`
  - mostly custom architecture, little framework scaffolding
- `medium`
  - some framework reliance, but not dominant
- `high`
  - framework semantics strongly shape architecture reading

### `state_complexity`

How much the repo depends on careful state modeling:

- number of stores
- config-dependent persistence
- queues, caches, sessions, snapshots
- durable vs ephemeral distinctions

### `integration_complexity`

How many meaningful external boundaries the system owns:

- HTTP clients
- messaging systems
- auth providers
- databases
- storage backends

### `extensibility`

How much the architecture depends on plugins, addons, connectors, modules, or user-defined runtime extensions.

### `ambiguity_risk`

How likely the repo is to require broader preload or deeper semantic reading.

Examples of `high`:

- heavy framework overlap
- plugin-host behavior hidden behind flat layout
- large polyglot monolith
- architecture-relevant names reused in many unrelated places

## Why These Labels Matter

These labels are specifically meant to support bundle/preload decisions.

Examples:

- `framework_density=high` may predict stronger benefit from broader framework preload
- `ambiguity_risk=high` may predict stronger benefit from `holistic`
- `state_complexity=high` may predict stronger benefit from state-oriented seeds and grounding
- `extensibility=high` may predict stronger benefit from broader component/decomposition guidance

## Minimum Label Set

For every benchmark repo, require at least:

- `repo`
- `local_slug`
- `bucket`
- `primary_languages`
- `size_class`
- `topology`
- `framework_density`
- `state_complexity`
- `ambiguity_risk`
- `notes`
