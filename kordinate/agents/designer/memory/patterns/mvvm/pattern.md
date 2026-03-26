---
description: Model-View-ViewModel architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Model-View-ViewModel

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
