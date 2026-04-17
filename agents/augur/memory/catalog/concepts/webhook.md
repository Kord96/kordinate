---
description: Webhook architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - subscription
  - server-route-registration
  - pub-sub
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Webhook

## Recognition

How to identify this pattern in code.

### Signatures

- Callback URL registration endpoints (`POST /webhooks`, `webhook_url` config field)
- HTTP POST to registered endpoints when events occur
- Webhook payload signing with HMAC (`X-Hub-Signature`, `X-Signature-256` headers)
- Retry with exponential backoff on delivery failure (4xx/5xx responses)
- `webhook_url` or `callback_url` in configuration or database models
- Event delivery queue backing webhook dispatch
- Signature verification on the receiving side (`hmac.compare_digest`)

### Confidence

- **high** -- callback URL registration, signed payloads, and retry logic all present
- **medium** -- HTTP POST on events with callback URLs but no signing or retry mechanism
- **low** -- outbound HTTP calls triggered by events but no formal registration or delivery guarantees

## Architecture

Look for event-driven HTTP callback delivery with authentication and at-least-once guarantees.

### Review Checklist

- Payloads are signed with a shared secret (HMAC-SHA256) and receivers verify the signature
- Failed deliveries are retried with exponential backoff and a maximum retry count
- Webhook endpoints are registered with validation (URL reachability or ownership proof)
- Idempotency keys or event IDs are included so receivers can deduplicate
- A dead-letter mechanism exists for permanently failed deliveries
- Payload size is bounded to prevent abuse

### Anti-patterns

- No payload signing -- receivers cannot verify the sender's identity
- Synchronous webhook dispatch blocking the event producer
- No retry mechanism -- a single network failure permanently drops the event
- Unbounded payload size allowing arbitrarily large deliveries

### Relationship To Other Concepts

- Related to [subscription](/concepts/subscription) when consumers register callback endpoints for specific event types.
- Related to [server-route-registration](/concepts/server-route-registration) because receiving webhooks requires server-side endpoint registration and verification handlers.
- Related to [pub-sub](/concepts/pub-sub) when webhooks are one delivery mechanism for published events.

### Boundary

Use `webhook` when the architecture centers on outbound event delivery over HTTP callbacks with registration, signing, and retry semantics.

Do not use it for ordinary REST APIs, internal HTTP calls, or server-side routes that are not callback-style event delivery endpoints.
