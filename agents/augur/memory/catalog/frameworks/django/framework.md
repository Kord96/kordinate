---
description: Batteries-included Python web framework with ORM, routing, templating, and admin features
---
# Django

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
