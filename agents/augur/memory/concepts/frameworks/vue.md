---
kind: framework
name: vue
signatures:
  framework: vue
  manifest_packages:
    package_json:
    - vue
  source_extensions:
  - .js
  - .ts
  - .vue
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+['"]vue['"]
    - \bcreateApp\s*\(
    - \bdefineComponent\s*\(
    - <template>
    medium:
    - \bv-model\b
    - \bdefineProps\s*\(
    - \bref\s*\(
    - \bcomputed\s*\(
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
  - form-binding
  - hydration
  related_to:
  - reactive-store
traits:
  ui_surface: true
  component_model_native: true
  template_binding_native: true
  reactive_state_native: true
common_concepts:
- component
- form-binding
common_failure_modes:
- component-sprawl
- shared-reactive-state-coupling
- lifecycle-data-loading-drift
---

# Explanation

Vue is a reactive component framework with template bindings, composition APIs, and progressive hydration options.

## Recognition
Common signals:
- `vue` dependency
- `.vue` single-file components
- `createApp()` or `defineComponent()`
- template directives such as `v-if`, `v-for`, and `v-model`
- Composition API helpers like `ref()`, `computed()`, and `watch()`

## Architectural implications
- component structure and reactive state are usually the main frontend organizing surfaces
- form binding is often framework-native through directives
- hydration is possible, but usually depends on the surrounding stack rather than Vue alone

## Common failure modes
- overgrown component files mixing view logic and orchestration
- reactive state leaking across unrelated features
- ad hoc data loading spread across component lifecycle hooks
