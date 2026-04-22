# Framework Detection Reference

Supporting legacy view only.

- Use this file for cross-language recognition ideas and fallback heuristics.
- Do not treat this file as the canonical detector or reference contract.
- Canonical framework references now live under `../../../references/frameworks/`.
- Detector policy or executable rules, when present, live under `../../../detectors/frameworks/<name>/`.
- The generated ontology view lives in `../../indexes/ontology-graph.json` and `../../indexes/ontology-graph.md`.

## Python

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Flask | `from flask import`, `Flask(__name__)` | `@app.route`, `@blueprint.route` |
| FastAPI | `from fastapi import`, `FastAPI()` | `@app.get/post/put/delete/patch`, `@router.get/post/...` |
| Django | `urlpatterns`, `django.urls` | `path(`, `re_path(`, `url(` |
| Starlette | `from starlette`, `Starlette(` | `Route(`, `Mount(` |
| aiohttp | `from aiohttp import web`, `web.Application()` | `web.get(`, `web.post(`, `router.add_route(` |

## JavaScript / TypeScript

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| React | `react` / `react-dom` deps, `createRoot`, `hydrateRoot` | Component tree composition; no native route surface by itself |
| Vue | `vue` dep, `.vue` files, `createApp`, `defineComponent` | Component tree composition; route surfaces depend on surrounding stack |
| Angular | `@angular/core`, `@Component`, `RouterModule` | Component tree and router configuration; route guards are common |
| Express | `require('express')`, `import express` | `app.get/post/put/delete(`, `router.get/post/...` |
| Koa | `require('koa')`, `import Koa` | `router.get/post(` (via `@koa/router` or `koa-router`) |
| Fastify | `require('fastify')`, `import fastify` | `fastify.get/post(`, `fastify.route({` |
| Hono | `import { Hono }` | `app.get/post(`, `app.route(` |
| Elysia | `import { Elysia }` | `app.get/post(`, `app.group(` |
| NestJS | `@Controller`, `@nestjs/common` | `@Get()`, `@Post()`, `@Put()` |
| Next.js API | `app/api/` or `pages/api/` directory | File-based routing; export `GET`, `POST` functions |
| SvelteKit API | `src/routes/` with `+server.ts`/`+server.js` | File-based routing; export `GET`, `POST` functions |

## Go

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| net/http | `net/http`, `http.HandleFunc`, `http.ListenAndServe` | `http.HandleFunc(`, `mux.Handle(` |
| Gin | `gin.Default()`, `gin.New()` | `router.GET/POST/PUT/DELETE(` |
| Chi | `chi.NewRouter()` | `r.Get/Post/Put/Delete(` |
| Echo | `echo.New()` | `e.GET/POST(`, `e.Group(` |
| Fiber | `fiber.New()`, `gofiber/fiber` | `app.Get/Post(`, `app.Group(` |

## Elixir

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Phoenix | `mix.exs` with `phoenix`, `use MyAppWeb, :router` | `get "/", PageController`, `resources "/users"`, `pipe_through`, `scope "/"` |

## Ruby

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Rails | `routes.rb`, `Gemfile` with `rails` | `resources :`, `get '/'`, `post '/'`, `namespace :` |
| Sinatra | `require 'sinatra'` | `get '/' do`, `post '/' do` |
| Grape | `require 'grape'`, `Grape::API` | `get :endpoint do`, `post :endpoint do`, `resource :name` |

## Java / Kotlin

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Spring Boot | `@RestController`, `@SpringBootApplication` | `@GetMapping`, `@PostMapping`, `@RequestMapping` |
| Quarkus | `@Path`, `quarkus` in `pom.xml` | `@GET`, `@POST`, `@PUT` (JAX-RS) |
| Ktor | `io.ktor`, `embeddedServer` | `routing { get("/") }`, `route("/") { post { } }` |

## C# / .NET

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| ASP.NET Minimal | `WebApplication.CreateBuilder`, `*.csproj` with `Microsoft.AspNetCore` | `app.MapGet(`, `app.MapPost(`, `app.MapPut(` |
| ASP.NET Controllers | `[ApiController]`, `ControllerBase` | `[HttpGet]`, `[HttpPost]`, `[Route("api/[controller]")]` |

## PHP

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Laravel | `composer.json` with `laravel/framework`, `routes/web.php` or `routes/api.php` | `Route::get(`, `Route::post(`, `Route::resource(`, `Route::apiResource(` |
| Symfony | `composer.json` with `symfony/framework-bundle` | `#[Route('/')]`, `@Route` annotation, `config/routes.yaml` |
| Slim | `composer.json` with `slim/slim` | `$app->get(`, `$app->post(`, `$app->group(` |

## Rust

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Actix-web | `actix_web` in `Cargo.toml` | `web::get()`, `web::resource(`, `#[get("/")]` |
| Axum | `axum` in `Cargo.toml` | `Router::new().route(`, `.get(handler)` |

## Swift

| Framework | Import / Config Signals | Route Patterns |
|-----------|------------------------|----------------|
| Vapor | `Package.swift` with `vapor/vapor` | `app.get(`, `app.post(`, `app.grouped(` |

## Fallback Detection

If none of the above match:

1. Check dependency manifests: `package.json`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `*.csproj`, `composer.json`, `Package.swift`
2. Look for generic signals: HTTP method names (`GET`, `POST`) near path string literals, handler registrations, listen/serve calls
3. Check for code-generation approaches: OpenAPI specs (`openapi.yaml`, `swagger.json`), gRPC proto files (`.proto`), GraphQL schemas (`.graphql`)

Report what you found (e.g., "detected X dependency but no recognized routing pattern") and proceed with a best-effort scan. Note the limitation in the final report.

## Non-REST API Detection

| Style | File / Import Signals | Endpoint Signals |
|-------|----------------------|-----------------|
| GraphQL | `.graphql` / `.gql` schema files, `graphql` / `apollo-server` / `@nestjs/graphql` / `ariadne` / `strawberry` / `gqlgen` / `graphql-yoga` / `pothos` in deps | `type Query {`, `type Mutation {`, `type Subscription {`, resolver registrations, `@Query()` / `@Mutation()` decorators |
| gRPC | `.proto` files, `grpc` / `grpcio` / `@grpc/grpc-js` / `google.golang.org/grpc` / `tonic` (Rust) in deps | `service Name { rpc Method(` in proto; generated `*Server` interfaces or `*Handler` stubs |
| WebSocket | `ws` / `socket.io` / `websockets` / `gorilla/websocket` / `coder/websocket` (formerly `nhooyr.io/websocket`) / `@nestjs/websockets` in deps | `@app.websocket(`, `io.on('connection'`, `ws.on('message'`, `Upgrade: websocket` handling |
| SSE | `text/event-stream` content type, `EventSource`, `sse` helper libraries (`better-sse`, `django-eventstream`, `sse-starlette`) | Streaming response with `event:` / `data:` format, `StreamingResponse`, `EventSourceResponse` |

When detected alongside a REST framework, treat each as a separate API surface.

## Multiple Frameworks

If multiple frameworks are detected (e.g., a Flask admin alongside a FastAPI main API, or a monorepo with services in different languages): treat each as a separate API surface. Run all review steps for each independently and note the split in the report header.
