# Codesight Integration Plan

Purpose: adopt the strongest lower-layer ideas from `codesight` without weakening Augur's detector semantics, concept layer, or atlas synthesis.

## Principle

Keep Augur's value centered on:
- semantic concept memory
- anti-pattern reasoning
- failure-mode synthesis
- atlas and downstream agent outputs

Borrow from `codesight` only where it improves the lower layer:
- framework-native extraction breadth
- normalized intermediate artifacts
- detector provenance
- blast radius and hot-file utilities

## Target Pipeline

```text
framework detection -> fact extraction -> concept inference -> atlas -> stories/journeys
```

Questions stay in concept inference, after facts and before concept confirmation.

## Workstreams

### 1. Facts Contract

Status: landed in docs

Artifacts:
- `schemas/facts-schema.md`
- `detectors/facts/schema.md`
- `bundles/detectors/facts/all.json`

### 2. Initial Fact Domains

First-class v1 domains:
- frameworks
- routes
- models
- external-clients
- import-graph

Preferred follow-on domains:
- middleware
- config
- hot-files
- jobs
- events
- auth-surface

### 3. Extractor Design Rules

- AST first where practical
- signature or regex fallback when AST is unavailable or too expensive
- framework-native logic preferred over generic heuristics
- facts must be useful without atlas generation
- concepts must consume fact IDs rather than raw detector hits

### 4. Atlas Integration

Use facts to populate:
- `api_surface`
- `domain_model`
- `state`
- `external_dependencies`
- `module_graph`
- `flows`

Use concept inference over facts to populate:
- `concepts.detected_patterns`
- `concepts.detected_anti_patterns`
- `concepts.gaps`
- resilience-driven `failure_modes`
- debt and recommendations

### 5. Direct Utility Features

Add outputs that do not require full atlas consumption:
- blast radius by file and component
- hot-file ranking
- topic slices: `api`, `data`, `deps`, `failures`, `auth`
- detector coverage reports

## Recommended Implementation Order

1. facts schema and runtime file layout
2. route extractor
3. model/state extractor
4. import graph extractor
5. external client extractor
6. provenance wiring into concept evidence
7. blast radius derivation
8. focused topic artifacts
9. benchmark harness against `codesight`

## Success Criteria

- atlas can be regenerated from facts plus concept inference
- every concept can explain which fact IDs caused it to fire
- detector outputs are debuggable without reading implementation code
- Augur matches or exceeds `codesight` on targeted extraction classes while preserving richer higher-level outputs
