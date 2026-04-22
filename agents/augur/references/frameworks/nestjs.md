---
kind: framework
name: nestjs
signatures:
  framework: nestjs
  manifest_packages:
    package_json:
    - nestjs
    - '@nestjs/common'
    - '@nestjs/core'
  source_extensions:
  - .ts
  - .tsx
  - .js
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '@Controller\b'
    - '@Get\s*\('
    - '@Post\s*\('
    - '@Put\s*\('
    - '@Delete\s*\('
    - '@Patch\s*\('
    medium:
    - '@Injectable\b'
    - '@Module\b'
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - require\(['"]express['"]\)
source:
  memory_framework: memory/catalog/frameworks/nestjs/framework.md
  semantics: memory/catalog/frameworks/nestjs/semantics.yaml
language: typescript
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

NestJS is an opinionated TypeScript backend framework that uses decorators, modules, and dependency injection to structure services.

## Recognition
Common signals:
- `@Controller`, `@Get`, `@Post`
- `@Injectable` and module metadata
- `@nestjs/common` or `@nestjs/core`
- providers and constructor injection

## Architectural implications
- modules and providers create visible composition boundaries
- dependency injection is framework-native rather than optional
- transport abstractions can hide runtime wiring if the service graph is not explicit

## Common failure modes
- decorators and reflection make control flow hard to trace
- service classes grow into broad orchestration layers
- runtime wiring becomes implicit instead of documented at module boundaries
