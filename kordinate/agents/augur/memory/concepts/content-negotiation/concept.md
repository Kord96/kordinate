---
description: Content/Protocol Negotiation architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [api]
---
# Content/Protocol Negotiation

## Recognition

How to identify this pattern in code.

### Signatures

- `Accept` and `Content-Type` HTTP headers used for format selection
- `produces` and `consumes` annotations on API endpoints (JAX-RS, Spring)
- Format selection logic dispatching between JSON, XML, protobuf, or other serializations
- API versioning via `Accept-Version`, `Accept: application/vnd.api.v2+json`, or URL path segments
- Media type routing: `application/json`, `application/xml`, `application/protobuf`
- `406 Not Acceptable` or `415 Unsupported Media Type` error responses
- Content negotiation middleware or request interceptors
- `Vary: Accept` response header for cache correctness

### Negative signals (not sufficient for detection)

- Simply referencing `MediaType.APPLICATION_JSON` or `application/json` in API responses is standard REST formatting, not content negotiation
- A single-format API that sets `Content-Type: application/json` on all responses does not perform negotiation
- Import of `MediaType` class alone without multi-format dispatch or Accept header handling is not negotiation
- TypeScript/Python: Setting `Content-Type` headers in HTTP responses or checking `Content-Type` in request parsing is standard HTTP handling, not content negotiation. Content negotiation requires the server to choose between multiple response formats based on the client's `Accept` header
- Parsing different request content types (JSON body vs form body) is input parsing, not content negotiation unless the response format also varies

### Confidence

- **high** -- Explicit `Accept`/`Content-Type` handling with multiple format serializers and `406`/`415` responses
- **medium** -- API version headers or vendor media types with format-specific serialization
- **low** -- Single format API that sets `Content-Type` without any negotiation logic

## Architecture

Look for correct format dispatch based on client preferences with proper error responses for unsupported types.

### Review Checklist

- All supported media types are explicitly declared, not inferred
- Unsupported `Accept` types return `406 Not Acceptable` with a list of supported types
- Unsupported `Content-Type` on requests returns `415 Unsupported Media Type`
- `Vary: Accept` header is set on responses to prevent cache poisoning
- Default format is defined for requests without an `Accept` header
- API versioning strategy is consistent (header-based, URL-based, or media type -- not mixed)

### Anti-patterns

- Silently ignoring the `Accept` header and always returning JSON
- Missing `Vary` header causing CDN or proxy caches to serve wrong formats
- Mixing version negotiation strategies across endpoints (some URL-based, some header-based)
- Supporting content types that are never tested or documented
