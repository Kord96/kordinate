---
kind: framework
name: django
signatures:
  framework: django
  manifest_packages:
    pyproject:
    - django
    requirements:
    - django
  source_extensions:
  - .py
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+django\.urls\s+import
    - urlpatterns\s*=
    medium:
    - from\s+django\s+import
    - django\.setup\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - from\s+flask\s+import
language: python
framework_kind: full-stack
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - input-validation
  uses:
  - server-route-registration
  related_to:
  - layered
traits:
  api_surface: true
  orm_native: true
  validation_native: true
  admin_surface: true
common_concepts:
- active-record
common_failure_modes:
- fat-models
- implicit-coupling-through-settings
- leaking-orm-models
---

# Explanation

Django is a batteries-included Python web framework that combines routing, ORM models, forms, admin tooling, and request middleware into one stack.

## Recognition
Common signals:
- `urlpatterns = [...]`
- `from django.urls import path`
- `models.Model`, form classes, and settings-driven app configuration
- Django management commands and admin registration

## Architectural implications
- the framework provides many default building blocks, so architectural boundaries can either be clear or heavily framework-shaped
- model, form, and serializer layers often become the practical architecture seams
- request lifecycle behavior is strongly affected by middleware and settings

## Common failure modes
- fat models or views swallowing too much business logic
- ORM entities leaking directly into API contracts
- implicit coupling through settings, signals, and global app state
