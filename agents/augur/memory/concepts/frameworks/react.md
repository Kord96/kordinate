---
kind: framework
name: react
signatures:
  framework: react
  manifest_packages:
    package_json:
    - react
    - react-dom
  source_extensions:
  - .js
  - .jsx
  - .ts
  - .tsx
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+['"]react['"]
    - require\(['"]react['"]\)
    - from\s+['"]react-dom/client['"]
    - \b(createRoot|hydrateRoot)\s*\(
    medium:
    - \buse(State|Effect|Reducer|Memo|Ref|Context|DeferredValue|Transition)\s*\(
    - \bReact\.(useState|useEffect|useReducer|createElement)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: typescript
framework_kind: library
scope: frontend
status: supporting
family: frameworks
relationships:
  implements:
  - component
  supports:
  - hydration
  - suspense-boundary
  - error-boundary
  - form-binding
  related_to:
  - prop-drilling
  - reactive-store
traits:
  ui_surface: true
  component_model_native: true
  client_hydration_native: true
  suspense_native: true
common_concepts:
- component
common_failure_modes:
- prop-drilling
- state-scatter
- data-fetching-in-components
---

# Explanation

React is a component-oriented UI library for declarative rendering, client hydration, and async boundary composition.

## Recognition
Common signals:
- `react` or `react-dom` dependency
- JSX or TSX component files
- imports from `react` or `react-dom/client`
- hooks such as `useState`, `useEffect`, or `useReducer`
- `createRoot()` or `hydrateRoot()` bootstrap code

## Architectural implications
- component trees are the dominant unit of UI composition
- server rendering and hydration may be present, but only when the surrounding stack enables it
- async loading and failure handling often appear through suspense and error boundary patterns

## Common failure modes
- prop drilling across deep trees
- state scattered across ad hoc hooks without clear ownership
- data fetching leaking into presentation components
