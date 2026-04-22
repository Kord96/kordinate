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
source:
  memory_framework: memory/catalog/frameworks/django/framework.md
  semantics: memory/catalog/frameworks/django/semantics.yaml
language: python
framework_kind: full-stack
scope: backend
status: primary
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
