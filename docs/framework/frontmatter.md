# Frontmatter Reference

Every file in kordinate has YAML frontmatter that describes its recall properties. This page documents all frontmatter fields, which file types use them, and how they interact with the Claude Code runtime.

## Recall Properties

These are kordinate's own properties. They control how knowledge is stored, discovered, loaded, and protected.

| Property | In frontmatter | Values | Default | Purpose |
|----------|:-:|--------|---------|---------|
| **description** | yes | one-line text | required | What this file is. Used for discovery, KORD.md index, and Claude's skill/agent triggering. |
| **curated** | yes | `true` / `false` | `false` | `true` = only updated when explicitly requested. The guard requires scribe auth to write to curated files. |
| **preloaded** | yes | `none` / `all` / `<agent>` | `none` | Who loads this at startup. `all` = main session (survives compaction). `<agent>` = that agent's spawn prompt. |
| **scope** | no | — | — | Determined by path: `~/.kord/` = global, `.kord/` = project. Not a frontmatter field. |
| **template** | no | — | — | Inferred by `generate-kord.sh` from file type and stored in KORD.json. Not a frontmatter field. |
| **owner** | no | — | — | Derived from directory: `agents/<name>/` = that agent. Not a frontmatter field. |
| **expiry** | no | — | — | Expressed as `expiry.sh` files in kord directories. Not a frontmatter field. |

### Derived properties

`path`, `scope`, `template`, `owner`, and `expiry` are never written in frontmatter. They are derived from the file's location and structure, then recorded in KORD.json by `generate-kord.sh`.

## Claude-native Fields

These fields are defined by Claude Code, not kordinate. They appear in agent identity files and skill definitions. Kordinate passes them through to the runtime during linking.

| Field | File type | Purpose |
|-------|-----------|---------|
| `name` | IDENTITY.md, SKILL.md | Identifier. Kebab-case, max 64 chars for skills. |
| `model` | IDENTITY.md | Which Claude model this agent uses. |
| `tools` | IDENTITY.md | Tool access list for this agent. |
| `color` | IDENTITY.md | Terminal color for this agent's output. |
| `memory` | IDENTITY.md | Memory configuration. |
| `argument-hint` | SKILL.md | Syntax hint shown when the skill accepts arguments. |
| `disable-model-invocation` | SKILL.md | `true` prevents Claude from auto-invoking (for destructive skills). |
| `allowed-tools` | SKILL.md | Restricts which tools the skill can use. |
| `context` | SKILL.md | `fork` runs the skill in an isolated context. |
| `user-invocable` | SKILL.md | Whether users can invoke the skill directly. |

During linking, scribe strips kordinate properties (`curated`, `preloaded`) from IDENTITY.md before writing to `~/.claude/agents/`. Claude Code only sees its native fields.

## File Types

### IDENTITY.md

Agent definition. Mixed frontmatter: Claude-native fields + recall properties.

```yaml
---
name: deployer
description: Infrastructure operations — deployments, cluster management
model: claude-opus-4-6
color: blue
tools: [Read, Edit, Write, Bash, Glob]
memory: auto
curated: true
preloaded: deployer
---
```

### SKILL.md

Skill definition. Mostly Claude-native, plus `description` and `curated` from recall.

```yaml
---
name: infra
description: Manage cluster infrastructure and deployments
argument-hint: "<subcommand> [args]"
curated: true
---
```

### Memory files

Agent knowledge. Recall properties only — no Claude-native fields.

**Topic files** (curated knowledge):
```yaml
---
description: Infrastructure reference
curated: true
preloaded: deployer
---
```

**Scratchpads** (working notes):
```yaml
---
description: Deployer working notes and observations
curated: false
preloaded: deployer
---
```

### Contract files

Kord consultation contracts. Recall properties plus kord-specific fields.

```yaml
---
description: General cluster questions
requester: "*"
mode: stateful
skill: infra
curated: true
cache_inputs: [cluster]
---
```

Kord-specific fields:

| Field | Purpose |
|-------|---------|
| `requester` | Who can invoke this kord (`*` = any agent, or a specific agent name) |
| `mode` | `stateful` (cached responses) or `stateless` (fresh each time) |
| `skill` | Which skill handles the consultation |
| `cache_inputs` | For stateful kords: which inputs to key the cache on |

### Concept files

Designer's pattern catalog. Recall properties plus concept-specific fields.

**Pattern file** (`pattern.md`):
```yaml
---
description: Circuit Breaker architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
preloaded: none
graphable: true
abstraction: [resilience, integration]
---
```

**Supplementary file** (`testing.md`, `monitoring.md`, `deployment.md`):
```yaml
---
description: Circuit Breaker — testing guidance
type: supplementary
curated: true
preloaded: none
---
```

Concept-specific fields:

| Field | Values | Purpose |
|-------|--------|---------|
| `type` | `pattern` / `anti-pattern` / `supplementary` | What kind of concept file |
| `testable` | `true` / `false` | Can be validated with automated checks |
| `observable` | `true` / `false` | Has monitoring/observability signals |
| `distributed` | `true` / `false` | Involves distributed systems |
| `graphable` | `true` / `false` | Can be represented as a diagram |
| `abstraction` | list of categories | Which abstraction levels this concept belongs to |

Valid abstraction values: `architectural`, `design`, `data`, `integration`, `messaging`, `infrastructure`, `resilience`, `concurrency`, `security`, `api`, `lifecycle`, `deployment`, `observability`, `testing`, `frontend`, `error-handling`, `realtime`, `ml`, `compiler`.

### Shared protocols

Single files at `shared/<name>.md`. Recall properties only.

```yaml
---
description: Memory write protocol
curated: true
preloaded: all
---
```

## KORD.json

The registry. `generate-kord.sh` reads frontmatter from all files and produces a JSON array where each entry contains:

- `path` — relative to `$KORDINATE_HOME`
- `description` — from frontmatter
- `curated` — from frontmatter (omitted if `false`)
- `preloaded` — from frontmatter (omitted if `none`)

The guard reads KORD.json at runtime to decide whether a write requires scribe auth.
