---
description: Reactive component framework with template bindings, composition APIs, and progressive hydration options
---
# Vue

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
