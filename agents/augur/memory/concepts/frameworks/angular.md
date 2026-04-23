---
kind: framework
name: angular
signatures:
  framework: angular
  manifest_packages:
    package_json:
    - '@angular/core'
    - '@angular/common'
    - '@angular/router'
  source_extensions:
  - .ts
  - .js
  path_patterns:
    strong:
    - (^|/)src/app/
    medium: []
    weak: []
  source_patterns:
    strong:
    - '@Component\s*\('
    - '@NgModule\s*\('
    - \bbootstrapApplication\s*\(
    - \bplatformBrowserDynamic\s*\(
    medium:
    - '@Injectable\s*\('
    - \bRouterModule\.forRoot\s*\(
    - \b(FormBuilder|FormGroup|FormControl|ngModel)\b
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: typescript
framework_kind: ui-app
scope: frontend
status: primary
family: frameworks
relationships:
  implements:
  - component
  supports:
  - dependency-injection
  - form-binding
  - route-guard
  - hydration
  related_to:
  - mvvm
traits:
  ui_surface: true
  component_model_native: true
  dependency_injection_native: true
  routing_native: true
  forms_native: true
common_concepts:
- component
- dependency-injection
- form-binding
common_failure_modes:
- service-god-objects
- module-boundary-drift
- workflow-logic-in-components
---

# Explanation

Angular is a TypeScript frontend application framework with dependency injection, components, routing, and structured forms.

## Recognition
Common signals:
- `@angular/core` dependency
- `@Component()` or `@NgModule()` decorators
- `bootstrapApplication()` or `platformBrowserDynamic()`
- `RouterModule` configuration
- `FormGroup`, `FormBuilder`, or `ngModel`

## Architectural implications
- dependency injection is a first-class composition mechanism
- route structure, guards, and forms are usually framework-shaped rather than ad hoc
- UI code often separates component templates, services, and modules more explicitly than lighter frontend libraries

## Common failure modes
- service layers turning into god objects
- module boundaries drifting into a distributed monolith inside one frontend
- business workflow logic buried in components or route guards
