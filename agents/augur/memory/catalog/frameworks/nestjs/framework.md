---
description: Opinionated TypeScript backend framework with decorators, modules, and dependency injection
---
# NestJS

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
