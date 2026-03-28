# Concept File Template

Level 3 resource for the remember skill. Defines the expected format for Designer concept files.

Use this template when writing a new concept file for the Designer agent at `agents/designer/memory/concepts/<concept-name>/concept.md` (canonical path).

## Frontmatter

```yaml
---
description: "<Concept Name> — one-line description of what this concept is"
type: pattern | anti-pattern
testable: true | false
curated: true
preloaded: none
graphable: true | false
abstraction: [<abstraction-1>, <abstraction-2>]
---
```

### Recall properties

| Field | Required | Description |
|-------|----------|-------------|
| `description` | yes | Human-readable name + brief description |
| `curated` | yes | Always `true` for concept files |
| `preloaded` | yes | Always `none` (loaded on demand, not preloaded into agent memory) |

### Concept-specific fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | yes | `pattern` for concepts to follow, `anti-pattern` for concepts to avoid |
| `testable` | no | Whether this concept can be validated with automated checks |
| `observable` | no | Whether this concept has monitoring/observability signals |
| `distributed` | no | Whether this concept involves distributed systems |
| `graphable` | yes | `true` if the concept can be meaningfully represented as a diagram |
| `abstraction` | yes | List of abstraction levels this concept belongs to. Valid values: architectural, design, data, integration, messaging, infrastructure, resilience, concurrency, security, api, lifecycle, deployment, observability, testing, frontend, error-handling, realtime, ml, compiler. See `agents/designer/memory/abstractions.md` for descriptions. |

## Body Structure

```markdown
# <Concept Name>

## Recognition

How to identify this concept in code.

### Signatures

- Import/library indicators (e.g., `from kafka import KafkaConsumer`)
- Class/function naming patterns (e.g., `class *Consumer`, `*Repository`)
- Directory structure indicators (e.g., `ports/`, `adapters/`)
- Framework-specific markers (e.g., `@app.route`, `useEffect`)
- Config file indicators

### Confidence

- **high** — clear, unambiguous indicators present
- **medium** — partial implementation or indirect evidence
- **low** — traces of the concept but not formalized

## Architecture

Review guidance for this concept.

### Review Checklist

- Key properties to verify when this concept is detected
- Best practices specific to this concept

### Anti-patterns

- Common mistakes when implementing this concept
- What to flag during review
```

## Notes

- Each concept gets its own directory: `<concept-name>/concept.md`
- The directory may also contain implementation-specific files (e.g., `stoik.md` for stream-to-store, `orchestrator.md` for service-manager)
- Anti-pattern concept files follow the same structure but `type: anti-pattern` and the Architecture section focuses on detection and remediation rather than review
