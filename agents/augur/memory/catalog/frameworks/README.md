# Framework catalog

Framework entries describe runtime ecosystems and framework-native primitives.
Keep this catalog concrete. A framework is a named implementation surface, not a generic architecture idea.

They are separate from architectural concepts:
- frameworks answer **what stack/primitives are present**
- concepts answer **what architectural patterns and shapes are present**

Each framework should live in its own directory:

```text
frameworks/<name>/
  framework.md       # canonical narrative: primitives, conventions, failure modes
  semantics.yaml     # structured semantic metadata
```

## `semantics.yaml`

```yaml
name: fastapi
kind: framework
language: python
summary: Async Python API framework with typed routing and validation
status: primary | specialized | supporting | compatibility
scope: backend | frontend | cross-cutting | platform
relationships:
  implements: [pattern-or-contract]
  supports: [capability-or-pattern]
  uses: [dependency-or-surface]
  related_to: [peer-concept]
traits:
  api_surface: true
common_concepts:
  - rest
common_failure_modes:
  - business-logic-in-routes
```

Detector policy and executable rules for frameworks live under `../../../detectors/facts/frameworks/`.

## Split Of Responsibilities

- `framework.md`
  Human-readable semantic contract for what the framework exposes architecturally.
- `semantics.yaml`
  Machine-friendly ontology and detection summary for traits, framework-authored concept edges, and common failure modes.
- `detectors/facts/frameworks/<name>/`
  Deterministic detection assets for proving the framework is present.

## Precedence

- Concept-to-concept ontology edges must be authored only in concept frontmatter.
- Framework semantics may author only framework-origin edges to concepts.
- `relationships` is the authoritative framework ontology surface.
- `common_concepts` is a low-confidence inferred-association hint. Prefer authored `relationships` whenever you can say something more precise.
- If a framework authors an edge to a concept, inferred hints for the same source-target pair should be treated as maintenance-only signal.

## Relationship Semantics

- `implements`
  Framework -> pattern or contract the framework directly realizes.
- `supports`
  Framework -> capability or pattern the framework natively enables.
- `uses`
  Framework -> concrete dependency surface or runtime mechanism it relies on.
- `related_to`
  Framework -> concept with a meaningful association but no stronger relationship. Use sparingly.

## Authoring Guidance

- Prefer `implements`, `supports`, or `uses` over `related_to`.
- Keep `common_concepts` small. Use it only for genuinely weak or broad co-occurrence hints that are not precise enough for `relationships`.
- Do not encode concept-to-concept hierarchy here.
- Keep `framework.md` explanatory and concrete; keep `semantics.yaml` short and structured.
- When in doubt, fewer explicit edges with better semantics are better than many loose associations.
