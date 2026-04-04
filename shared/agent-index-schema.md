---
description: Schema and semantics for per-agent INDEX.yaml manifests that drive deterministic static bundle generation
---

# Agent INDEX schema

Each agent can define `INDEX.yaml` at the root of its agent directory.

Purpose:
- describe the static content hierarchy for the agent
- define what belongs in the generated static bundle (for example `AUGUR.md`)
- separate static preload content from mutable runtime state
- avoid runtime discovery of preload files

## Frontmatter fields

```yaml
schema: agent-index/v1
agent: <agent-name>
description: <one-line description>
usage:
  preload: included in generated <AGENT>.md and intended to be cache-friendly static context
  ondemand: not included in the generated bundle; read only when needed
  runtime: mutable or generated at runtime; never compiled into the static bundle
```

## Entry fields

Each entry can be a file, directory, generated artifact, or runtime-only path.

```yaml
path: <relative path>
kind: file | dir | generated | runtime
purpose: <short explanation>
preload: preload | ondemand | runtime
include: true | false
mutable: true | false
source_of_truth: repo | generated | runtime
children: []
```

### Field semantics

- `path` — path relative to the agent root
- `kind` — structural type
- `purpose` — why the file/dir exists and when it matters
- `preload`
  - `preload` = compile into generated static bundle
  - `ondemand` = available in repo/runtime but not preloaded
  - `runtime` = dynamic state only
- `include` — whether the entry itself is included in generated `<AGENT>.md`
- `mutable` — whether runtime is allowed to modify it
- `source_of_truth`
  - `repo` = authoritative file in git
  - `generated` = derived artifact
  - `runtime` = runtime-only state
- `children` — nested entries for directories

## Rules

- Secrets must never appear in `INDEX.yaml`
- Public routing metadata must not live in `INDEX.yaml`
- `INDEX.yaml` is for static agent content and bundle generation only
- `preload` should only be used for stable, high-value context
- Large volatile outputs (project memory, analysis outputs, logs) should be marked `runtime`

## Generation target

A generator consumes `INDEX.yaml` and produces a deterministic static bundle named `AGENT.md`.

That bundle should be referenced by the runtime `CLAUDE.md` shim using `@AGENT.md`.

Mutable runtime files and project memory stay outside the generated bundle.
