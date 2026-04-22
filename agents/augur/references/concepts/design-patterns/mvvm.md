---
kind: concept
name: mvvm
signatures: {}
source:
  memory_concept: memory/catalog/concepts/mvvm.md
type: pattern
abstraction:
- architectural
- frontend
scope: frontend
status: specialized
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- ViewModel classes exposing observable properties that the view binds to
- Two-way data binding between view and ViewModel (`@observable`, `@computed`, `@Binding`)
- `ViewModel` suffix on classes (`UserViewModel`, `SettingsViewModel`)
- Commands or actions exposed as ViewModel methods, invoked by the view
- Frameworks: WPF/XAML, SwiftUI, Android ViewModel/LiveData, Knockout.js, Vue (Composition API)

### Confidence

- **high** -- ViewModel classes with `@observable`/`@Published` properties and declarative view bindings
- **medium** -- Reactive state objects driving UI updates without direct DOM manipulation, but no formal ViewModel naming
- **low** -- Any pattern where a non-model object mediates between data and view with some reactivity

## Architecture

Look for a ViewModel layer providing observable state that views bind to declaratively.

### Relationship To Other Concepts

- `mvvm` is a UI state/presentation coordination pattern.
- It can coexist with `component` architecture, especially in reactive frontends.
- It often overlaps with `layered` naming but is narrower and presentation-focused.
- Prefer `mvc` instead when explicit controllers mediate input and choose views rather than reactive view-model state driving the UI.

### Review Checklist

- ViewModels contain no view-specific code (no UI imports, no layout logic)
- Data binding is declarative, not manually synchronized in imperative code
- ViewModel state is the single source of truth for the view -- no parallel state in the view layer
- ViewModels are testable in isolation without instantiating views
- Disposal/cleanup of subscriptions when the view is destroyed

### Anti-patterns

- ViewModel directly manipulating DOM elements or UI widgets
- Two-way binding on complex objects causing unintended cascading updates
- ViewModel holding a reference to the view (breaking the decoupling)
- Observable properties with no cleanup, leaking subscriptions on navigation

### Boundary

Use `mvvm` when the important observation is this specific architectural concern within a frontend, UI, or client-side architectural concern.

Do not promote it above a broader parent concept unless the specialization itself is what materially explains the design.
