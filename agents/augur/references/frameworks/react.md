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
source:
  memory_framework: memory/catalog/frameworks/react/framework.md
  semantics: memory/catalog/frameworks/react/semantics.yaml
language: typescript
framework_kind: library
scope: frontend
status: supporting
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
